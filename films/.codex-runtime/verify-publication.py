"""Verify retained publication files locally. No network, installs or elevation."""
import hashlib
import json
from pathlib import Path
import sys

manifest = Path(__file__).with_name('publication-manifest.json')
data = json.loads(manifest.read_text())
errors = []
for item in data['files']:
    path = Path(item['path'])
    try:
        h = hashlib.sha256()
        with path.open('rb') as f:
            for block in iter(lambda: f.read(1024*1024), b''):
                h.update(block)
        if path.stat().st_size != item['bytes'] or h.hexdigest() != item['sha256']:
            errors.append({'path': str(path), 'error': 'size or SHA256 changed'})
    except OSError as exc:
        errors.append({'path': str(path), 'error': type(exc).__name__})
for item in data['required_paths']:
    path = Path(item['path'])
    if not path.exists():
        errors.append({'path': str(path), 'error': 'missing path or unresolved symlink'})
print(json.dumps({'files_checked': len(data['files']), 'errors': errors, 'ok': not errors}, indent=2))
sys.exit(1 if errors else 0)
