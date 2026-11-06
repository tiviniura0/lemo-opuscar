# Contrôle final avant publication — Lemo-Opuscar V2

Date : 5 novembre 2026. Conclusion : les fonctions principales sont validées sur la machine actuelle ; le brouillon est préparé pour publication après votre confirmation. Aucune publication n’a été effectuée.

## 1. Chromium réellement utilisé

L’instrumentation de Playwright a enregistré le chemin demandé, la version retournée par le navigateur et le véritable exécutable du processus :

- Sélecteur : `/usr/bin/chromium`.
- Binaire réel : `/usr/lib/chromium/chromium`.
- Version : `155.0.8059.79`.

Les essais actuels passent pour Canvas 2D, CRT WebGL2 et Three.js avec post-traitement (GTAO, profondeur de champ, bloom). Les commandes communes `still.mjs`, `video.mjs`, `events.mjs` et `readcheck.mjs` ont toutes lancé cette version. Les journaux sont dans `chromium-launches.jsonl`.

L’inspection des scripts a révélé deux anciennes conventions supplémentaires : `CHROME_PATH` pour Halftone Dossier et `CHROME` pour Game Show. Leurs véritables points d’entrée ont été exécutés jusqu’au lancement du navigateur, dont le chemin et la version ont été vérifiés, puis le navigateur a été fermé. Il ne s’agit pas de rendus complets de ces deux démonstrations. Les autres lancements examinés utilisent le sélecteur commun de `core/render/browser.mjs`.

Les instructions réutilisables définissent maintenant :

```sh
export PLAYWRIGHT_CHROME=/usr/bin/chromium
export CHROME_PATH=/usr/bin/chromium
export CHROME=/usr/bin/chromium
export LEMO_ANGLE=swiftshader
```

Copie directement utilisable : `env.sh`. Aucun script suivi du dépôt n’a été modifié.

Un essai 3D a dépassé le délai de navigation de 30 secondes pendant des vérifications simultanées. L’essai identique a ensuite réussi seul, sans changement de code ou de délai ; la capture a pris environ 11,8 secondes. Les processus de cet essai terminé étaient déjà arrêtés (état zombie), aucun autre processus n’a été tué. La cause précise du dépassement n’est pas démontrée ; la charge simultanée reste une hypothèse cohérente avec le succès isolé. La recommandation est de lancer les tâches lourdes séquentiellement, avec un seul worker. Le rendu reste logiciel, sans promesse de performance GPU.

Le Chromium 153 associé exactement à Playwright reste absent, son téléchargement ayant été refusé par la politique réseau lors de l’audit précédent. Chromium 155 constitue l’alternative documentée et vérifiée, sans garantie sur chaque ancienne démonstration.

## 2. Whisper et fonctionnement hors ligne

Le paquet faster-whisper est installé. Son API accepte un dossier local de modèle CTranslate2, et l’outil officiel `core/tts/asr_check.py` accepte ce dossier par `--model`. La recherche effectuée dans le workspace et le cache Hugging Face standard n’a trouvé aucun modèle compatible.

Deux vérifications ont été exécutées :

| Vérification | Résultat |
|---|---|
| Chargement de base avec `HF_HUB_OFFLINE=1` | Sortie 2, `LocalEntryNotFoundError`, aucun snapshot local disponible |
| Téléchargement officiel de base depuis Hugging Face | Sortie 2, `ProxyError: 403 Forbidden` |

Traces : `whisper-offline.log`, `whisper-network.log` et fichiers `.exit`. Le wrapper de journalisation a terminé normalement ; les sorties **2** des commandes Whisper sont enregistrées distinctement. Aucun miroir, proxy alternatif ou contournement de la politique n’a été utilisé.

Une intégration strictement hors ligne serait possible si un modèle complet et de provenance vérifiée était fourni par un transfert autorisé. Conserver le modèle multilingue dans `/workspace/models/whisper-base`, notamment `model.bin`, `config.json`, `tokenizer.json`, `preprocessor_config.json` et les fichiers de vocabulaire distribués. `tokenizer.json` est nécessaire pour éviter un téléchargement de secours du tokenizer. Vérifier les empreintes à partir d’une source de confiance avant utilisation, puis exécuter :

