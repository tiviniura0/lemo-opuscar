# Validation finale Lemo-Opuscar V2 — 5 novembre 2026, Tahiti

La validation fonctionnelle de la session actuelle est réussie sous réseau restrictif. L'environnement est préparé pour la décision finale de l'utilisateur, mais n'est pas publié. La restauration dans une nouvelle tâche après publication reste à vérifier.

## Réseau effectivement appliqué

Contrôlé avant les tests puis à leur issue avec l'outil officiel environment_status : session connectée, observations_current=true, mode restricted, état enforced, révision demandée 4 et observée 4. L'accès Internet public illimité est désactivé.

Les domaines personnalisés actifs sont exactement huggingface.co et speech.platform.bing.com. Ils correspondent au brouillon enregistré, révision 11 lors de la lecture initiale. Le préréglage package_managers correspond également ; il autorise d'autres destinations de gestion de paquets. Le réseau n'est donc pas limité à deux domaines au total. Aucune règle réseau n'a été modifiée pendant cette validation.

Hugging Face n'est plus nécessaire pour exécuter Whisper localement, mais reste autorisé conformément aux paramètres enregistrés par l'utilisateur. Le CDN us.aws.cdn.hf.co utilisé pour l'acquisition précédente n'a pas été ajouté. Aucun modèle ni paquet n'a été téléchargé pendant cette validation.

Le fichier /etc/codex/network-policy.json est un instantané de démarrage : sa liste ne contenait pas le domaine Edge, alors que l'état officiel courant le confirmait et que la synthèse réelle réussissait. Les conclusions ci-dessus reposent sur l'état courant et les essais effectifs, pas sur cet instantané ancien.

## Résultats des tests de cette exécution

| Composant | Résultat réel | Limite ou précision |
|---|---|---|
| Whisper small multilingue | Intégrité des quatre fichiers vérifiée ; modèle chargé depuis /workspace/models/whisper-small | Révision 536b0662742c02347bc0e980a01041f333bce120 |
| Transcription française hors ligne | Phrase attendue et transcrite identiques ; mismatches: 0 ; code 0 | WAV réel synthétisé par Kokoro ; une phrase de contrôle, pas un corpus d'évaluation |
| Kokoro français hors ligne | Voix ff_siwis, WAV PCM signé 16 bits, mono, 24 kHz, 2,4615 s | Fichier nouvellement généré pendant cette exécution |
| Isolation des tests Python hors ligne | HF_HUB_OFFLINE=1 ; socket.connect, connect_ex et create_connection remplacés par un refus | Contrôle applicatif des connexions Python, pas un espace réseau système séparé |
| Décodage Kokoro | FFmpeg -v error -xerror : succès | Aucun téléchargement nécessaire |
| Edge TTS français | MP3 mono, 24 kHz, 4,080 s, 24 480 octets ; décodage complet réussi | Moteur en ligne ; wrapper avec proxy et autorité Codex, TLS vérifié |
| Chromium avec Playwright | Playwright 1.63.0 lance Chromium 155.0.8059.79 | Binaire réel confirmé : /usr/lib/chromium/chromium ; override /usr/bin/chromium |
| Rendu 2D | Image 1920×1080 produite ; contenu non uniforme vérifié | Fixture graphique du projet |
| Rendu 3D logiciel | Image 640×360 produite, SwiftShader, environ 6,7 s ; contenu non uniforme | Exécution séquentielle ; performances CPU limitées |
| Export vidéo avec voix française | MP4, H.264, 1920×1080, 24 i/s, 96 images, 4 s | Voix Kokoro générée pendant cette validation |
| Piste audio du MP4 | AAC mono 48 kHz ; mixage -14,0 LUFS, pic -1,2 dBFS | WAV complété par silence jusqu'à 4 s |
| Décodage vidéo complet | FFmpeg -v error -xerror : succès | Pas seulement une lecture des métadonnées |
| Dépendances Python | pip check : aucune dépendance cassée | Aucun paquet modifié |
| Styles | 66 styles présents et inventaire identique | Répertoire _template exclu ; pas un rendu intégral des 66 démonstrations |
| Intégrité des sources | 2 478 fichiers suivis identiques à la référence SHA-256 ; liste suivie inchangée | Git propre, HEAD bebbbe1aa92a3cb4bb6f83500e61b23a17d1aa00 |
| Scripts réutilisables | Installation et vérification restrictive : syntaxe shell valide ; commandes de validation exécutées avec succès | Réinstallation complète non relancée pour éviter une résolution inutile des dépendances |

