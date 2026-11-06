# Diagnostic Whisper et Edge TTS — 5 novembre 2026

## Conclusion

Le socle multimédia reste fonctionnel. Whisper et Edge TTS ne sont pas encore opérationnels : leurs destinations sont refusées par le proxy Codex avant connexion TLS aux services. Aucune modification de politique réseau, publication, création de commit ou opération de push n'a été effectuée. Kokoro reste le moteur vocal principal hors ligne.

La correction de sélection du proxy WebSocket est préparée et vérifiée. Elle ne suffit pas à autoriser Edge TTS. La validation réseau demandée à l'utilisateur reste nécessaire pour poursuivre ces deux diagnostics.

## 1. Sources, versions et investigation

Instructions du dépôt et rapports précédents examinés : TECHNIQUE.md, core/README.md, scripts de préparation, core/tts/asr_check.py, implémentation TTS, films/.installation-audit/RAPPORT.md et films/.publication-check/CONTROLE-FINAL.md. Les rapports précédents restent la référence pour les composants non concernés par cette intervention.

Versions constatées : Python 3.12.14, faster-whisper 1.2.1, CTranslate2 4.8.5, huggingface-hub 2.4.0, edge-tts 7.3.1, aiohttp 3.14.5, Kokoro ONNX 0.6.1, ONNX Runtime 1.31.1, Playwright 1.63.0, Chromium 155.0.8059.79, Three.js 0.170.0, FFmpeg 7.1.5. Le contrôle pip check réussit.

Documentation des mainteneurs consultée et conservée localement :

- https://github.com/SYSTRAN/faster-whisper — `faster-whisper-upstream.md` ; CPU int8, modèles compatibles et chargement depuis un répertoire local.
- https://github.com/rany2/edge-tts — `edge-tts-upstream.md` ; client communautaire du service en ligne Microsoft Edge, pas une API Microsoft officiellement garantie.
- Code des bibliothèques installées : sélection de proxy aiohttp, appels HTTPS/WSS Edge et téléchargement Hugging Face.

L'environnement impose le réseau restreint, avec le groupe de domaines des gestionnaires de paquets et aucune destination personnalisée. HTTP_PROXY et HTTPS_PROXY ainsi que la configuration de confiance CA sont présents ; leurs valeurs ne sont pas reproduites. WSS_PROXY était absent. Aucun paramètre TLS n'a été désactivé, aucun miroir ni autre route de téléchargement n'a été utilisé.

## 2. Whisper : cause, solution préparée et limites

**Faits vérifiés.** Lemo utilise faster-whisper, avec CTranslate2 sur CPU et compute_type=int8. `--model` et WHISPER_MODEL acceptent un chemin local. Le modèle par défaut pour le français est `base` multilingue. Les variantes `.en` ne conviennent pas au français. Aucun modèle local n'a été trouvé. Les précédents essais hors ligne échouaient faute de cache.

Le nouvel essai `download_model('small')` échoue avec ProxyError / 403 Forbidden. Une requête indépendante vers `https://huggingface.co/Systran/faster-whisper-small/resolve/main/model.bin` reçoit `CONNECT tunnel failed, response 403`, serveur intermédiaire envoy. Le refus précède la négociation TLS avec Hugging Face ; il ne démontre pas un refus de Hugging Face ni une incompatibilité du modèle.

**Choix proposé, à mesurer.** `Systran/faster-whisper-small`, multilingue, CPU int8. La machine dispose d'un quota de 4 vCPU et d'environ 34 Go de mémoire. Le compromis précision/coût paraît adapté au français ; sa précision et sa vitesse sur cette machine ne sont pas encore testées. Le benchmark CPU publié par les mainteneurs utilise un matériel différent et ne constitue pas une mesure locale. Base reste une alternative plus légère si les mesures le justifient. Les modèles tiny/base/small/medium/large multilingues existent ; l'implémentation n'accepte pas directement un poids OpenAI `.pt` à la place du format CTranslate2.

**Préparation réalisée.** `whisper-model.py` prépare un téléchargement depuis le dépôt du mainteneur, résout une révision précise, vérifie SHA-256 des fichiers LFS et identifiants Git des petits fichiers, puis écrit un manifeste SHA-256 local. S'il existe déjà, le manifeste est vérifié sans nouveau téléchargement. Syntaxe vérifiée ; téléchargement réel et vérification de véritables poids non exécutés à cause du blocage. Aucun modèle factice n'est installé.

