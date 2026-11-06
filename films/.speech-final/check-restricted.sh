#!/usr/bin/env bash
# Compatibility checker; prefer the per-command procedure in .codex-runtime/README.md.
# Execute only after the platform confirms restricted/enforced networking.
# Do not elevate this entire script: obtain approval only for individual render commands.
set -euo pipefail
cd /workspace/lemo-opuscar
source films/.publication-check/env.sh
.venv/bin/python -B films/.speech-final/verify-whisper.py
OMP_NUM_THREADS=2 .venv/bin/python -B films/.speech-final/offline-python.py core/tts/tts.py films/.publication-check/lines.json films/.speech-final/kokoro-restricted
OMP_NUM_THREADS=4 .venv/bin/python -B films/.speech-final/offline-python.py core/tts/asr_check.py films/.publication-check/lines.json films/.speech-final/kokoro-restricted --lang fr --model /workspace/models/whisper-small
/usr/bin/chromium --version
node --import ./films/.codex-runtime/chromium-safe.mjs core/render/still.mjs films/.installation-audit/graphics 0 --out films/.speech-final/2d-restricted
node --import ./films/.codex-runtime/chromium-safe.mjs core/render/still.mjs films/.installation-audit/graphics 0 --q mode=3d --size 640x360 --out films/.speech-final/3d-restricted
node --import ./films/.codex-runtime/chromium-safe.mjs core/render/video.mjs films/.installation-audit/graphics --fps 24 --workers 1 --out films/.speech-final/video-restricted.mp4
ffmpeg -hide_banner -loglevel error -y -i films/.speech-final/kokoro-restricted/french.wav -af apad -t 4 films/.speech-final/voice-mix-restricted.wav
sh core/render/mux.sh films/.speech-final/video-restricted.mp4 films/.speech-final/voice-mix-restricted.wav films/.speech-final/regression-restricted.mp4 24 0
ffmpeg -v error -xerror -i films/.speech-final/regression-restricted.mp4 -f null -
.venv/bin/python -m pip check
