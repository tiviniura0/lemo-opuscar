# Audit final avant publication

Date : 5 novembre 2026, Pacific/Tahiti.

## Conclusion : PRÊT À PUBLIER

La préparation est prête à être soumise à la publication par l'utilisateur. Aucun défaut bloquant des modèles, des sources, des helpers actifs ou des instructions sauvegardées n'a été trouvé. Les conditions d'exécution demeurent explicites : les opérations nécessitant des sockets peuvent nécessiter une demande ciblée require_escalated autorisée par la tâche et acceptée par la plateforme. Cette possibilité ne devient jamais une permission permanente par publication.

Aucune publication, installation, requête de téléchargement, modification du réseau, suppression de fichier, création de commit ou opération de push n'a été effectuée pendant cet audit. Aucun test avec require_escalated n'a été lancé pendant cet audit : les preuves fonctionnelles de la mission précédente sont conservées.

## Contrôles effectués maintenant

| Élément | Résultat |
|---|---|
| Réseau | État officiel actuel restricted/enforced, session connectée ; huggingface.co et speech.platform.bing.com conservés avec package_managers |
| Prévalidation | errors vide ; code 20 uniquement pour les EPERM de socket IPv4 et setsockopt Unix dans use_default |
| Whisper | Répertoire local et quatre fichiers vérifiés par SHA-256 ; révision figée 536b0662742c02347bc0e980a01041f333bce120 |
| Kokoro | Modèle et voix locaux présents, empreintes attendues vérifiées |
| Styles | 66 définitions, zéro anomalie au contrôle officiel style_format et au rapprochement du catalogue |
| Sources | 2 478 fichiers suivis, mêmes fichiers et mêmes SHA-256 que la référence ; Git propre |
| Helpers Python/Node/shell | Lecture du code et vérifications syntaxiques réussies |
| Chromium | Le preload impose chromiumSandbox:true ; quatre options de désactivation sont refusées avant lancement dans les tests négatifs |
| TLS Edge | CERT_REQUIRED et check_hostname conservés ; ajout de l'autorité Codex existante, pas de désactivation TLS |
| Seccomp/namespaces | Aucune commande de modification dans les nouveaux helpers actifs ; aucune modification exécutée |
| require_escalated | Aucune demande automatique depuis un script ; consignes limitées aux commandes ciblées et à la décision de la plateforme |
| Brouillon | Instructions complètes relues puis actualisées ; install_script inchangé et vérifié syntaxiquement, pas exécuté |

Les occurrences textuelles de --no-sandbox et des options similaires dans chromium-safe.mjs sont des motifs de refus, pas des arguments transmis au navigateur. Les mentions de sudo, Seccomp et namespaces dans la procédure sont des interdictions. Le périmètre vérifié est le chemin de production documenté, avec chromium.launch. Les API Chromium et autres scripts du dépôt appelés directement ne bénéficient pas automatiquement de ce preload.

## Ajustement local issu de l'audit

L'ancien helper ignoré par Git films/.speech-final/check-restricted.sh utilisait encore trois commandes de rendu sans preload. Ses trois appels utilisent maintenant explicitement chromium-safe.mjs, avec commentaire interdisant d'élever le script complet. Le fichier a été conservé, sa syntaxe vérifiée ; les moteurs sous-jacents et le preload avaient déjà été testés fonctionnellement. Le helper complet n'a pas été relancé durant cet audit.

Les consignes sauvegardées reflètent cet ajustement et recommandent toujours la procédure par commande. Aucun fichier suivi du dépôt n'a été modifié. Le script d'installation reste une procédure de reconstruction avec npm/pip et téléchargements conditionnels : il ne doit pas être exécuté au démarrage normal d'une tâche ou pendant le contrôle de restauration. Le réglage lemo.managed est absent dans le dépôt actuel ; aucun changement Git automatique n'a été déclenché.

## Ce que la publication doit conserver

La documentation officielle d'onboarding décrit une publication qui prend un snapshot du système de fichiers préparé et crée une version active de configuration. Les éléments ci-dessous sont présents sous /workspace et destinés à ce snapshot ; le fait qu'ils soient ignorés par Git ne les rend pas équivalents à des fichiers absents du snapshot.