Phrase transcrite : « Bonjour, la synthèse vocale fonctionne. »

## Modèles et persistance

Présents sur la machine préparée :

- /workspace/models/whisper-small/model.bin : 483 546 902 octets, SHA-256 3e305921506d8872816023e4c273e75d2419fb89b24da97b4fe7bce14170d671 ; config.json, tokenizer.json, vocabulary.txt et manifeste local présents et vérifiés.
- core/tts/kokoro-v1.0.onnx : 325 532 387 octets, SHA-256 7d5df8ecf7d4b1878015a32686053fd0eebe2bc377234608764cc0ef3636a6c5.
- core/tts/voices-v1.0.bin : 28 214 398 octets, SHA-256 bca610b8308e8d99f32e6fe4197e7ec01679264efed0cac9140fe9c29f1fbf7d.
- .venv, node_modules, helpers sous films/.speech-final/ et fixtures utilisées.

Les scripts d'installation et de démarrage sont sauvegardés dans le brouillon. La vérification Whisper n'effectue aucun téléchargement ; si les fichiers sont absents ou altérés, elle échoue explicitement. Les instructions de démarrage définissent les sélecteurs Chromium et le chemin local Whisper. Le wrapper Edge ajoute la confiance CA fournie par Codex sans désactiver la validation TLS.

Une réinstallation depuis les requirements non entièrement figés peut résoudre d'autres versions : le snapshot de l'installation testée doit être distingué d'une reconstruction future. Le relevé de versions et les anciens audits sont conservés.

La validation actuelle confirme la présence et le fonctionnement des actifs sur cette machine. Elle ne confirme pas leur restauration depuis un snapshot publié. Cette dernière vérification devra être réalisée dans une nouvelle tâche, après publication explicitement autorisée.

## Limites conservées

- Edge TTS dépend du service distant et de speech.platform.bing.com. Le helper utilise des attributs de contexte TLS internes à edge-tts 7.3.1 ; il devra être revalidé après mise à niveau. Les scripts historiques qui ne passent pas par ce helper ne reçoivent pas automatiquement sa correction TLS.
- Le Chromium système testé diffère de la version normalement associée à Playwright 1.63.0. Les opérations représentatives demandées fonctionnent ; cela ne garantit pas toute API navigateur possible.
- Le rendu 3D utilise le CPU ; conserver une exécution séquentielle et un seul worker pour les premières productions.
- Certains packs d'instruments optionnels, dépendances propres à certains styles et vidéos de galerie restent à installer selon le projet choisi, comme documenté dans l'audit initial.

## Preuves de cette validation

- restricted-validation.log : exécution complète audio hors ligne, rendus, export, décodage et pip check.
- restricted-integrity.json : empreintes, fichiers suivis et inventaire des styles.
- restricted-chromium.json : version et chemin du vrai binaire lancé par Playwright.
- kokoro-restricted/french.wav et words.json : voix française et transcription horodatée.
- edge-restricted-fr.mp3 : synthèse française via réseau limité.
- 2d-restricted/t_0.jpg et 3d-restricted/t_0.jpg : rendus.
- regression-restricted.mp4 : export final vérifié.
- install-saved-final.sh : copie locale du script d'installation relu et vérifié syntaxiquement.

Aucune publication, aucun commit ni push n'a été effectué. L'accord final de l'utilisateur reste requis pour publier.
