# Lemo-Opuscar — validated production workflow after publication
Use the existing checkout /workspace/lemo-opuscar; do not create a worktree unless requested. Read AGENTS.md, TECHNIQUE.md and core/README.md. Preserve the 66 style definitions, application sources, manifests and lockfiles. Put production output and helpers under ignored films/. Never publish, commit or push without explicit user authorization.

The canonical operational procedure is films/.codex-runtime/README.md. The latest evidence is films/.codex-runtime/RAPPORT.md and validation/. Read these first; they supersede older readiness commands that launched Chromium without explicitly enabling its internal sandbox.

## Start each task
1. Check cloud environment_status: current observations, connected session, restricted/enforced networking. Preserve the user's current domains and package-manager presets. Do not turn on unrestricted Internet.
2. Run timeout 45s .venv/bin/python -B films/.codex-runtime/preflight.py with use_default.
   Exit 0 means local prerequisites and socket probes passed, not full application validation.
   Exit 20 means sources/models passed but sockets are unavailable in the current command sandbox.
   Exit 1 means a missing/changed prerequisite requiring investigation. Never automatically install dependencies, reset sources, change Seccomp or change namespaces.
3. The script performs the official source-definition checks for all 66 styles and compares tracked files against the retained audit. It does not require gallery release videos or claim to render every style.
4. Perform local Kokoro/Whisper and FFmpeg operations with use_default. The offline-python.py helper sets HF_HUB_OFFLINE and denies Python connections. Whisper local path: /workspace/models/whisper-small; revision 536b0662742c02347bc0e980a01041f333bce120. verify-whisper.py validates all retained files without download.
5. Only if sockets fail and the current task authorizes it, request require_escalated for the exact bounded Edge test or browser/render command, with justification. This is a per-command platform review, not a shell flag, not an installation permission and not permanent authorization. A previous task's approval is not presumed. On rejection, stop that step and report the platform reason. Do not request blanket bash/python/node approvals or full-access mode.

## Render and voice entrypoints
For core render tools ALWAYS use:
node --import ./films/.codex-runtime/chromium-safe.mjs core/render/still.mjs ...
node --import ./films/.codex-runtime/chromium-safe.mjs core/render/video.mjs ...
The preload forces system Chromium 155, chromiumSandbox:true and SwiftShader; it refuses sandbox-disabling args and checks the actual browser command line/version/executable. It makes no global permission change. The local compatibility checker films/.speech-final/check-restricted.sh now also uses chromium-safe.mjs for all three render calls. Prefer the documented per-command procedure; never elevate the whole checker, since offline checks do not require elevation.
Run 3D sequentially and use --workers 1 initially. Bound each diagnostic; adapt production deadlines to measured scene duration. The 640x360 3D test includes postprocessing; CPU rendering remains slower than GPU.
For French Edge use films/.speech-final/edge-with-platform-ca.py with fr-FR-DeniseNeural. It preserves TLS verification, loads the provided platform CA and uses the existing proxy. core/tts/tts_zh.py is unmodified and does not automatically incorporate that correction. The wrapper depends on internal SSL contexts of edge-tts 7.3.1: revalidate after upgrades.
Use core/render/mux.sh for voice/video assembly, then ffprobe and full ffmpeg -v error -xerror decoding. Keep sample outputs separate from actual production projects.

## Retained state and limits
Installed: Chromium 155.0.8059.79, Playwright 1.63.0, Three.js 0.170.0, FFmpeg 7.1.5, Kokoro models/voices, Whisper small CTranslate2, .venv and node_modules. Current published-instance tests confirmed offline French Kokoro and Whisper, online French Edge through its allowed host, local 2D and sequential 3D renders with the Chromium sandbox enabled, and 4-second 1080p24 H.264/AAC export with French voice and full decode. A full sequential 3D export also passed: 640x360, 12fps, 48 frames, 4 seconds, about 94 seconds render time. A combined 2D/3D 1080p24 film with French voice was produced and fully decoded; its 3D segment is upscaled from 360p12, not natively rendered at 1080p24.
All 2478 tracked files were unchanged; the 66 definitions passed source-only checks. This is not a full render of all 66 demonstrations or a broad French transcription benchmark. Optional style dependencies/sample packs and gallery release MP4s remain on-demand; no installations without justified authorization. Python upstream requirements are not completely pinned; retain the tested snapshot and version record.
Current network rules at validation: custom huggingface.co and speech.platform.bing.com, plus package_managers. Whisper no longer needs network execution. Edge always needs its remote service. Do not change these rules without authorization.
The new .codex-runtime helpers and these draft instructions have not been newly published. A future task based on the previously published snapshot may lack them until a user-authorized publication includes them. No script grants execution permissions across tasks. Verify retained files and actual permissions each time.

## Publication audit and restoration check
Publication readiness and snapshot scope: films/.codex-runtime/PREPUBLICATION.md.
Exact post-publication procedure: films/.codex-runtime/POST-PUBLICATION.md.
First run python3 -B films/.codex-runtime/verify-publication.py in a new restored task to check the retained file manifest, then preflight.py in use_default. Do not equate snapshot files with persistent execution approvals. The .venv interpreter is a symlink to a platform Python runtime; its target and system Chromium/FFmpeg must remain available.
The saved install_script is a reconstruction script containing npm/pip installs and conditional asset downloads, not a normal task-start command. Do not execute it during restoration validation or without installation authorization. Publication snapshots the prepared machine; no reinstall is needed for normal task startup.
