"""Official-source model preparation. Download only after network approval.
Usage: python whisper-model.py verify|download /workspace/models/whisper-small
"""
import hashlib,json,pathlib,sys
REPO='Systran/faster-whisper-small'
FILES=['config.json','preprocessor_config.json','model.bin','tokenizer.json','vocabulary.json','vocabulary.txt']
def sha(p):
 h=hashlib.sha256()
 with p.open('rb') as f:
  for b in iter(lambda:f.read(1024*1024),b''):h.update(b)
 return h.hexdigest()
def verify(root):
 m=json.loads((root/'verified-manifest.json').read_text())
 assert m['repo']==REPO
 for n,h in m['sha256'].items():assert sha(root/n)==h,n
 for n in ['model.bin','config.json','tokenizer.json']:assert n in m['sha256'],n
 print('Local integrity verified:',m['revision'])
if __name__=='__main__':
 mode,folder=sys.argv[1:]; root=pathlib.Path(folder)
 if mode=='verify':verify(root)
 elif mode=='download':
  if (root/'verified-manifest.json').exists():verify(root);sys.exit(0)
  from huggingface_hub import HfApi,snapshot_download
  info=HfApi().model_info(REPO,files_metadata=True)
  snapshot_download(REPO,revision=info.sha,local_dir=str(root),allow_patterns=FILES)
  hashes={}
  for f in info.siblings:
   if f.rfilename not in FILES:continue
   p=root/f.rfilename; digest=sha(p)
   lfs=getattr(f,'lfs',None)
   if lfs:
    expected=lfs.get('sha256') if isinstance(lfs,dict) else lfs.sha256
    assert digest==expected,f.rfilename
   else:
    data=p.read_bytes()
    assert hashlib.sha1(b'blob '+str(len(data)).encode()+b'\0'+data).hexdigest()==f.blob_id,f.rfilename
   hashes[f.rfilename]=digest
  assert all(f in hashes for f in ['model.bin','config.json','tokenizer.json'])
  (root/'verified-manifest.json').write_text(json.dumps({'repo':REPO,'revision':info.sha,'sha256':hashes},indent=2))
  verify(root)
 else:raise SystemExit('Use verify or download')
