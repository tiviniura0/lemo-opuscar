# Rapport de vérification de l’installation — lemo-opuscar-v2

Date : 5 novembre 2026, fuseau Pacific/Tahiti.
Dépôt inspecté : `tiviniura0/lemo-opuscar`, branche `main`, commit local `bebbbe1aa92a3cb4bb6f83500e61b23a17d1aa00`.
Répertoire : `/workspace/lemo-opuscar`.

## Conclusion et portée

Le socle de production fonctionne : rendu Canvas 2D, WebGL2/Three.js, effets CRT, profondeur de champ et occlusion ambiante, synthèse vocale Kokoro, musique procédurale, échantillonnage et export MP4 avec voix. L’installation complète de toutes les fonctions ne peut pas être déclarée validée : le navigateur exactement associé à Playwright et le modèle Whisper sont bloqués au téléchargement ; le service Edge TTS est inaccessible par la politique réseau.

La première réponse était trop générale : elle validait uniquement les dépendances de base et un test graphique court. Elle ne constituait pas une validation de Kokoro, de la transcription ou de chacun des 66 styles. Cet audit apporte ces distinctions et étend les essais.

Aucune publication d’environnement, aucun déploiement GitHub Pages, aucun push ni changement du code applicatif n’a été effectué. Votre validation explicite reste nécessaire avant publication. Les champs `install_script` et `start_skill` ont été corrigés et sauvegardés uniquement dans le brouillon ; cette sauvegarde ne publie pas et ne modifie pas la politique réseau.

## Documentation et procédure de référence

Lecture intégrale des instructions techniques de `TECHNIQUE.md`, `core/README.md`, `plugin/skills/lemo-opuscar/SKILL.md` et du script `plugin/skills/lemo-opuscar/scripts/setup.sh`. Lecture des instructions d’installation/configuration des README anglais et chinois, d’AGENTS.md, des guides DIRECTOR/MAINTAINING, des scripts de récupération des ressources et de la procédure alternative de l’édition « directory ». Examen des quatre fichiers requirements, de tous les manifestes npm, du verrou npm, du workflow Pages et des exigences d’installation particulières recensées dans les 66 STYLE.md. Le fichier `style-requirements.json` conserve les paragraphes relatifs aux paquets supplémentaires.

Le dépôt offre deux voies : clone ou plugin Claude. La voie clone existante est adaptée à cet environnement ; installer Claude Code ou créer un second clone n’est pas nécessaire pour exécuter ses outils Node/Python.

La procédure officielle installe par niveaux :

1. Base : Node >=20, Python >=3.11, FFmpeg >=7, npm, Chromium headless, requirements.txt.
2. Voix : requirements-voice.txt, modèle Kokoro et fichier de voix ; Whisper téléchargé lors de la première transcription.
3. Musique : requirements-music.txt / numba pour pluck.py.
4. Ressources : packs HDRI, banques d’instruments et polices selon le film.
5. Dépendances spécifiques à un style : environnement privé dans le projet, sans les mélanger au venv central.

## Comparaison avec les actions exécutées

| Étape officielle | Première installation | Audit et résultat actuel |
|---|---|---|
| Utiliser le clone existant | Oui | Même clone, même commit, aucune réinitialisation |
| npm via le script officiel | `npm ci`, plutôt que `npm install` | Écart volontaire pour préserver le verrou ; versions identiques au lockfile |
| Chromium correspondant à Playwright | Non, Chromium système choisi par PLAYWRIGHT_CHROME | Installation officielle tentée, refus HTTP 403 ; solution système testée et conservée |
| Python / venv / base | Oui | Imports, calcul audio, images et `pip check` validés |
| Voix Kokoro | Non, niveau optionnel non installé | Niveau installé, modèle SHA-256 vérifié, synthèses anglaise et française exécutées |
| Transcription Whisper | Non | Paquet installé ; modèle bloqué, commande officielle exécutée et sortie 2 |
| Musique numba | Non | Niveau installé ; les 11 presets de pluck.py produisent un signal fini non silencieux |
| HDRI / instruments | Non | Deux HDRI et banque Karoryfer installés avec contrôles SHA-256 ; erhu échantillonné testé |
| Marqueurs du script officiel | Absents | Marqueurs synchronisés après validation des paquets ; invocation informative du script sans avertissement |
| Contrôles fonctionnels | 2 s / 640×360 + audio procédural | Graphisme 1080p, effets avancés, voix réelle, export 4 s, 24 fps, décodage complet |

