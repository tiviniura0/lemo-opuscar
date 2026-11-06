#!/usr/bin/env bash
set -euo pipefail
cd /workspace/lemo-opuscar
# This cloud task already has an isolated checkout. Preserve sources and lockfiles.
node -e 'if (+process.versions.node.split(".")[0] < 20) process.exit(1)'
python3 -c 'import sys; assert (3,11) <= sys.version_info < (3,14), "Kokoro requires Python 3.11-3.13"'
command -v chromium
ffmpeg -version | sed -n '1p'
python3 - <<'PY'
import re,subprocess
v=subprocess.check_output(['ffmpeg','-version'],text=True)
assert int(re.search(r'ffmpeg version (?:n)?(\d+)',v)[1])>=7
PY
npm ci --no-audit --no-fund
if [ ! -x .venv/bin/python ]; then python3 -m venv .venv; fi
.venv/bin/python -m pip install --disable-pip-version-check -r requirements.txt -r requirements-voice.txt -r requirements-music.txt
.venv/bin/python -m pip check
if [ ! -s core/tts/kokoro-v1.0.onnx ] || [ ! -s core/tts/voices-v1.0.bin ]; then sh tools/fetch.sh voice; fi
if [ ! -s core/assets/polyhaven/photo_studio_loft_hall_2k.hdr ] || [ ! -s core/assets/polyhaven/lythwood_lounge_2k.hdr ]; then sh tools/fetch.sh hdri; fi
if [ ! -d core/audio/instruments/karoryfer ]; then sh tools/fetch.sh instruments karoryfer; fi
# Keep the official setup script's bookkeeping consistent with the tested installation.
cat package.json package-lock.json | cksum | cut -d' ' -f1 > node_modules/.lemo-ok
for tier in core voice music; do
  if [ "$tier" = core ]; then req_file=requirements.txt; else req_file="requirements-$tier.txt"; fi
  req_sig=$(cksum < "$req_file" | cut -d' ' -f1)
  py_sig=$(.venv/bin/python -V | cut -d. -f1,2)
  printf '%s-%s\n' "$req_sig" "$py_sig" > ".venv/.lemo-$tier"
done
sh plugin/skills/lemo-opuscar/scripts/setup.sh
# Supported fallback: Chromium 155 is validated; Playwright's matching 153 download is network-blocked.
# Do not disable TLS, change package versions, or bypass the configured network policy.
# Startup must export PLAYWRIGHT_CHROME=/usr/bin/chromium and LEMO_ANGLE=swiftshader.

# Whisper is retained in the prepared filesystem, never fetched at task startup.
# Missing or changed weights must be reimported from the pinned verified source;
# do not silently download a moving revision or use a mirror.
.venv/bin/python -B films/.speech-final/verify-whisper.py
