# Lemo-Opuscar dans une nouvelle tâche Codex

Ce dossier contient des helpers locaux de validation. Il ne modifie pas les sources suivies, les dépendances, le réseau ou les autorisations système. Son inclusion dans un futur snapshot exige une publication explicitement autorisée ; les permissions d'exécution ne sont pas stockées dans les fichiers.

## 1. Conditions préalables

Depuis `/workspace/lemo-opuscar`, lire AGENTS.md, TECHNIQUE.md et core/README.md. Employer la copie existante, sans créer de worktree ni réinstaller les dépendances. Vérifier avec l'outil officiel `environment_status` que la session est connectée, que les observations sont actuelles et que le réseau est `restricted/enforced`. Les domaines personnalisés validés sont `huggingface.co` et `speech.platform.bing.com`, avec le préréglage package_managers. Ne pas élargir ces règles.

Les fichiers de politique au démarrage et le résultat du script local ne remplacent pas cette vérification de l'état actif. Ne pas imprimer de valeurs de proxy, de certificats ou de secrets.

## 2. Prévalidation en use_default

```sh
timeout 45s .venv/bin/python -B films/.codex-runtime/preflight.py
```

- **0** : les prérequis locaux et les sondes de sockets réussissent. Les tests fonctionnels restent nécessaires.
- **20** : modèles et sources vérifiés, mais socket TCP ou setsockopt Unix refusé. Continuer les tests hors ligne en use_default. Pour Edge et les rendus, vérifier l'autorisation de la tâche avant toute demande ciblée require_escalated.
- **1** : prérequis absent ou différent. Examiner le diagnostic ; ne pas réinstaller, réinitialiser Git ou élargir les permissions automatiquement.

Le contrôle des styles utilise les fonctions officielles `style_slugs()` et `style_format()` de tools/release.py, ainsi que l'appartenance au catalogue. Il vérifie les 66 définitions et leur format sans exiger les MP4 des releases. Ce n'est pas une validation de publication ni un rendu de toutes les démonstrations. La comparaison des sources utilise la référence SHA-256 de l'audit : une modification applicative légitime ultérieure devra être examinée, pas effacée.

## 3. Audio local, sans élévation

Créer un dossier de sortie neuf pour chaque production, par exemple `films/mon-film`. Les entrées sont des fichiers JSON au format du dépôt. Pour reproduire le contrôle existant :

```sh
mkdir -p films/mon-film
timeout 120s env OMP_NUM_THREADS=2 .venv/bin/python -B films/.speech-final/offline-python.py core/tts/tts.py films/.publication-check/lines.json films/mon-film/kokoro
timeout 60s env OMP_NUM_THREADS=4 .venv/bin/python -B films/.speech-final/offline-python.py core/tts/asr_check.py films/.publication-check/lines.json films/mon-film/kokoro --lang fr --model /workspace/models/whisper-small
```

Le wrapper active HF_HUB_OFFLINE et interdit les connexions Python. Les modèles Kokoro et Whisper sont locaux. Le modèle Whisper est figé à `536b0662742c02347bc0e980a01041f333bce120` ; `films/.speech-final/verify-whisper.py` vérifie son intégrité sans téléchargement.

## 4. Commandes qui nécessitent les sockets

Exécuter normalement si les sockets fonctionnent. En cas d'EPERM, **ne pas utiliser sudo, changer Seccomp, les namespaces, les règles réseau, ou le mode accès complet**. Si les instructions de la tâche autorisent une demande ciblée, soumettre uniquement la commande concernée avec `sandbox_permissions: require_escalated` et une justification. Ce champ appartient à l'outil Codex ; ce n'est pas une option shell. Ne pas encapsuler une installation ou des commandes générales dans cette demande. La plateforme peut refuser : dans ce cas, arrêter et rapporter son motif. Une réussite antérieure n'accorde aucune permission permanente.

### Edge français

```sh
timeout --signal=KILL 20s .venv/bin/python -B films/.speech-final/edge-with-platform-ca.py --voice fr-FR-DeniseNeural --text 'Bonjour, la synthèse vocale française fonctionne.' --write-media films/mon-film/edge-fr.mp3
```

Le helper existant fournit le proxy WSS et charge l'autorité CA de Codex dans les contextes de edge-tts 7.3.1, avec vérification TLS et du nom d'hôte conservée. Revalider après une mise à niveau de la bibliothèque. `core/tts/tts_zh.py` n'intègre pas automatiquement ce helper : ne pas supposer qu'un appel brut applique la correction. Edge nécessite son service en ligne ; Kokoro reste le moteur hors ligne.