Le premier échec réseau de l’installation provenait des permissions réseau de la commande isolée : l’exécution avec l’autorisation adaptée a permis npm/PyPI/Git via le proxy configuré. Les refus 403 ultérieurs de Chromium/Whisper/Edge sont des refus de domaines, différents de ce premier problème. Ni le proxy ni TLS ni les sommes de contrôle n’ont été contournés.

## Versions constatées

| Composant | Exigence du dépôt | Version / état vérifié |
|---|---|---|
| Node.js | >=20 | 24.22.1, conforme |
| Python | >=3.11 ; Kokoro 3.11–3.13 | 3.12.14, conforme |
| FFmpeg / ffprobe | >=7 | 7.1.5, conforme ; H.264/libx264 et AAC fonctionnent |
| Playwright Core | ^1.63.0, lock 1.63.0 | 1.63.0, conforme |
| Chromium Playwright | 153.0.8010.12 / revision 1243 | Non installé, téléchargement refusé |
| Chromium système | Exécutable alternatif documenté | 155.0.8059.79, testé ; écart de version assumé, pas une équivalence garantie |
| Three.js | ^0.170.0 / r170 | 0.170.0, conforme |
| Kokoro ONNX | requirements non épinglé | 0.6.1, modèle kokoro-v1.0.onnx et voices-v1.0.bin disponibles |
| ONNX Runtime / eSpeak loader | Dépendances Kokoro | 1.31.1 / 0.2.4 ; inférence réussie ; chemin eSpeak 89 octets, inférieur à la limite 160 |
| edge-tts | Niveau voix | 7.3.1 installé, service distant bloqué |
| faster-whisper | Niveau voix | 1.2.1 installé, modèle absent |
| PyAV | <19 | 18.1.0, contrainte respectée |
| numba / llvmlite | Niveau musique | 0.68.1 / 0.50.0, JIT fonctionnel |
| numpy / scipy | Base, non épinglées | 2.5.4 / 1.18.1 |
| soundfile / soxr | Base | 0.14.0 / 1.1.0 |
| Pillow / fonttools | Base | 13.0.0 / 4.68.0 |

L’inventaire complet est dans `python-freeze.txt` et `versions.json`. Les versions Python ne sont pas épinglées par le projet : une installation future depuis les seuls requirements peut résoudre des versions différentes. Les paquets système étaient déjà présents ; ils n’ont pas été remplacés.

## Essais fonctionnels réellement exécutés

| Essai | Résultat et limite |
|---|---|
| npm ls et imports Playwright / Three | Versions conformes ; aucune dépendance npm manquante |
| pip check après installation | Succès, aucune exigence cassée |
| Réexécution du script complet réutilisable | Succès ; journal `logs/install-repeat.log` |
| Script officiel, mode informatif | Succès, `LIB=/workspace/lemo-opuscar` |
| Canvas 2D | Deux images distinctes, non uniformes, 1920×1080 |
| CRT WebGL2 (`core/post/crt.js`) | Deux images distinctes non uniformes, 640×360, shaders compilés |
| Three.js et `core/three/post.js` | Images 640×360 avec supersampling ×2, GTAO, profondeur de champ et bloom ; image inspectée visuellement |
| Performance 3D | Environ 8,8–9,3 s par image de capture avancée ; SwiftShader CPU, pas de validation GPU matériel |
| Événements | `events.mjs` exporte un événement et une durée de 4 s |
| Temps de lecture | `readcheck.mjs` passe : texte « OK » visible 4 s pour 1,63 s requise |
| Kokoro anglais | « The sun is shining today. », af_bella, 24 kHz, 1,428 s |
| Kokoro français | « Bonjour, la synthèse vocale fonctionne. », ff_siwis, 24 kHz, 2,462 s |
| Qualité numérique des deux WAV | Valeurs finies, signal non silencieux ; crêtes 0,652 et 0,618 ; pas de validation perceptive humaine ni de transcription réussie |
| Musique physique | 11/11 presets testés sur une note, sans NaN/Inf et non silencieux ; cela ne valide pas tous les paramètres musicaux |
| Échantillonneur | Note d’erhu Karoryfer synthétisée et exportée ; autres instruments non testés individuellement |
| Sous-titres | srt.py exporte une cue française avec ses temps |
| Encodage vidéo | 96 images, 1920×1080, 24 fps, durée 4,000 s, H.264 |
| Mix voix et vidéo | MP4 final avec AAC 48 kHz ; normalisation en deux passes : −13,9 LUFS, LRA 2,4, crête −1,2 dBFS |
| Décodage final | FFmpeg avec `-xerror`, toutes les pistes décodées, sortie 0 |
| Images noires | blackdetect sur 96 images, aucun intervalle noir détecté |
| Galerie locale | `python3 styleboard/build.py --site _site` réussit : 66 styles ; aucun déploiement |
| Intégrité | SHA-256 des 2 478 fichiers suivis inchangés, `git status --short` vide |

