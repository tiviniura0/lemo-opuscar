# Contrôle exact dans une nouvelle tâche

Cette procédure s'exécute seulement après une publication décidée par l'utilisateur. Elle ne publie rien et n'installe rien. Ne pas réutiliser les anciens résultats pour déclarer la nouvelle tâche validée.

## 1. État de la nouvelle instance

L'agent lit `environment_status` : observations actuelles, session connectée, réseau `restricted/enforced`. Comparer domaines personnalisés et préréglages aux paramètres enregistrés : huggingface.co, speech.platform.bing.com et package_managers au moment de cet audit. Si l'état est inconnu ou différent, arrêter les tests réseau et signaler la différence sans modifier les règles.

Lire ensuite les instructions de démarrage de la version publiée. Elles doivent renvoyer vers ce dossier, imposer chromium-safe.mjs et rappeler que require_escalated reste soumis aux autorisations de la tâche et à la décision de la plateforme.

## 2. Fichiers restaurés et contrôle local

Depuis le dépôt, exécuter en use_default :

```sh
cd /workspace/lemo-opuscar
python3 -B films/.codex-runtime/verify-publication.py
timeout 45s .venv/bin/python -B films/.codex-runtime/preflight.py
```

Le premier contrôle doit sortir avec 0 et aucune différence d'empreinte. Le second doit avoir `errors: []`, 66 styles, 2 478 fichiers suivis inchangés, et Whisper vérifié. Son code 20 est attendu si le sandbox de commande refuse les sockets : ce n'est pas un défaut des modèles, mais cela n'autorise pas automatiquement une élévation. Un code 1 bloque la suite jusqu'au diagnostic de la différence.

Créer un dossier de résultats neuf ; ne pas écraser un contrôle antérieur :

```sh
mkdir films/post-publication-check
```

Si ce nom existe déjà, choisir un autre nom et le substituer uniformément aux commandes suivantes. Ne pas supprimer les anciens fichiers.

## 3. Audio hors ligne en use_default

```sh
timeout 120s env OMP_NUM_THREADS=2 .venv/bin/python -B films/.speech-final/offline-python.py core/tts/tts.py films/.publication-check/lines.json films/post-publication-check/kokoro
timeout 60s env OMP_NUM_THREADS=4 .venv/bin/python -B films/.speech-final/offline-python.py core/tts/asr_check.py films/.publication-check/lines.json films/post-publication-check/kokoro --lang fr --model /workspace/models/whisper-small
ffprobe -v error -show_streams -show_format -of json films/post-publication-check/kokoro/french.wav
ffmpeg -v error -xerror -i films/post-publication-check/kokoro/french.wav -f null -
```

Attendus : WAV mono 24 kHz, environ 2,462 s ; transcription « Bonjour, la synthèse vocale fonctionne. », zéro différence ; aucun accès réseau ou téléchargement de modèle.

## 4. Tests nécessitant les sockets

Utiliser use_default si possible. En cas d'EPERM confirmé, lire l'autorisation de la nouvelle tâche. Si elle ne couvre pas ces commandes, demander un accord ciblé. Sinon, demander au mécanisme officiel require_escalated l'exécution de **chaque commande concernée**, avec justification ; ne pas élever cette procédure complète, un interpréteur générique ou une installation. Arrêter l'étape concernée si la plateforme refuse. Ne jamais désactiver le sandbox Chromium, Seccomp ou les namespaces.

Edge français, une commande bornée :

```sh
timeout --signal=KILL 20s .venv/bin/python -B films/.speech-final/edge-with-platform-ca.py --voice fr-FR-DeniseNeural --text 'Bonjour, la synthèse vocale française fonctionne.' --write-media films/post-publication-check/edge-fr.mp3
```

Puis vérifier en use_default :

```sh
ffprobe -v error -show_streams -show_format -of json films/post-publication-check/edge-fr.mp3
ffmpeg -v error -xerror -i films/post-publication-check/edge-fr.mp3 -f null -
```

Attendus : MP3 valide, mono 24 kHz, environ 4,08 s ; une légère variation du service distant n'est pas une corruption si la voix et le décodage sont corrects.

Rendus locaux, à exécuter séquentiellement, chaque commande séparément :

```sh
timeout -k 5s 60s node --import ./films/.codex-runtime/chromium-safe.mjs core/render/still.mjs films/.installation-audit/graphics 0 1 --out films/post-publication-check/2d
timeout -k 5s 90s node --import ./films/.codex-runtime/chromium-safe.mjs core/render/still.mjs films/.installation-audit/graphics 0 1 --q mode=3d --size 640x360 --out films/post-publication-check/3d
timeout -k 5s 180s node --import ./films/.codex-runtime/chromium-safe.mjs core/render/video.mjs films/.installation-audit/graphics --fps 24 --workers 1 --out films/post-publication-check/video.mp4
timeout -k 5s 240s node --import ./films/.codex-runtime/chromium-safe.mjs core/render/video.mjs films/.installation-audit/graphics --q mode=3d --size 640x360 --fps 12 --workers 1 --out films/post-publication-check/video-3d.mp4
```

Attendus : logs CHROMIUM_VALIDATED avec version 155 et chromiumSandbox=true ; images non vides et différentes à t=0/t=1 ; 96 images 2D à 24 i/s et 48 images 3D à 12 i/s, quatre secondes chacune. La 3D est logicielle, sans garantie de temps réel.

## 5. Montage, contrôle et intégrité en use_default

```sh
ffmpeg -hide_banner -loglevel error -n -i films/post-publication-check/kokoro/french.wav -af apad -t 4 films/post-publication-check/voice-mix.wav
sh core/render/mux.sh films/post-publication-check/video.mp4 films/post-publication-check/voice-mix.wav films/post-publication-check/final.mp4 24 0
ffprobe -v error -show_streams -show_format -of json films/post-publication-check/final.mp4
ffmpeg -v error -xerror -i films/post-publication-check/final.mp4 -f null -
ffmpeg -v error -xerror -i films/post-publication-check/video-3d.mp4 -f null -
.venv/bin/python -m pip check
git diff --exit-code
git diff --cached --exit-code
git status --porcelain
```

Attendus : MP4 1080p24 de quatre secondes, H.264/AAC avec voix, décodage intégral sans erreur, dépendances cohérentes et aucun fichier suivi modifié. Pour refaire le montage mixte 2D/3D, suivre la commande d'assemblage validée dans README.md.

Conclure séparément sur : fichiers restaurés, intégrité des modèles, audio hors ligne, Edge, rendu avec sandbox actif et contexte d'exécution autorisé. Un test bloqué par une permission ne doit pas être marqué réussi. Ne pas publier, committer ou pousser à l'issue de ce contrôle.
