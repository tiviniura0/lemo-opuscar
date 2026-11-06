# Sauvegarde de la V2 corrigée — 6 novembre 2026

## Identité et portée

Source auditée en lecture seule : `/workspace/lemo-opuscar`, environnement Codex sélectionné. Dépôt personnel confirmé par le connecteur GitHub : https://github.com/tiviniura0/lemo-opuscar (public), branche principale `main`. HEAD local `work` et main distant au début de l'audit : `bebbbe1aa92a3cb4bb6f83500e61b23a17d1aa00`. Autre branche distante observée : `directory` à `0eea08d6d761943e9161cc54bf114cc542d36d1e`. Aucun changement suivi ni fichier non suivi non ignoré. Les remotes locaux pointaient vers ce dépôt personnel. Le reflog témoigne d'un checkout/reset au démarrage de l'environnement ; cette mission n'a effectué aucune de ces opérations sur la source.

La V2 est une installation Git accompagnée de dépendances, modèles et helpers persistés dans l'environnement. Les fichiers et manifestes de publication sont présents. La provenance exacte de l'image complète Codex et sa reproductibilité depuis une publication ne sont pas prouvées par ce seul audit.

Cette branche sauvegarde les **2 478 fichiers suivis et 85 fichiers locaux ignorés** (2 563 fichiers originaux). Ils sont copiés depuis les fichiers réellement présents, sans remplacement par une version distante. L'organisation des helpers sous `films/` est conservée par ajout explicite dans Git malgré les règles d'exclusion historiques. `backup-v2/` apporte les inventaires et procédures de cette sauvegarde. Aucun développement V3.

## Corrections réellement conservées

- `films/.codex-runtime/chromium-safe.mjs` : preload Playwright pour Chromium système 155, sandbox interne activé, refus des arguments désactivant le sandbox, contrôle du binaire et de la version. Sélecteurs Chromium et SwiftShader ; les outils core d'origine restent inchangés.
- `films/.publication-check/env.sh` et `trace-chromium.mjs` : sélecteurs et observation des lancements.
- `films/.speech-final/edge-with-platform-ca.py` : confiance dans l'autorité CA fournie par Codex, proxy WSS hérité, vérification TLS et du nom d'hôte conservée. Intégration interne testée historiquement avec edge-tts 7.3.1. Ce wrapper doit être explicitement utilisé : `core/tts/tts_zh.py` brut ne l'applique pas automatiquement.
- `films/.speech-final/offline-python.py` : refus des connexions Python et mode Hugging Face hors ligne ; Kokoro français avec ff_siwis.
- `films/.speech-final/prepare-whisper.py`, `verify-whisper.py`, `model-metadata.json` : provenance officielle et contrôles du modèle small multilingue figé à `536b0662742c02347bc0e980a01041f333bce120`.
- `films/.codex-runtime/` : prévalidation, procédures d'installation/démarrage et procédures post-publication ; `films/.installation-audit/graphics/` et `.publication-check/lines.json` : fixtures 2D/3D et voix française. Scripts core de rendu, mixage, ASR et publication conservés exactement.

Les rapports antérieurs sont des archives de leurs exécutions, pas des preuves de réussite actuelle. Les scripts historiques contiennent parfois des chemins absolus et des installations : **ne pas les exécuter sur l'installation V2 à protéger**. Les anciennes procédures exigent aussi une liste Git de 2 478 fichiers : elles peuvent signaler une différence après les ajouts légitimes de cette branche. Utiliser le vérificateur de sauvegarde ci-dessous pour l'intégrité de la nouvelle branche.

## Inventaires et intégrité

- `source-manifest.json` : chemin, taille et SHA-256 de chacun des 2 563 fichiers originaux inclus.
- `external-resources.json` : 274 fichiers externes observés, dont modèles, HDRI et échantillons d'instruments ; versions et empreintes disponibles.
- `exclusions.json` : exclusions individuelles pour les ressources et sorties ; métadonnées Git, dépendances, caches et galerie générée regroupés avec leurs nombres. L'inventaire complet avant/après de l'installation est conservé dans l'espace isolé d'audit, sans publier ses métadonnées Git internes.
- `python-installed.txt` : versions effectivement installées, y compris dépendances transitives. C'est un relevé figé, pas un lock Python avec empreintes de distributions.
- `runtime-versions.json` : Node 24.22.1, Python 3.12.14, Chromium 155.0.8059.79, FFmpeg 7.1.5 et système observés. Playwright-core 1.63.0 et Three 0.170.0 sont figés par `package-lock.json`, avec intégrités npm.
- `test-results.json` : résultats de cette mission uniquement.