Les fichiers de tests sont isolés dans `films/.installation-audit/` et restent ignorés par Git. Les tests de base antérieurs sont dans `films/.environment-smoke/`. Aucun test trivial n’a été substitué à une suite officielle : le package racine n’expose pas de commande npm test ; certains manifestes de démonstration contiennent seulement le placeholder « no test specified ».

## Ressources et fonctions qui restent indisponibles ou non validées

**Blocages réseau confirmés :**

- Chromium associé à Playwright : `node node_modules/playwright-core/cli.js install chromium-headless-shell` échoue, sortie 1, HTTP 403 « Domain forbidden » sur `cdn.playwright.dev`. Le navigateur système permet les tests, mais ne garantit pas tous les comportements de la version attendue.
- Whisper : `core/tts/asr_check.py ... --lang auto --model base` échoue, sortie 2, `ProxyError: 403 Forbidden`. Le modèle n’a pas pu être récupéré depuis Hugging Face. L’exactitude du texte prononcé n’est donc pas certifiée automatiquement.
- Edge TTS : une requête en lecture pour la liste des voix à `speech.platform.bing.com` est refusée dès CONNECT, HTTP 403. Aucun texte de narration n’a été envoyé à ce service et aucune synthèse Edge n’est déclarée réussie.

Pour lever ces blocages, les paramètres réseau devront autoriser les destinations nécessaires, d’abord `cdn.playwright.dev`, `huggingface.co`, et `speech.platform.bing.com` si les voix Edge sont souhaitées. Des hôtes de redirection/CDN supplémentaires peuvent être révélés lors du prochain téléchargement ; leur nécessité n’est pas présumée validée. Aucune liste réseau n’a été remplacée ou élargie pendant cet audit. Aucun secret manquant n’est établi pour ces tests.

**Dépendances à installer selon le style et le film, conformément au dépôt :**

- LiDAR : laspy, lazrs, scikit-image, brotli et ses données dans un environnement privé au projet.
- Microscope : tifffile, imagecodecs ; certains formats requièrent OpenSlide et openslide-python.
- Teardown : occt-import-js dans un node_modules privé au projet.
- Briefing Board : modèle BiRefNet facultatif pour le détourage automatique ; alternative polygonale documentée. La présence d’ONNX Runtime pour Kokoro n’installe pas ce modèle.
- Projections et satellite : éventuels pyproj, shapely ou rasterio selon les données, pas requis pour tous les films.
- Banques non installées : VSCO 2 CE, VCSL, FreePats et Salamander. Elles restent téléchargeables par la procédure officielle ; pas de validation de leurs instruments dans cet audit.
- Polices spécifiques, photos, archives, scans, CAD et données propres aux démonstrations ne sont pas tous livrés dans Git ; ils se récupèrent selon chaque film. Les polices de base sont conservées.
- requirements-dev.txt / librosa n’a pas été installé : il sert à reconstruire l’index des instruments pour la maintenance, pas au pipeline de rendu testé.
- Certains anciens exemples utilisent des outils macOS ou des voix externes (par exemple `say`) : ils ne sont pas reproduits à l’identique sous Linux. Ne pas confondre la disponibilité d’un style avec la reconstruction de sa bande-son de démonstration.

