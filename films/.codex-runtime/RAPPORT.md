# Finalisation opérationnelle — Lemo-Opuscar

Date : 5 novembre 2026, fuseau Pacific/Tahiti.

## Conclusion

La chaîne demandée fonctionne dans l'instance restaurée depuis l'environnement publié : voix françaises Edge et Kokoro, Whisper local, rendu 2D, rendu 3D logiciel séquentiel et MP4 avec voix française. Les tests qui utilisent les sockets nécessitent actuellement une demande ciblée require_escalated ; les demandes de cette mission ont été autorisées et exécutées. Les autres étapes ont fonctionné en use_default.

Les 66 définitions de styles passent le contrôle source-only. Les 2 478 fichiers suivis sont préservés, sans modification des composants applicatifs ni installation de dépendances. Les ajouts sont des helpers et résultats sous films/.codex-runtime/, ignoré par Git. Les nouvelles consignes de démarrage sont sauvegardées dans le brouillon ; aucune nouvelle publication, aucun commit ni push n'a été effectué.

## Résultats réels

| Contrôle | Résultat | Preuve |
|---|---|---|
| Réseau actif | Session connectée, observations actuelles, restricted/enforced ; domaines personnalisés huggingface.co et speech.platform.bing.com, préréglage package_managers | Lecture officielle avant les essais ; aucune règle modifiée |
| Prévalidation en use_default | Sources/modèles/dépendances valides ; socket IPv4 et setsockopt Unix refusés avec EPERM | preflight-result.json ; code 20, distinct d'un défaut d'installation |
| Définitions de styles | 66, aucun problème | Fonctions officielles style_slugs/style_format de tools/release.py et correspondance avec le catalogue |
| Whisper | Révision 536b0662742c02347bc0e980a01041f333bce120 vérifiée localement ; transcription française exacte, mismatches: 0 | validation/whisper.log ; modèle /workspace/models/whisper-small |
| Kokoro français | WAV PCM s16le, mono, 24 kHz, 2,4615 s ; décodage complet réussi | validation/kokoro.log et kokoro/french.wav |
| Hors ligne | Kokoro et Whisper exécutés en use_default, HF_HUB_OFFLINE=1 et connexions Python interdites | Wrapper offline-python.py existant ; aucun téléchargement |
| Edge français | Wrapper existant, fr-FR-DeniseNeural ; MP3 mono 24 kHz, 4,080 s, 24 480 octets ; FFprobe et décodage complet réussis | validation/edge-fr.mp3 ; commande bornée à 20 s, code 0 |
| Chromium / Playwright | Chromium 155.0.8059.79, vrai binaire /usr/lib/chromium/chromium ; sandbox interne explicitement activé | Lignes CHROMIUM_VALIDATED des journaux de rendu |
| Rendu 2D local | Deux images 1920×1080, t=0 et t=1 ; contenu non uniforme et mouvement confirmé | validation/2d.log, 2d/t_0.jpg, 2d/t_1.jpg, graphics-check.json |
| Rendu 3D local | Deux images 640×360, SwiftShader et postprocessing, rendues séquentiellement ; mouvement confirmé | validation/3d.log, 3d/t_0.jpg, 3d/t_1.jpg ; environ 1,9–2,0 s par capture |
| Protection Chromium | Le helper impose chromiumSandbox:true ; vérification des arguments réels ; --no-sandbox refusé avant lancement dans le test négatif | chromium-safe.mjs et résultat de test dans la session |
| Export vidéo | 96 images, 1920×1080, 24 i/s, H.264, durée 4 s ; export séquentiel avec un worker | validation/video.log ; rendu en environ 7 s |
| Export animé 3D complet | 48 images, 640×360, 12 i/s, H.264, durée 4 s ; rendu séquentiel et décodage complet réussis | validation/video-3d.log et ffprobe-3d.json ; environ 94 s |
| Voix du MP4 | Nouvelle voix Kokoro française, complétée par silence, AAC mono 48 kHz | validation/voice-mix.wav ; validation/mux.log |
| Mixage | -14,0 LUFS, pic -1,2 dBFS | validation/mux.log |
| MP4 final | FFprobe conforme aux dimensions/codecs/durée attendus ; décodage complet FFmpeg avec -xerror réussi | validation/final.mp4 et ffprobe.json ; commandes sorties avec code 0 |
| MP4 mixte 2D/3D avec voix | Deux secondes 2D puis deux secondes 3D, sortie 1080p24, 96 images, 4 s, H.264/AAC ; décodage intégral et assertions réussis | validation/final-2d-3d.mp4, ffprobe-combined.json et mux-combined.log |
| Python | pip check : aucune dépendance cassée | Exécution en use_default, code 0 |
| Sources | 2 478 fichiers suivis identiques à la référence SHA-256 ; Git propre | preflight-result.json, contrôle final Git et empreintes |

