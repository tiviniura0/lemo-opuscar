"""Read-only, offline readiness check. Never requests elevated permissions.
Exit 0: local prerequisites pass; 20: sockets need an approved execution context;
1: files, models, dependency imports or source definitions fail.
"""
import hashlib
import importlib.metadata
import json
import os
from pathlib import Path
import runpy
import socket
import subprocess
import sys

ROOT = Path(__file__).resolve().parents[2]
os.chdir(ROOT)
result = {'root': str(ROOT), 'errors': [], 'socket_errors': [], 'network_policy_verified': False}
result['network_note'] = 'Agent must verify current restricted/enforced policy with environment_status; startup files do not prove enforcement.'
result['environment_presence'] = {k: bool(os.environ.get(k)) for k in ['HTTPS_PROXY', 'WSS_PROXY', 'NO_PROXY', 'SSL_CERT_FILE']}
try:
    release = runpy.run_path(str(ROOT/'tools/release.py'))
    slugs = release['style_slugs']()
    issues = []
    release['style_format'](slugs, issues)
    catalog = {x['slug'] for x in json.loads((ROOT/'styleboard/catalog.json').read_text())}
    for slug in slugs:
        if slug not in catalog:
            issues.append(slug + ': absent from catalog')
    if len(slugs) != 66:
        issues.append('Expected 66 source style definitions')
    result['styles_source_only'] = {'count': len(slugs), 'issues': issues, 'method': 'official style_slugs + style_format, catalog membership; no release videos required'}
    result['errors'].extend(issues)
    baseline = json.loads((ROOT/'films/.installation-audit/baseline.json').read_text())
    tracked = subprocess.check_output(['git', 'ls-files', '-z'], timeout=10).decode().strip('\0').split('\0')
    changed = [f for f, h in baseline.items() if not (ROOT/f).is_file() or hashlib.sha256((ROOT/f).read_bytes()).hexdigest() != h]
    result['tracked_integrity'] = {'count': len(tracked), 'changed_since_audit': changed, 'same_file_set': set(tracked) == set(baseline)}
    if changed or set(tracked) != set(baseline):
        result['errors'].append('Tracked sources differ from prepared audit; inspect, never reset automatically')
    result['git_status'] = subprocess.check_output(['git', 'status', '--porcelain'], timeout=10).decode()
    versions = {p: importlib.metadata.version(p) for p in ['faster-whisper', 'ctranslate2', 'kokoro-onnx', 'onnxruntime', 'edge-tts', 'aiohttp']}
    result['python_versions'] = versions
    verify = subprocess.run([sys.executable, '-B', 'films/.speech-final/verify-whisper.py'], capture_output=True, text=True, timeout=30)
    result['whisper_integrity_ok'] = verify.returncode == 0
    if verify.returncode:
        result['errors'].append('Whisper local verification failed')
    for name, expected in {
        'core/tts/kokoro-v1.0.onnx': '7d5df8ecf7d4b1878015a32686053fd0eebe2bc377234608764cc0ef3636a6c5',
        'core/tts/voices-v1.0.bin': 'bca610b8308e8d99f32e6fe4197e7ec01679264efed0cac9140fe9c29f1fbf7d',
    }.items():
        if hashlib.sha256((ROOT/name).read_bytes()).hexdigest() != expected:
            result['errors'].append('Kokoro integrity mismatch: ' + name)
    for name in ['films/.speech-final/edge-with-platform-ca.py', 'films/.speech-final/offline-python.py', 'node_modules/playwright-core/package.json', 'node_modules/three/package.json']:
        if not (ROOT/name).is_file():
            result['errors'].append('Missing runtime file: ' + name)
    result['chromium_version'] = subprocess.check_output(['/usr/bin/chromium', '--version'], timeout=5, text=True).strip()
    if 'Chromium 155.' not in result['chromium_version']:
        result['errors'].append('Chromium version differs from validated 155')
except Exception as exc:
    result['errors'].append(type(exc).__name__ + ': ' + str(exc)[:180])

for name, family in [('tcp_ipv4', socket.AF_INET), ('unix_passcred', socket.AF_UNIX)]:
    try:
        with socket.socket(family, socket.SOCK_STREAM) as s:
            s.settimeout(1)
            if family == socket.AF_INET:
                s.bind(('127.0.0.1', 0))
                s.listen(1)
            else:
                s.setsockopt(socket.SOL_SOCKET, socket.SO_PASSCRED, 1)
    except OSError as exc:
        result['socket_errors'].append({'test': name, 'errno': exc.errno, 'message': exc.strerror})
result['exit_code'] = 1 if result['errors'] else (20 if result['socket_errors'] else 0)
print(json.dumps(result, indent=2, ensure_ascii=False))
sys.exit(result['exit_code'])
