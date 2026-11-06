# Suite de l'autorisation réseau — 5 novembre 2026, Tahiti

## Configuration enregistrée, pas encore appliquée

L'utilisateur a explicitement autorisé huggingface.co pour le téléchargement initial Whisper et speech.platform.bing.com pour Edge TTS. L'ajout des deux seuls domaines personnalisés est enregistré dans le brouillon, révision 6. Le mode reste restreint, les préréglages des gestionnaires de paquets sont préservés. Aucun domaine supplémentaire, joker, secret, accès illimité ou publication n'a été ajouté.

L'outil de configuration expose des règles par nom d'hôte ; il ne propose pas de contrôle par port, chemin, objectif ou expiration. Les essais ont été limités à HTTPS/WSS sur le port 443, via le proxy existant. L'usage temporaire de Hugging Face est documenté : retirer cette règle après acquisition et validation du modèle, sans supprimer ses fichiers locaux.

Après sauvegarde et après les tests locaux, l'état de la machine rapporte toujours observations_current=true, politique restricted/enforced, révision active 1 et allowed_hosts=[] pour les domaines personnalisés. La sauvegarde du brouillon n'a donc pas appliqué les nouveaux domaines à la session. L'outil disponible confirme explicitement qu'il sauvegarde sans appliquer ni publier ; aucun outil d'application directe au runtime n'est disponible dans cette session.

**Action nécessaire : enregistrer les changements réseau dans les paramètres de l'environnement pour demander leur application à la session, sans publier.** L'autorisation des deux domaines est déjà acquise : aucune nouvelle approbation de ces mêmes domaines n'est demandée. Attendre l'application effective avant de reprendre les opérations bloquées.

## Essais réseau réalisés après sauvegarde

| Essai | Résultat |
|---|---|
| Métadonnées du dépôt officiel Systran/faster-whisper-small sur huggingface.co | Tunnel CONNECT refusé, HTTP 403 |
| En-têtes du fichier model.bin, sans suivre les redirections | Tunnel CONNECT refusé, HTTP 403 |
| Liste des voix Edge avec proxy explicite | ClientHttpProxyError, HTTP 403 |
| Synthèse fr-FR-DeniseNeural avec proxy explicite | ClientHttpProxyError, HTTP 403 ; aucun audio valide |

Les résultats sont conservés dans network-results.json. Ces refus précèdent la connexion TLS aux services ; ils ne démontrent aucun refus distant de Hugging Face ou Microsoft. Aucune redirection n'est observable : le premier tunnel échoue. Aucun autre domaine n'a été ajouté ou utilisé comme route de substitution.

Un premier outil de diagnostic supposait le module `httpx` présent et s'est arrêté avant toute requête. La distribution huggingface-hub 2.4.0 installée dépend de `httpx2`. Le diagnostic a été corrigé pour utiliser urllib de la bibliothèque standard ; aucune installation ou modification des dépendances n'a été nécessaire.

## Whisper : éléments encore bloqués

Le modèle small multilingue n'a pas pu être téléchargé. Il n'y a donc ni poids dont vérifier l'intégrité, ni transcription française réelle, ni essai de transcription entièrement hors ligne à rapporter. Le chemin /workspace/models/whisper-small/model.bin est absent.

Le script préparé lors du diagnostic précédent, films/.speech-diagnostic/whisper-model.py, prévoit un téléchargement du modèle CTranslate2 du mainteneur, une révision précise et une vérification des sommes du fournisseur. Il reste non validé avec de vrais poids. Avant de l'exécuter après application réseau, inspecter les redirections sans les suivre ; tout nouveau domaine doit être présenté à l'utilisateur et autorisé séparément. Ne pas utiliser un miroir, modifier les paramètres du proxy ou désactiver TLS.

Après acquisition approuvée et vérification, conserver les fichiers complets sous /workspace/models/whisper-small, y compris tokenizer.json et la configuration. Tester le texte français, puis refaire le test avec connexions interdites et HF_HUB_OFFLINE=1. Ne définir WHISPER_MODEL vers ce chemin qu'après réussite. Aucun téléchargement à chaque nouvelle tâche ne sera nécessaire pour une installation locale complète, mais cela reste à démontrer ici.

## Non-régression : nouvelles exécutions réussies

- Kokoro ff_siwis : nouvelle phrase française « Bonjour, la synthèse vocale fonctionne. », WAV 24 kHz, 2,462 s. HF_HUB_OFFLINE=1 et connexions Python connect/connect_ex/create_connection interdites pendant la synthèse.
- Chromium 155.0.8059.79 utilisé avec les sélecteurs système du projet et Playwright ; image 2D 1920×1080 produite.
- Rendu Three.js 3D 640×360 séquentiel par SwiftShader réussi, environ 4,3 s.
- Nouvelle vidéo de 96 images, 24 i/s ; mixage avec la voix française générée pendant cette exécution.
- MP4 1920×1080, 4 s, vidéo H.264, audio AAC 48 kHz ; décodage intégral FFmpeg sans erreur. Mesure audio : -14,0 LUFS, pic -1,2 dBFS.
- pip check : aucune dépendance cassée.
- Les 2 478 fichiers suivis correspondent à la référence SHA-256 ; liste suivie inchangée, Git propre. Les 66 styles sont conservés, hors répertoire de modèle `_template`.

Ces contrôles n'équivalent pas à un nouveau rendu intégral des 66 démonstrations.

## Modèles, dépendances et persistance

Présents et utilisés dans la machine préparée : .venv, node_modules, modèle Kokoro core/tts/kokoro-v1.0.onnx (325 532 387 octets), voix core/tts/voices-v1.0.bin (28 214 398 octets), scripts de préparation et fixtures. Leurs empreintes locales sont enregistrées dans integrity.json ; le contrôle de provenance du pack Kokoro avait déjà été effectué pendant l'installation officielle.

Versions revérifiées : faster-whisper 1.2.1, huggingface-hub 2.4.0, CTranslate2 4.8.5, edge-tts 7.3.1, aiohttp 3.14.5, kokoro-onnx 0.6.1, onnxruntime 1.31.1 (versions.json). Les scripts d'installation et de démarrage restent sauvegardés ; les instructions précisent l'autorisation acquise, la limitation des domaines, le proxy WSS existant et l'interdiction de publication automatique.

Whisper est absent et ne peut pas être annoncé comme inclus dans un snapshot fonctionnel. Edge nécessite son service distant à chaque synthèse ; sa bibliothèque seule ne garantit pas son fonctionnement. Kokoro reste le moteur principal hors ligne.

La présence actuelle des actifs est confirmée. Leur restauration dans une nouvelle tâche ne pourra être confirmée qu'après une publication explicitement autorisée et un test distinct. Aucun commit, push ou publication n'a été effectué.

## Fichiers de preuve

- network-results.json : résultats des connexions après sauvegarde.
- versions.json et integrity.json : versions, actifs locaux et intégrité du dépôt.
- kokoro/french.wav, 2d/t_0.jpg, 3d/t_0.jpg et regression.mp4 : sorties produites pendant ce contrôle.
- ../.speech-diagnostic/RAPPORT.md : diagnostic précédent et méthode de préparation du modèle.