Emplacement prévu : `/workspace/models/whisper-small`. Fournir model.bin, config.json, tokenizer.json et les fichiers de vocabulaire/prétraitement présents dans le dépôt du modèle. tokenizer.json évite un téléchargement implicite du tokenizer.

### Procédure après autorisation ou importation approuvée

Sur une machine dont l'accès à la source est autorisé, préparer le modèle avec le même script et les dépendances compatibles :

```sh
python whisper-model.py download /chemin/whisper-small
python whisper-model.py verify /chemin/whisper-small
```

Transférer ensuite le répertoire complet par un mécanisme explicitement autorisé, avec son manifeste et la révision de référence. La provenance du manifeste doit être fiable ; un manifeste fourni avec des fichiers non fiables ne suffit pas à établir leur authenticité. Cette procédure n'a pas été exécutée et ne constitue pas une autorisation de contourner la politique actuelle.

Dans cet environnement, une fois les fichiers disponibles :

```sh
cd /workspace/lemo-opuscar
.venv/bin/python films/.speech-diagnostic/whisper-model.py verify /workspace/models/whisper-small
HF_HUB_OFFLINE=1 .venv/bin/python core/tts/asr_check.py films/.publication-check/lines.json films/.speech-diagnostic/kokoro-offline --lang fr --model /workspace/models/whisper-small
```

Puis répéter avec les connexions réseau interdites, comparer réellement les mots transcrits et tester plusieurs phrases françaises, accents et nombres. La transcription française et sa répétition hors réseau restent **non testées**, faute de poids. Ne pas annoncer une transcription fiable à ce stade.

## 3. Edge TTS : deux obstacles distincts

**Sélection du proxy, cause identifiée.** aiohttp avec trust_env=True trouve HTTPS_PROXY pour HTTPS, mais ne le réutilise pas automatiquement pour `wss://`. Le moteur du dépôt appelle Communicate sans proxy explicite. Avant correction, le sélecteur aiohttp ne trouve aucun proxy WSS. Avec WSS_PROXY défini à partir du HTTPS_PROXY existant, il sélectionne bien ce même proxy.

Correction locale dans `speech-env.sh`, également ajoutée aux instructions de démarrage du brouillon :

```sh
if [ -n "${HTTPS_PROXY:-}" ]; then export WSS_PROXY="$HTTPS_PROXY"; fi
```

Ce réglage n'ajoute aucun domaine et ne désactive pas TLS. Il n'altère ni le code suivi du dépôt ni les protections du service Microsoft.

**Autorisation réseau, blocage restant.** Trois essais séparés avec proxy explicite échouent tous avec ClientHttpProxyError 403 : liste des voix HTTPS, transport WSS et synthèse française fr-FR-DeniseNeural. Une requête curl indépendante confirme le refus CONNECT. Le test WSS brut ne vaut qu'essai de transport ; la tentative avec la bibliothèque utilise le protocole du client installé.

**Non établis à ce stade.** La compatibilité TLS/CA après le tunnel, l'acceptation de la mise à niveau WebSocket, l'acceptation du client par Microsoft et la synthèse finale. Edge utilise notamment un contexte certifi ; il faudra vérifier sa confiance envers la chaîne réellement présentée si le tunnel devient autorisé. Il n'existe actuellement aucune preuve d'un refus du service Microsoft indépendant de Codex. Aucune modification anticipée de certificats, version, jetons ou mécanismes du service n'est justifiée.

Edge TTS reste nécessairement en ligne. Il ne peut pas remplacer Kokoro pour un fonctionnement entièrement hors ligne.

## 4. Configuration réseau minimale soumise à validation

| Domaine exact | Protocole destination | Usage | Durée nécessaire |
|---|---|---|---|
| huggingface.co | HTTPS TCP 443 via proxy existant | Métadonnées, révision et fichiers du modèle Systran | Téléchargement initial seulement ; inutile pour la transcription locale complète |
| speech.platform.bing.com | HTTPS et WSS TCP 443 via proxy existant | Liste des voix et synthèse Edge | À chaque utilisation d'Edge ; accès d'exécution permanent si cette fonction est retenue |