Depuis la racine d'un clone restauré, sans écriture ni téléchargement :

```sh
python3 -B backup-v2/verify.py
```

Attendu : 2 563 fichiers contrôlés, `errors: []`. Ce contrôle couvre les contenus originaux inclus ; le SHA de l'arbre Git couvre également les documents ajoutés par la sauvegarde. Git préserve le bit exécutable, pas les propriétaires ni toutes les permissions Unix : ce dépôt est une sauvegarde de sources reconstructibles, pas une image de machine.

## Résultats réels et limites

Réussis dans une copie isolée : comparaison SHA-256 des 2 563 fichiers, 66 définitions de styles via les fonctions officielles et le catalogue, syntaxe de 16 helpers Python/shell/Node, `pip check`, intégrité Whisper, synthèse Kokoro française, transcription Whisper avec zéro différence et décodage FFmpeg du WAV. Les dépendances Python et modèles existants ont été réutilisés dans l'espace isolé ; les modèles Whisper ont été lus sans modification depuis `/workspace/models/whisper-small`.

Non validés dans cette mission : rendus 2D/3D et export vidéo (écoute TCP locale refusée : `listen EPERM 127.0.0.1`, avant le lancement du navigateur), Edge français (délai de 25 secondes), réinstallation npm (accès au proxy indisponible dans le sandbox de commande ; tentative arrêtée). Les modules Node existants ont été copiés dans l'espace isolé pour les essais. Aucune réinstallation Python complète, aucun rendu des 66 démonstrations et aucune restauration sur machine vierge ne sont revendiqués. Les validations historiques des exports sont conservées comme contexte uniquement.

## Restauration sur une machine distincte

Ne jamais appliquer cette procédure à la V2 existante. Utiliser une autre machine/environnement ou un répertoire neuf, sans remplacer aucun chemin existant. Exemple de clone neuf, après publication et vérification de la branche :

```sh
git clone --branch backup/lemo-opuscar-v2-corrected --single-branch https://github.com/tiviniura0/lemo-opuscar.git lemo-v2-restored
cd lemo-v2-restored
python3 -B backup-v2/verify.py
```