```sh
HF_HUB_OFFLINE=1 .venv/bin/python core/tts/asr_check.py \
  films/.publication-check/lines.json films/.publication-check/voices \
  --lang fr --model /workspace/models/whisper-base
```

Cette intégration avec poids locaux n’a pas pu être exécutée faute de fichiers : la transcription et la vérification automatique du texte prononcé restent indisponibles. Il n’est pas possible de fabriquer ou d’installer hors ligne un modèle absent.

## 3. Contenu réutilisable

Présence vérifiée sur disque des deux fichiers Kokoro : `core/tts/kokoro-v1.0.onnx` (325 532 387 octets) et `core/tts/voices-v1.0.bin` (28 214 398 octets). Leurs empreintes sont consignées dans `kokoro-files.json`. Leur archive officielle avait été contrôlée par SHA-256 lors de l’audit.

Les dépendances centrales, voix et musique sont présentes dans `.venv` et `node_modules` ; `pip check` réussit de nouveau. Les scripts sources et les fichiers de validation sont présents. Le `install_script` sauvegardé reproduit l’installation npm verrouillée, les trois niveaux Python, et récupère les ressources officielles vérifiées si elles manquent. Les fichiers de modèles et les dépendances présents seront inclus dans le snapshot de système de fichiers lors de la publication ; ils ne sont pas encodés dans le texte du script.

Le `start_skill` du brouillon a été complété avec les trois sélecteurs Chromium et la procédure Whisper hors ligne. Sa sauvegarde est confirmée (`saved`, publication toujours nécessaire). Aucun domaine réseau ni secret n’a été ajouté. Les instructions sont copiées dans `start-saved.md`.

La réutilisation est préparée, mais la restauration dans une nouvelle tâche ne peut pas être certifiée avant qu’un snapshot ait été publié puis restauré. Aucun processus en cours n’est requis pour cette préparation.

## 4. Derniers tests essentiels

| Test actuel | Résultat |
|---|---|
| Rendu Chromium Canvas 2D | Réussi, image 1920×1080 non uniforme |
| Rendu CRT et Three.js | Réussis, images 640×360 non uniformes |
| Événements et temps de lecture | Réussis, durée 4 secondes |
| Nouvelle synthèse française Kokoro | Réussie : ff_siwis, 24 kHz, 2,4615 s, signal fini non silencieux |
| Nouveau rendu vidéo | Réussi : 96 images, 24 fps, 1920×1080 |
| Export voix + image | Réussi : H.264 + AAC 48 kHz, durée 4,000 s |
| Normalisation | −13,9 LUFS ; LRA 2,4 ; crête −1,2 dBFS |
| Décodage intégral FFmpeg `-xerror` | Réussi, sortie 0 |
| Intégrité du dépôt | 2 478 fichiers suivis comparés par SHA-256, aucun changement ; git status vide |
| Conservation des styles | 66 styles préservés |

L’export de cette nouvelle exécution est `verification-finale.mp4`. Les sources de test réutilisent le banc graphique de l’audit ; la voix et la vidéo ont été régénérées dans ce dossier, puis assemblées. Les 66 démonstrations ne sont pas prétendues testées individuellement.

## 5. Fonctions optionnelles à signaler avant publication

- Whisper : modèle absent ; téléchargement refusé ; aucun contrôle ASR réussi.
- Edge TTS : service Microsoft bloqué lors de l’audit précédent ; aucune synthèse Edge validée.
- Chromium 153 correspondant à Playwright : téléchargement bloqué ; Chromium système 155 validé à sa place.
- Démonstrations complètes : certains médias, polices, banques d’instruments et paquets particuliers restent à récupérer selon le style. Les vidéos de Releases ne sont pas installées pour la galerie locale.
- Accélération GPU matérielle : non validée ; utiliser les réglages de rendu logiciel testés.

Les fonctions principales réussissent. Le brouillon est préparé pour publication avec ces limites explicites. La publication reste en attente de votre confirmation.
