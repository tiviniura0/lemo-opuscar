"""Read-only verification of the original V2 payload. No downloads or writes."""
from pathlib import Path
import hashlib,json,sys
root=Path(__file__).resolve().parents[1]
manifest=json.loads((root/'backup-v2/source-manifest.json').read_text())
errors=[]
for name,expected in manifest['files'].items():
 p=root/name
 if not p.is_file():errors.append(name+': missing');continue
 if p.stat().st_size!=expected['bytes'] or hashlib.sha256(p.read_bytes()).hexdigest()!=expected['sha256']:errors.append(name+': content mismatch')
print(json.dumps({'checked':len(manifest['files']),'errors':errors},indent=2))
sys.exit(bool(errors))