1. Fournir Node/Python/Chromium/FFmpeg et les bibliothèques système correspondant autant que possible à `runtime-versions.json`. Python 3.11–3.13 est requis par Kokoro ; FFmpeg >=7 est requis par le mixage. Aucun binaire système n'est distribué par cette branche.
2. Depuis ce nouveau clone seulement : `npm ci --no-audit --no-fund`, puis `python3 -m venv .venv`, `.venv/bin/python -m pip install -r backup-v2/python-installed.txt` et `.venv/bin/python -m pip check`. Les requirements originaux restent disponibles. La disponibilité future de toutes les distributions figées n'a pas été validée ; ne pas substituer silencieusement des versions si une résolution échoue.
3. Restaurer les packs officiels avec `sh tools/fetch.sh voice`, `sh tools/fetch.sh hdri`, `sh tools/fetch.sh instruments karoryfer`, depuis ce clone neuf. `tools/assets.json` donne le dépôt `lemomo-ai/lemo-opuscar`, tag `assets`, tailles et SHA-256 des archives ; `tools/fetch.sh` contrôle les empreintes. Les packs freepats, salamander, vcsl et vsco2ce sont optionnels selon le style choisi, non tous présents dans la V2 auditée. Les licences et crédits des ressources restent à respecter ; poids, HDRI, fontes téléchargées et samples ne sont pas republiés ici.
4. Whisper : récupérer uniquement `config.json`, `model.bin`, `tokenizer.json`, `vocabulary.txt` depuis `https://huggingface.co/Systran/faster-whisper-small/resolve/536b0662742c02347bc0e980a01041f333bce120/<fichier>` dans un nouveau dossier de modèles. Vérifier les SHA-256 dans `external-resources.json` ou `films/.speech-final/verify-whisper.py`. Le binaire fait 483 546 902 octets, SHA-256 `3e305921506d8872816023e4c273e75d2419fb89b24da97b4fe7bce14170d671`. Respecter les restrictions réseau et arrêter si la destination ou une redirection n'est pas autorisée.
5. Les helpers Whisper historiques utilisent `/workspace/models/whisper-small`. Pour les conserver inchangés, restaurer ce chemin **uniquement dans un environnement neuf**. Sinon, passer le nouveau chemin à `core/tts/asr_check.py --model <chemin>` et vérifier manuellement les empreintes. `prepare-whisper.py` écrit à son chemin absolu : ne pas le lancer sur la machine V2 actuelle.
6. Vérifier Kokoro après extraction : `core/tts/kokoro-v1.0.onnx`, SHA-256 `7d5df8ecf7d4b1878015a32686053fd0eebe2bc377234608764cc0ef3636a6c5` ; `voices-v1.0.bin`, SHA-256 `bca610b8308e8d99f32e6fe4197e7ec01679264efed0cac9140fe9c29f1fbf7d`.
7. Créer un nouveau dossier de sorties et tester avec les commandes ci-dessous. Pour les rendus, conserver un worker et le preload Chromium ; les sockets et le sandbox interne du navigateur doivent être autorisés par la plateforme. Les permissions Codex ne sont pas stockées dans Git. Le preload attend Chromium 155 : un autre numéro échoue explicitement et doit être évalué séparément.

```sh
mkdir -p films/restoration-check
OMP_NUM_THREADS=2 .venv/bin/python -B films/.speech-final/offline-python.py core/tts/tts.py films/.publication-check/lines.json films/restoration-check/kokoro
OMP_NUM_THREADS=4 .venv/bin/python -B films/.speech-final/offline-python.py core/tts/asr_check.py films/.publication-check/lines.json films/restoration-check/kokoro --lang fr --model /chemin/neuf/whisper-small
node --import ./films/.codex-runtime/chromium-safe.mjs core/render/still.mjs films/.installation-audit/graphics 0 1 --out films/restoration-check/2d
node --import ./films/.codex-runtime/chromium-safe.mjs core/render/still.mjs films/.installation-audit/graphics 0 1 --q mode=3d --size 640x360 --out films/restoration-check/3d
node --import ./films/.codex-runtime/chromium-safe.mjs core/render/video.mjs films/.installation-audit/graphics --fps 24 --workers 1 --out films/restoration-check/video.mp4
ffmpeg -hide_banner -loglevel error -n -i films/restoration-check/kokoro/french.wav -af apad -t 4 films/restoration-check/mix.wav
sh core/render/mux.sh films/restoration-check/video.mp4 films/restoration-check/mix.wav films/restoration-check/final.mp4 24 0
ffprobe -v error -show_streams -show_format -of json films/restoration-check/final.mp4
ffmpeg -v error -xerror -i films/restoration-check/final.mp4 -f null -
```

Pour Edge, depuis ce clone neuf : `.venv/bin/python -B films/.speech-final/edge-with-platform-ca.py --voice fr-FR-DeniseNeural --text 'Bonjour.' --write-media films/restoration-check/edge-fr.mp3`. Le réseau et les sélecteurs CA/proxy de la plateforme doivent être fournis au runtime ; aucune valeur sensible n'est sauvegardée. Hors Codex, utiliser un contexte réseau et TLS adapté, sans désactiver les vérifications.

Les démonstrations peuvent demander des fontes ou médias additionnels : consulter `CREDITS`, `SOURCES.jsonl`, `build.sh` et `TECHNIQUE.md` du style. Les films de galerie sont distribués par les releases, pas par ce dépôt de sources ; les exports locaux de contrôle sont volontairement exclus. Ne pas confondre la présence des sources avec la présence de tous les médias de toutes les démonstrations.