**Galerie et 66 styles :**

Les 66 métadonnées, STYLE.md, DEMO.md et points d’entrée demo/index.html sont présents et inchangés. Le catalogue contient 66 styles. La galerie construite référence 67 vidéos, avec OPUSCAR 98 ; ces MP4 de Releases sont absents localement. Ce n’est pas une suppression de styles. Leur lecture locale et la reconstruction intégrale de chaque film de démonstration ne sont pas validées. Les tests graphiques couvrent les moteurs communs, pas 66 rendus complets ni l’esthétique de chaque style.

## Corrections appliquées et configuration conservée

Corrections à cause identifiée uniquement : installation des niveaux voix et musique manquants ; récupération vérifiée des ressources Kokoro/HDRI/Karoryfer ; synchronisation des marqueurs du script de setup ; instructions réutilisables complétées et testées intégralement. Le script enregistré vérifie maintenant explicitement FFmpeg >=7 et Python 3.11–3.13 pour Kokoro, en plus de Node >=20.

Le brouillon sauvegardé contient les champs `install_script` et `start_skill` actualisés. Copies lisibles : `install-verified.sh` et `start-verified.md`. La sauvegarde est confirmée par le statut `saved`; le serveur indique encore `requires_publish: true`. Aucun réseau, secret, nom d’environnement ou membre de dépôt n’a été changé par cet audit.

Il reste à décider des ouvertures réseau avant de retester les fonctions bloquées. Aucune erreur de code du dépôt n’est établie par les contrôles exécutés ; aucune correction de code n’a donc été faite. L’environnement n’est pas présenté comme intégralement validé et sa restauration dans une nouvelle tâche n’a pas été testée.

## Pièces jointes locales

- `export-voix-1080p.mp4` : export fonctionnel avec la voix française.
- `voices/english.wav`, `voices/french.wav`, `voices/dur.json` : synthèses Kokoro.
- `frames-2d/`, `frames-crt/`, `frames-3d/` : images des moteurs communs.
- `export-probe.json`, `integrity.json`, `versions.json`, `python-freeze.txt` : résultats inspectables.
- `styles.json` : inventaire des 66 styles ; `style-requirements.json` : exigences spécifiques.
- `logs/install-repeat.log`, `logs/blackdetect.log`, journaux des packs : traces conservées.

## Annexe : inventaire des styles conservés