### Rendus avec sandbox interne Chromium activé

Les outils de rendu du dépôt ne passent pas explicitement `chromiumSandbox:true` à Playwright. Utiliser le preload local ci-dessous pour conserver le sandbox Chromium. Il force le binaire système 155 et SwiftShader, vérifie le lancement effectif et refuse les arguments désactivant le sandbox. Il ne change aucune source suivie ni configuration globale. Son périmètre testé est `chromium.launch` utilisé par les outils core ; ne pas généraliser à une autre bibliothèque ou à launchPersistentContext sans contrôle.

```sh
timeout -k 5s 60s node --import ./films/.codex-runtime/chromium-safe.mjs core/render/still.mjs films/.installation-audit/graphics 0 1 --out films/mon-film/2d
timeout -k 5s 90s node --import ./films/.codex-runtime/chromium-safe.mjs core/render/still.mjs films/.installation-audit/graphics 0 1 --q mode=3d --size 640x360 --out films/mon-film/3d
timeout -k 5s 180s node --import ./films/.codex-runtime/chromium-safe.mjs core/render/video.mjs films/.installation-audit/graphics --fps 24 --workers 1 --out films/mon-film/video.mp4
timeout -k 5s 240s node --import ./films/.codex-runtime/chromium-safe.mjs core/render/video.mjs films/.installation-audit/graphics --q mode=3d --size 640x360 --fps 12 --workers 1 --out films/mon-film/video-3d.mp4
```

Ces exemples utilisent la fixture de contrôle. L'export 3D complet de quatre secondes à 12 i/s a pris environ 94 s ; les temps des seules images fixes ne suffisent pas à prévoir toute la durée. Pour un film réel, remplacer ce chemin par la composition choisie, qui doit fournir index.html, window.READY, window.DUR et window.render(t). Adapter le délai à la durée mesurée et garder un worker. Ne pas interpréter les délais de ces tests comme des limites universelles de production.

## 5. Mixage et validation sans élévation

Pour cette fixture de quatre secondes, compléter la voix courte par du silence, puis mixer :

```sh
ffmpeg -hide_banner -loglevel error -i films/mon-film/kokoro/french.wav -af apad -t 4 films/mon-film/voice-mix.wav
sh core/render/mux.sh films/mon-film/video.mp4 films/mon-film/voice-mix.wav films/mon-film/final.mp4 24 0
ffprobe -v error -show_streams -show_format -of json films/mon-film/final.mp4
ffmpeg -v error -xerror -i films/mon-film/final.mp4 -f null -
```

Vérifier également le MP3 Edge et le WAV Kokoro par FFprobe et décodage FFmpeg. Pour une production réelle, assembler la narration sur la durée réelle du film, sans la couper pour faire passer ce test.

La validation inclut aussi une vidéo de quatre secondes avec deux secondes 2D puis deux secondes 3D. Pour reproduire l'assemblage, avant le mixage, remplacer video.mp4 par combined.mp4 produit ainsi :

```sh
ffmpeg -hide_banner -loglevel error -n -i films/mon-film/video.mp4 -i films/mon-film/video-3d.mp4 -filter_complex '[0:v]trim=duration=2,setpts=PTS-STARTPTS,fps=24,setsar=1[v0];[1:v]trim=duration=2,setpts=PTS-STARTPTS,scale=1920:1080:flags=lanczos,fps=24,setsar=1[v1];[v0][v1]concat=n=2:v=1:a=0[v]' -map '[v]' -an -c:v libx264 -preset medium -crf 18 -pix_fmt yuv420p films/mon-film/combined.mp4
```

Le segment 3D est calculé en 640×360 à 12 i/s puis agrandi et converti à 24 i/s : cela ne crée pas 24 images 3D distinctes par seconde. Le résultat est une preuve fonctionnelle, pas une promesse de rendu 3D natif 1080p en temps réel.

## 6. Clôture

Confirmer les codecs, la durée, la voix, l'absence d'erreur de décodage et le mouvement sur plusieurs images. Contrôler Git et les 66 styles. Ne jamais publier, committer ou pousser automatiquement. Le rapport de cette exécution est `RAPPORT.md` et ses preuves sont dans `validation/`.
