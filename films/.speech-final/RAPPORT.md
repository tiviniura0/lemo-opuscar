# Finalisation Whisper et Edge TTS — 5 novembre 2026 (Tahiti)

## Résultat

Whisper small multilingue est installé, son intégrité est vérifiée et la transcription française de contrôle réussit. Edge TTS produit une synthèse française valide après intégration de l'autorité de confiance fournie par Codex dans ses contextes TLS. Aucun fichier suivi, style, commit ou branche n'a été modifié. Aucune publication ni aucun push n'a été effectué.

Les essais en ligne sont terminés. La dernière observation de la session indique encore `unrestricted/enforced`, connectée, révisions demandée et observée 2. Le retour au mode restrictif a été demandé à l'utilisateur. Les vérifications spécifiquement demandées **après** ce retour restent en attente ; elles ne doivent pas être confondues avec les tests locaux déjà réussis.

## 1. Réseau confirmé avant connexion

L'état officiel indiquait observations_current=true, connectivity=connected et network_policy={mode:unrestricted,state:enforced}. Le brouillon était en révision 8, mode unrestricted. Le fichier de politique au démarrage indiquait également unrestricted. La lecture HTTPS des métadonnées officielles Hugging Face a répondu 200.

Toutes les requêtes sont passées par le proxy fourni. Aucun contournement, miroir, désactivation TLS ou changement des règles réseau n'a été utilisé. Le passage temporaire au mode public a été effectué et autorisé par l'utilisateur.

## 2. Modèle Whisper et intégrité

- Implémentation : faster-whisper 1.2.1 / CTranslate2 4.8.5, CPU int8.
- Source du mainteneur : https://huggingface.co/Systran/faster-whisper-small
- Révision figée : `536b0662742c02347bc0e980a01041f333bce120`.
- Emplacement : `/workspace/models/whisper-small`.
- Fichiers : config.json, model.bin, tokenizer.json, vocabulary.txt et verified-manifest.json local.
- Poids model.bin : 483 546 902 octets.
- SHA-256 officiel des poids : `3e305921506d8872816023e4c273e75d2419fb89b24da97b4fe7bce14170d671`.

Précision historique : aucune révision précise n'avait pu être obtenue lors des essais précédents bloqués par HTTP 403. Celle ci-dessus a été identifiée dans les métadonnées officielles pendant cette mission, puis utilisée explicitement dans chaque URL de téléchargement. Aucun téléchargement flottant depuis `main` n'a été utilisé pour les fichiers.

Les tailles et le SHA-256 LFS ont été vérifiés pour les poids. Les identifiants Git blob publiés ont été vérifiés pour les petits fichiers, puis leurs SHA-256 ont été enregistrés et figés dans verify-whisper.py. Un second contrôle local de tous les fichiers a réussi. Le modèle est multilingue, pas une variante `.en`.

Redirections observées : HTTP 307 sur huggingface.co pour les petits fichiers, HTTP 302 vers `us.aws.cdn.hf.co` pour les poids. Le script n'accepte que ces deux hôtes, en HTTPS sur le port 443. Les URL signées ne sont pas reproduites. Aucune règle CDN n'a été ajoutée à la configuration ; ce domaine était accessible pendant la fenêtre publique autorisée. Il ne sera pas nécessaire à l'exécution hors ligne.

## 3. Transcription réelle et rechargement local

Le script du dépôt core/tts/asr_check.py a traité le WAV français réellement généré par Kokoro, avec `--lang fr --model /workspace/models/whisper-small`, CPU int8 et HF_HUB_OFFLINE=1.

Texte attendu : « Bonjour, la synthèse vocale fonctionne. »

Texte transcrit : « Bonjour, la synthèse vocale fonctionne. »

Résultat : `mismatches: 0`, code de sortie 0.

Un second processus a rechargé le modèle depuis le même répertoire avec HF_HUB_OFFLINE=1 et les connexions Python socket.connect, connect_ex et create_connection remplacées par un refus. La transcription a de nouveau correspondu exactement, code 0. Cela valide le chargement et la transcription locale sans téléchargement dans ce test ; la politique globale de la session était encore publique. Le test supplémentaire après restauration du réseau restrictif reste à exécuter.

Cette validation porte sur une phrase de contrôle. Elle ne constitue pas une mesure de précision sur un corpus français varié ni une validation d'enregistrements humains bruités.

## 4. Edge TTS : diagnostic corrigé et synthèse réussie