| Ensemble | Emplacement et rôle |
|---|---|
| Nouveaux helpers | films/.codex-runtime/preflight.py et chromium-safe.mjs |
| Contrôle de restauration | films/.codex-runtime/verify-publication.py et publication-manifest.json |
| Procédures et rapports | films/.codex-runtime/README.md, POST-PUBLICATION.md, PREPUBLICATION.md et RAPPORT.md |
| Copies des consignes relues | publication-install-saved.sh et publication-start-saved.md, sous films/.codex-runtime/ |
| Preuves de fonctionnement | films/.codex-runtime/validation/ : logs, images, voix, vidéos et contrôles JSON, dont final-2d-3d.mp4 |
| Helpers audio conservés | films/.speech-final/edge-with-platform-ca.py, offline-python.py, verify-whisper.py ; helper de réacquisition figé et ses métadonnées |
| Données requises par les contrôles | films/.installation-audit/baseline.json, styles.json, graphics/index.html ; films/.publication-check/lines.json et env.sh |
| Modèle Whisper | /workspace/models/whisper-small/ : model.bin, config.json, tokenizer.json, vocabulary.txt, verified-manifest.json |
| Kokoro | core/tts/kokoro-v1.0.onnx et core/tts/voices-v1.0.bin |
| Dépendances et sources | .venv, node_modules, dépôt complet et ses 66 styles, autres actifs déjà préparés |
| Configuration | Instructions install_script/start_skill et politique restrictive enregistrées dans le brouillon |

Le manifeste contient les tailles et SHA-256 des fichiers de publication sélectionnés, des helpers nécessaires, des fixtures et des modèles. Il ne remplace pas un manifeste complet de l'image système ni une garantie de restauration ; il permet de détecter les pertes ou altérations dans une nouvelle tâche.

## Ce qu'il ne faut pas présumer persistant

- Processus Chromium, serveurs locaux, sockets, PID, connexions et ports : ils doivent être recréés.
- Approbations require_escalated : elles ne sont pas incluses dans les fichiers ni garanties dans une autre tâche.
- Valeurs de proxy, confiance CA et authentification fournies par Codex : elles sont injectées par la plateforme, sans copie de secrets dans ces helpers.
- Variables exportées dans un shell ou modifications de contexte Python : elles ne survivent pas comme processus. Le wrapper Edge et le preload Chromium les réappliquent uniquement dans leur propre commande.
- Fichiers temporaires sous /tmp : aucun n'est requis par la procédure ; ne pas compter sur leur restauration.
- Clone Git seul : il ne contient pas les fichiers ignorés, modèles ou helpers locaux. Il ne suffit pas à reconstruire cet environnement sans les actifs préparés.
- Python de la plateforme : .venv/bin/python est un lien vers /opt/codex/runtimes/codex-primary-runtime/dependencies/python/bin/python3.12. Sa cible existe actuellement, mais le venv n'est pas un paquet autonome. Le vérificateur contrôle la résolution du lien ; Chromium et FFmpeg système doivent aussi rester disponibles.
- Une tâche déjà ouverte sur l'ancienne version ne migre pas nécessairement vers la nouvelle. Pour vérifier la nouvelle publication, ouvrir une nouvelle tâche explicitement basée sur celle-ci.

## Validation exacte après publication

Suivre POST-PUBLICATION.md, dans cet ordre :

1. Vérifier l'identité de la nouvelle tâche, les consignes publiées et restricted/enforced dans environment_status.
2. Exécuter verify-publication.py, puis preflight.py en use_default. Ne pas installer de dépendances pour masquer un échec de restauration.
3. Produire une nouvelle voix Kokoro et la transcrire avec Whisper hors ligne, dans un dossier neuf.
4. Tester Edge et les rendus locaux 2D/3D avec les commandes bornées documentées. Si les sockets sont refusées, respecter les autorisations de cette nouvelle tâche avant chaque demande ciblée require_escalated.
5. Générer le MP4, vérifier H.264/AAC, durée et nombre d'images, décoder intégralement, puis contrôler Git et les styles.

La procédure contient les commandes complètes et les résultats attendus. Aucun changement réseau, accès complet, désactivation de sécurité ou installation automatique n'est requis.

## Limites acceptées

Les succès fonctionnels précédents sont établis dans cette instance : Edge français, Kokoro/Whisper hors ligne, rendu 2D et export 3D séquentiel complet, montage mixte H.264/AAC et décodage. Ils ne valent pas encore résultat de restauration du nouveau snapshot.

Le rendu 3D de contrôle est calculé en 640×360 à 12 i/s, puis agrandi pour le montage 1080p. Les 66 sources sont validées, pas leurs 66 démonstrations intégrales. Certains packs optionnels et MP4 de galerie restent absents. Le wrapper TLS est spécifique à edge-tts 7.3.1, et les requirements Python amont ne sont pas tous figés. Ces limites sont documentées et ne bloquent pas la publication de la chaîne testée.
