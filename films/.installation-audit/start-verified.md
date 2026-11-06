# Lemo-Opuscar cloud startup — audited 2026-11-05
Use the existing isolated checkout at /workspace/lemo-opuscar; do not create a Git worktree unless explicitly requested. Read AGENTS.md, TECHNIQUE.md and core/README.md. Preserve all 66 styles, tracked sources, tests, manifests and lockfiles. Write user films and local validation outputs under ignored films/.

The full audit report is films/.installation-audit/RAPPORT.md. User explicitly prohibits publication without their validation. No publication has been performed by the agent.

From /workspace/lemo-opuscar, export PLAYWRIGHT_CHROME=/usr/bin/chromium and LEMO_ANGLE=swiftshader. Use .venv/bin/python. The tested tools are Node 24.22.1, Python 3.12.14, FFmpeg 7.1.5, Playwright 1.63.0, Three.js 0.170.0, system Chromium 155.0.8059.79. Chromium is a supported executable override, but differs from the Playwright-matched 153.0.8010.12: its installation attempt failed with policy HTTP 403 at cdn.playwright.dev. Do not claim that matching browser is installed. WebGL2 runs on CPU/SwiftShader; use one video worker initially. Advanced 3D postprocessing worked at 640x360 but took about 9 seconds per frame.

No persistent service is required. Rendering commands create and close their loopback HTTP server; processes do not survive restoration. Browser, loopback and proxy operations may need execution permission escalation. Preserve injected proxy and CA trust and keep TLS enabled.

Installed and functionally checked: core Node/Python dependencies, Kokoro voice model and voice tier, numba music tier, both official HDRIs, Karoryfer sample pack. Voice/model packs were obtained by tools/fetch.sh, which verifies the SHA-256 in tools/assets.json. Other sample packs and style-specific dependencies are installed only for a selected film, in a project-private environment when the style instructs it. The installer uses npm ci to preserve the lockfile; do not run an installer that rewrites tracked files. Python requirements are unpinned upstream; python-freeze.txt records this audited state.

Readiness checks from the checkout (fixtures are retained ignored filesystem files, not tracked source):
- .venv/bin/python -m pip check
- sh plugin/skills/lemo-opuscar/scripts/setup.sh (report-only invocation; do not set lemo.managed true)
- node core/render/still.mjs films/.installation-audit/graphics 0 1 --q mode=2d --out films/.installation-audit/frames-2d
- node core/render/still.mjs films/.installation-audit/graphics 0 1 --q mode=crt --size 640x360 --out films/.installation-audit/frames-crt
- node core/render/still.mjs films/.installation-audit/graphics 0 1 --q mode=3d --size 640x360 --out films/.installation-audit/frames-3d
- node core/render/events.mjs films/.installation-audit/graphics --size 640x360
- node core/render/readcheck.mjs films/.installation-audit/graphics --size 640x360
- OMP_NUM_THREADS=2 .venv/bin/python core/tts/tts.py films/.installation-audit/lines.json films/.installation-audit/voices
- node core/render/video.mjs films/.installation-audit/graphics --fps 24 --workers 1 --out films/.installation-audit/graphic-1080p.mp4
- sh core/render/mux.sh films/.installation-audit/graphic-1080p.mp4 films/.installation-audit/voice-mix.wav films/.installation-audit/export-voix-1080p.mp4 24 0
- ffmpeg -hide_banner -v error -xerror -i films/.installation-audit/export-voix-1080p.mp4 -f null -
Expected export: 4 seconds, 96 H.264 frames, 1920x1080 at 24fps, AAC 48kHz; audited loudness -13.9 LUFS, peak -1.2dBFS. Kokoro generates English af_bella and French ff_siwis WAVs at 24kHz. If fixtures are absent in a new instance, do not claim these checks ran; validate an existing suitable project instead.

Unresolved: faster-whisper package is installed but its base model download failed with proxy 403 from Hugging Face; asr_check.py exited 2, so speech content was not automatically verified. Edge TTS is installed but its Microsoft service is also blocked (CONNECT 403 to speech.platform.bing.com); no online synthesis is validated. Do not use alternate routes to bypass domain policy. Matching Playwright browser needs cdn.playwright.dev and possibly download destinations reported by its installer. Request supported network-setting changes only if those workflows are needed, then retry after actual propagation. No secrets were requested or configured. Do not treat the whole environment as fully validated while these tests remain blocked.

Gallery: python3 styleboard/build.py --site _site passed, 66 styles. Gallery playback needs release MP4s; 67 linked videos (including OPUSCAR 98) are absent locally. Do not run tools/publish.sh or GitHub deployment as part of readiness. All 2478 tracked files were SHA-256 compared and unchanged; the 66 demos were inventoried, not individually rendered end-to-end.