Avec le tunnel réseau désormais autorisé, les appels de la bibliothèque edge-tts 7.3.1 échouaient initialement avec ClientConnectorCertificateError. Son code crée deux contextes SSL à partir de certifi, sans reprendre automatiquement le magasin d'autorités fourni par SSL_CERT_FILE dans Codex.

Un test de transport WSS avec le contexte TLS système a obtenu HTTP 401 : le tunnel et TLS fonctionnaient, mais cette requête nue ne contenait pas le protocole complet du client. Ce résultat n'était pas un refus CONNECT 403 du proxy et ne suffisait pas à valider la synthèse.

Correction ciblée : ajout, via load_verify_locations, de l'autorité déjà fournie par Codex aux deux contextes SSL du client. CERT_REQUIRED et check_hostname restent activés. Pour WSS, le helper utilise le HTTPS_PROXY existant via WSS_PROXY. Aucun fichier de la bibliothèque, fichier suivi du projet, jeton, mécanisme de protection du service ou certificat distant n'a été modifié.

Après correction :

- Liste des voix HTTPS : 322 voix, dont fr-FR-DeniseNeural.
- Synthèse française par le véritable client et son protocole WSS : succès.
- Script réutilisable retesté séparément : edge-with-platform-ca.py.
- Sortie : edge-wrapper-fr.mp3, 24 480 octets, MP3 mono à 24 kHz, durée 4,080 s.
- Décodage complet FFmpeg : succès, aucune erreur.

Le helper utilise les contextes internes de edge-tts 7.3.1 : revalider cette intégration lors d'une mise à niveau. La correction n'est pas automatiquement appliquée à tous les scripts historiques du dépôt ; utiliser le wrapper testé, ou sa fonction configure() avant les appels à la bibliothèque dans un helper local.

Edge reste un moteur en ligne optionnel. Kokoro demeure le moteur principal hors ligne. Après rétablissement du réseau restreint, conserver `speech.platform.bing.com` pour HTTPS/WSS 443 si Edge doit rester disponible, puis vérifier son accès effectif. Aucun accès Hugging Face n'est nécessaire au modèle déjà installé.

## 5. Persistance et configuration préparée

Le modèle complet est présent sous /workspace/models/whisper-small. Les dépendances existantes dans .venv et node_modules sont conservées. Aucun paquet n'a été réinstallé ou mis à niveau.

Les instructions de démarrage et le script d'installation du brouillon ont été mis à jour sans toucher aux paramètres réseau. Le démarrage utilise WHISPER_MODEL=/workspace/models/whisper-small et le helper Edge avec confiance TLS Codex. Le script de préparation vérifie le modèle local ; il échoue si les fichiers manquent ou sont altérés, sans téléchargement implicite. Le script de réacquisition séparé reste figé sur la révision vérifiée et nécessite un accès autorisé à la source et à son CDN.

Fichiers réutilisables : prepare-whisper.py, model-metadata.json, verify-whisper.py, edge-with-platform-ca.py, offline-python.py et check-restricted.sh. Ils résident dans films/.speech-final/, ignoré par Git, et doivent être conservés avec le snapshot préparé.

La présence actuelle ne prouve pas la restauration dans une future tâche. Cette restauration devra être testée après une publication explicitement autorisée. Aucun service permanent n'est requis, aucun téléchargement de modèle ne doit avoir lieu à chaque tâche.

## 6. Contrôles restants après retour au mode restrictif

Ne lancer check-restricted.sh qu'après confirmation `restricted/enforced` et session connectée. Le script prépare successivement :

1. Vérification locale du modèle Whisper.
2. Nouvelle synthèse Kokoro française avec connexions Python interdites.
3. Nouvelle transcription Whisper de ce WAV avec connexions Python interdites.
4. Rendus Chromium 155/Playwright 2D et 3D logiciel séquentiel.
5. Export MP4 1080p H.264/AAC avec le nouveau WAV, puis décodage intégral.
6. pip check.

Le script est préparé et sa syntaxe shell vérifiée, mais cette série n'a pas encore été exécutée après restauration restrictive. Les tests similaires des audits précédents ne sont pas présentés comme des résultats nouveaux.

## Preuves

- model-metadata.json : métadonnées de la source vérifiée.
- download-redirects.json : hôtes des redirections observées.
- /workspace/models/whisper-small/verified-manifest.json : empreintes locales.
- edge-results.json : échecs TLS initiaux et test WSS sans authentification applicative.
- edge-platform-ca-results.json : succès après correction de confiance.
- edge-wrapper-fr.mp3 : synthèse du wrapper réutilisable.
- integrity.json : contrôle des 2 478 fichiers suivis et des 66 styles.
