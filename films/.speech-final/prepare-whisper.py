"""Prepare the approved official multilingual model; verify before reuse."""
import hashlib, json, os, pathlib, ssl, urllib.request, urllib.parse

REVISION = '536b0662742c02347bc0e980a01041f333bce120'
REPO = 'Systran/faster-whisper-small'
ROOT = pathlib.Path('/workspace/models/whisper-small')
HERE = pathlib.Path(__file__).resolve().parent
FILES = ['config.json', 'model.bin', 'tokenizer.json', 'vocabulary.txt']
HOSTS = {'huggingface.co', 'us.aws.cdn.hf.co'}
redirects = []

class VerifiedRedirect(urllib.request.HTTPRedirectHandler):
    def redirect_request(self, req, fp, code, msg, headers, newurl):
        u = urllib.parse.urlsplit(newurl)
        if u.scheme != 'https' or u.hostname not in HOSTS or u.port not in (None, 443):
            raise RuntimeError('Unapproved redirect host: ' + str(u.hostname))
        redirects.append({'status': code, 'host': u.hostname})
        return super().redirect_request(req, fp, code, msg, headers, newurl)

def digest(path, algorithm='sha256'):
    h = hashlib.new(algorithm)
    if algorithm == 'sha1':
        h.update(b'blob ' + str(path.stat().st_size).encode() + b'\0')
    with path.open('rb') as f:
        for chunk in iter(lambda: f.read(1024*1024), b''):
            h.update(chunk)
    return h.hexdigest()

def verify_file(path, entry):
    if path.stat().st_size != entry['size']:
        raise ValueError('Incorrect size: ' + path.name)
    if entry.get('lfs'):
        if digest(path) != entry['lfs']['sha256']:
            raise ValueError('SHA256 mismatch: ' + path.name)
    elif digest(path, 'sha1') != entry['blobId']:
        raise ValueError('Git blob mismatch: ' + path.name)

def main():
    metadata = json.loads((HERE/'model-metadata.json').read_text())
    if metadata['sha'] != REVISION or metadata['id'] != REPO:
        raise ValueError('Metadata repository or revision mismatch')
    entries = {x['rfilename']: x for x in metadata['siblings']}
    ROOT.mkdir(parents=True, exist_ok=True)
    opener = urllib.request.build_opener(VerifiedRedirect, urllib.request.HTTPSHandler(context=ssl.create_default_context()))
    hashes = {}
    for name in FILES:
        dest = ROOT/name
        if not dest.exists():
            url = f'https://huggingface.co/{REPO}/resolve/{REVISION}/{name}'
            temp = ROOT/(name+'.part')
            with opener.open(url, timeout=60) as response, temp.open('wb') as f:
                while chunk := response.read(1024*1024):
                    f.write(chunk)
            verify_file(temp, entries[name])
            os.replace(temp, dest)
        verify_file(dest, entries[name])
        hashes[name] = digest(dest)
        print('Verified', name, dest.stat().st_size, flush=True)
    (ROOT/'verified-manifest.json').write_text(json.dumps({'repo':REPO,'revision':REVISION,'sha256':hashes},indent=2))
    (HERE/'download-redirects.json').write_text(json.dumps(redirects,indent=2))

if __name__ == '__main__':
    main()