Texte de contrôle hors ligne : « Bonjour, la synthèse vocale fonctionne. » La transcription Whisper est identique. Cette phrase synthétique vérifie le fonctionnement ; elle ne mesure pas la précision sur un corpus varié ou du son humain bruité.

## Correction ciblée et conservation des sources

Le module core/render/page.mjs lance Playwright sans préciser chromiumSandbox:true. Le défaut Playwright ne permettait donc pas de réutiliser ces commandes brutes en respectant la contrainte de conservation du sandbox interne Chromium.

Le nouveau preload local chromium-safe.mjs corrige ce point pour les commandes concernées sans éditer core/ : il impose l'exécutable système 155, chromiumSandbox:true et SwiftShader. Il refuse les arguments de désactivation du sandbox, puis vérifie la version, le chemin réel et l'absence de ces arguments sur le processus lancé. Son chargement avec `node --import` est explicite et limité à la commande ; aucune permission globale n'est modifiée.

Les refus EPERM de use_default restent présents. Ils n'ont pas été « corrigés » en changeant les protections. Le mécanisme officiel require_escalated a été demandé uniquement pour Edge et les rendus précisément ciblés, conformément à l'autorisation de cette mission. Aucun test de sockets supplémentaire sous élévation ni aucune installation sous élévation n'a été effectué.

Le wrapper Edge existant reste nécessaire : il utilise HTTPS_PROXY pour WSS et ajoute la confiance CA fournie par Codex tout en conservant CERT_REQUIRED et la vérification du nom d'hôte. tts_zh.py est préservé et ne contient pas cette intégration automatique. Aucun jeton, protection du service distant ou réglage TLS global n'a été modifié.

## Mécanisme réutilisable

- preflight.py : contrôle local hors ligne, modèles, versions, définition des styles, empreintes des sources et capacités de sockets. Ne s'élève jamais automatiquement.
- chromium-safe.mjs : adaptation de lancement Chromium par commande, avec sandbox interne actif.
- README.md : commandes validées, ordre des opérations, délais de diagnostic et procédure pour un vrai film.
- Les helpers audio déjà présents sont réutilisés, sans duplication ni changement de dépendances.
- Les instructions start_skill du brouillon renvoient vers cette procédure. Le script d'installation existant et les paramètres réseau sont conservés.

Dans chaque nouvelle tâche, vérifier l'état réseau courant et exécuter preflight.py en use_default. Le code 20 invite l'agent à examiner les permissions de cette tâche et, seulement si elles le permettent, à soumettre la commande précise au contrôle officiel de require_escalated. Le code 20 ne donne aucune autorisation en lui-même. En cas de refus, arrêter l'étape concernée et rapporter la décision. Ne jamais demander d'autorisation générale pour un interpréteur ou d'accès complet.

## Limites restantes et publication

- Les MP4 fournis sont des fixtures techniques, dont un film mixte 2D/3D avec voix. Le segment 3D est calculé en 640×360 à 12 i/s, puis agrandi et converti à 24 i/s pour le montage 1080p. Il ne s'agit pas d'un rendu 3D natif 1080p24 ni d'une validation de toutes les scènes complexes.
- Les 66 définitions sont contrôlées côté sources ; leurs 66 démonstrations n'ont pas été rendues intégralement. Aucun faux succès n'est substitué à un contrôle de release : les vidéos de galerie et certains packs/dépendances de styles restent optionnels et absents.
- SwiftShader utilise le CPU ; les temps de cette fixture ne garantissent pas les performances d'autres scènes.
- Edge dépend du service distant et des contextes TLS internes de edge-tts 7.3.1. Revalider après une mise à niveau.
- Le Chromium système diffère de la version normalement associée à Playwright 1.63.0 ; les opérations testées fonctionnent, sans garantie universelle sur toutes les API.
- Un avertissement ONNX de persistance d'identifiant de télémétrie et un avertissement pip de cache non accessible ont été émis. Les synthèses et pip check ont réussi ; aucune permission n'a été élargie pour ces messages.
- Les modèles et dépendances existants ont été retrouvés et utilisés dans l'instance issue de la publication. Les **nouveaux helpers** et instructions de cette mission ne sont pas encore inclus dans une nouvelle version publiée. Leur présence dans une future tâche devra être vérifiée après une publication autorisée, ou après un transfert explicite des helpers. Aucune permission d'exécution ne sera présumée persistante.

La session actuelle est opérationnelle avec les conditions d'exécution décrites. La nouvelle préparation est disponible pour revue ; sa publication reste une décision distincte de l'utilisateur.