Aucun accès entrant, accès Internet illimité, joker ou changement de proxy n'est demandé. Une redirection éventuelle de Hugging Face vers un domaine de stockage reste inconnue, car le premier tunnel est bloqué. Les deux domaines ci-dessus constituent une première autorisation minimale, pas la garantie d'une liste exhaustive de téléchargement. Tout domaine supplémentaire devra être observé, justifié et soumis séparément à validation avant modification.

La demande d'approbation découle de la phase 4 de la mission de l'utilisateur. Aucune règle n'a été ajoutée. Une sauvegarde de brouillon n'applique pas à elle seule une nouvelle politique au processus courant ; vérifier sa propagation avant de retester.

## 5. Tests fonctionnels après la correction locale

| Test | Résultat vérifié |
|---|---|
| Sélection proxy aiohttp WSS | Même proxy que HTTPS_PROXY après export WSS_PROXY |
| Kokoro français local | WAV 24 kHz, 2,462 s, voix ff_siwis |
| Kokoro avec connexions Python interdites | Nouvelle synthèse réussie ; connect/connect_ex/create_connection remplacés par un refus ; HF_HUB_OFFLINE=1 |
| Chromium système | Version 155.0.8059.79 ; rendus Playwright avec sélecteurs système configurés |
| Rendu 2D | Image 1920×1080 produite ; contenu non uniforme |
| Rendu 3D logiciel | Image 640×360 produite séquentiellement, SwiftShader, environ 5,4 s ; contenu non uniforme |
| Export et mixage FFmpeg | MP4 H.264/AAC, 1920×1080, 24 i/s, 96 images, 4 s, audio 48 kHz |
| Décodage complet export | ffmpeg -v error -xerror : succès |
| Mesure audio de l'export | -13,9 LUFS, pic -1,2 dBFS |
| Cohérence Python | pip check : aucune dépendance cassée |
| Intégrité du dépôt | 2 478 fichiers suivis identiques à la référence SHA-256 ; état Git propre |
| Styles | 66 styles conservés ; répertoire supplémentaire `_template` exclu du décompte des styles |
| Whisper réel / hors ligne | Bloqué : modèle absent |
| Edge français | Bloqué : refus CONNECT 403 |

L'export utilise le mix français déjà validé lors du contrôle précédent ; la voix Kokoro a aussi été régénérée séparément pendant cette mission. Ces tests ne constituent pas un rendu intégral des 66 démonstrations. Le contrôle précédent avait tracé le vrai binaire Chromium pour les moteurs partagés et les deux entrées historiques ; il n'a pas été répété intégralement ici. CRT avait été validé précédemment.

## 6. Persistance et préparation à la publication

Kokoro et ses voix restent dans core/tts/, les dépendances dans .venv et node_modules. Les scripts et preuves de cette mission sont sous films/.speech-diagnostic/, ignoré par Git. Le script d'installation déjà sauvegardé préserve les actifs présents et télécharge les actifs Kokoro vérifiés uniquement s'ils manquent. Les instructions réutilisables ont été complétées avec le réglage WSS, les blocages et la procédure Whisper ; sauvegarde du brouillon confirmée, sans publication ni application réseau.

Les dépendances Python amont ne sont pas entièrement figées : le relevé python-freeze.txt de l'audit décrit l'installation testée, sans garantir qu'une réinstallation future résoudra les mêmes versions. Le snapshot préparé contient l'installation actuelle. Le modèle Whisper ne peut pas encore faire partie d'un snapshot fonctionnel puisqu'il n'est pas installé. Ne définir WHISPER_MODEL qu'après les vérifications effectives.

La restauration définitive des modèles, scripts et dépendances devra être testée dans une nouvelle tâche après une publication explicitement autorisée. Aucun téléchargement de modèle ne doit être nécessaire au démarrage normal d'une tâche après préparation complète.

**État final :** socle multimédia prêt à être présenté pour validation, Whisper et Edge indisponibles. La résolution réseau et les essais associés attendent l'accord demandé. L'environnement n'est pas publié.

## Preuves conservées

- `probes.json`, `probe.py` : reproduction des quatre échecs réseau.
- `whisper-connect.txt`, `edge-connect.txt` : erreurs CONNECT indépendantes.
- `integrity.json` : comparaison SHA-256 et inventaire des styles.
- `2d/`, `3d/`, `kokoro/`, `kokoro-offline/`, `regression.mp4` : sorties fonctionnelles.
- `speech-env.sh`, `whisper-model.py` : préparation locale non suivie.
- Documentation des mainteneurs téléchargée depuis leurs dépôts GitHub.