| Slug | Nom | Sources | Rendu complet individuel |
|---|---|---|---|
| archive-lighttable | Archive Light Table | Présentes, inchangées | Non exécuté |
| art-deco | Art Deco | Présentes, inchangées | Non exécuté |
| ascii-crt | ASCII / CRT Terminal | Présentes, inchangées | Non exécuté |
| backrooms | Liminal Found Footage | Présentes, inchangées | Non exécuté |
| blueprint | Blueprint | Présentes, inchangées | Non exécuté |
| brick-toy | Brick Toy | Présentes, inchangées | Non exécuté |
| briefing-board | Engineering Briefing Board | Présentes, inchangées | Non exécuté |
| caption-news | Caption News | Présentes, inchangées | Non exécuté |
| cel-anime-80s | 80s Cel Anime | Présentes, inchangées | Non exécuté |
| chalkboard | Chalkboard | Présentes, inchangées | Non exécuté |
| circuit-board | Circuit Board | Présentes, inchangées | Non exécuté |
| city-symphony | Time-lapse Symphony | Présentes, inchangées | Non exécuté |
| countdown | Live Countdown Split-screen | Présentes, inchangées | Non exécuté |
| crayon-book | Crayon Picture Book | Présentes, inchangées | Non exécuté |
| dark-keynote | Dark Tech Keynote | Présentes, inchangées | Non exécuté |
| data-physical | Data Physicalization | Présentes, inchangées | Non exécuté |
| dataviz | Data Storytelling | Présentes, inchangées | Non exécuté |
| desktop-flythrough | Desktop Flythrough | Présentes, inchangées | Non exécuté |
| engraving | Copperplate Engraving | Présentes, inchangées | Non exécuté |
| game-show | Game Show Flat | Présentes, inchangées | Non exécuté |
| glass-product | Glass Product Render | Présentes, inchangées | Non exécuté |
| halftone-dossier | Halftone Dossier | Présentes, inchangées | Non exécuté |
| hd-2d | HD-2D | Présentes, inchangées | Non exécuté |
| hologram-hud | Sci-fi Hologram HUD | Présentes, inchangées | Non exécuté |
| impasto | Impasto Oil Painting | Présentes, inchangées | Non exécuté |
| ink-wash | Chinese Ink Wash | Présentes, inchangées | Non exécuté |
| iso-infographic | Isometric Infographic | Présentes, inchangées | Non exécuté |
| isometric-picture-book | Isometric Picture Book | Présentes, inchangées | Non exécuté |
| kino-montage | Constructivist Montage | Présentes, inchangées | Non exécuté |
| lidar-survey | LiDAR Survey | Présentes, inchangées | Non exécuté |
| living-screencast | Living Screencast | Présentes, inchangées | Non exécuté |
| lowpoly-island | Low-poly Isometric Island | Présentes, inchangées | Non exécuté |
| memphis-diorama | Memphis Diorama | Présentes, inchangées | Non exécuté |
| microgame | Microgame Frenzy | Présentes, inchangées | Non exécuté |
| microscope | Microscope Story | Présentes, inchangées | Non exécuté |
| midcentury-toon | Mid-century Cartoon | Présentes, inchangées | Non exécuté |
| news-package | Broadcast News Package | Présentes, inchangées | Non exécuté |
| newsreel | 1920s Newsreel | Présentes, inchangées | Non exécuté |
| one-line | One-line Drawing | Présentes, inchangées | Non exécuté |
| paper-lantern | Paper-cut Lightbox | Présentes, inchangées | Non exécuté |
| paper-popup | Paper Pop-up Book | Présentes, inchangées | Non exécuté |
| papercut-red | Red Paper-cut | Présentes, inchangées | Non exécuté |
| pictogram-motion | Pictogram Motion | Présentes, inchangées | Non exécuté |
| pixel-rpg | 16-bit Pixel RPG | Présentes, inchangées | Non exécuté |
| printed-long-take | Printed Long Take | Présentes, inchangées | Non exécuté |
| risograph | Risograph Print | Présentes, inchangées | Non exécuté |
| rubber-hose | 1930s Rubber Hose Cartoon | Présentes, inchangées | Non exécuté |
| satellite-briefing | Satellite Briefing | Présentes, inchangées | Non exécuté |
| scifi-toon | Sci-Fi Sitcom Toon | Présentes, inchangées | Non exécuté |
| shadow-puppet | Shadow Puppetry | Présentes, inchangées | Non exécuté |
| silent-film | 1920s Silent Film | Présentes, inchangées | Non exécuté |
| silkscreen-poster | Silkscreen Travel Poster | Présentes, inchangées | Non exécuté |
| spy-titles | 60s Spy Title Sequence | Présentes, inchangées | Non exécuté |
| stained-glass | Stained Glass | Présentes, inchangées | Non exécuté |
| swiss-motion | Swiss Motion Graphics | Présentes, inchangées | Non exécuté |
| teardown | Exploded Teardown | Présentes, inchangées | Non exécuté |
| telestrator | Sports Telestrator | Présentes, inchangées | Non exécuté |
| tilt-shift | Tilt-Shift Miniature | Présentes, inchangées | Non exécuté |
| transit-map | Transit Map | Présentes, inchangées | Non exécuté |
| ukiyoe | Ukiyo-e | Présentes, inchangées | Non exécuté |
| urban-sketch | Urban Sketch · Pen & Wash | Présentes, inchangées | Non exécuté |
| visual-investigation | Visual Investigation | Présentes, inchangées | Non exécuté |
| watercolor | Watercolor Brush | Présentes, inchangées | Non exécuté |
| white-model | Projection on White Model | Présentes, inchangées | Non exécuté |
| whiteboard | Whiteboard Explainer | Présentes, inchangées | Non exécuté |
| woodcut | Woodcut Print | Présentes, inchangées | Non exécuté |
