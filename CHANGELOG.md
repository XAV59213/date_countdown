# Changelog

## Non publié

### Ajouté
- 📟 **Un appareil par événement** : nom = l’événement (« Anais Descamps - Anniversaire », traduit selon le type, 22 langues), fabricant `XAV59213`, modèle = type d’événement traduit, version de l’intégration, type *service*. Le capteur principal (qui n’avait pas d’appareil) et le calendrier y sont rattachés.
- ➕ **Entités séparées par événement** (créées selon le type) : jours restants, prochaine date, âge et âge au prochain anniversaire, catégorie d’âge, années écoulées, noces, âge si vivant, années depuis le décès, jours avant l’anniversaire du décès, date de retraite, années travaillées, médaille du travail (`enum` traduit) et `binary_sensor` « Aujourd’hui (jour J) ». Noms via `translation_key` (22 langues), `unique_id` stables, icônes, `device_class` / unités adaptés, recalcul au démarrage et à minuit.
- Le service `send_test_notification` accepte aussi une entité secondaire de l’événement.
- Tests : `tests/test_capteurs.py` (appareils, entités par type, valeurs, minuit, jour J, migration de l’ancien appareil, nom personnalisé conservé, entity_id inchangés).

### Modifié
- L’ancien appareil unique « Date Countdown » de chaque entrée est repris par le premier événement (même appareil, nom personnalisé conservé) ; nom, modèle et version mis à jour au démarrage ; appareils d’événements supprimés retirés.
- Le capteur principal prend le nom de son appareil (texte identique : « Anais Descamps - Anniversaire ») ; ses attributs et son état sont inchangés, les `entity_id` existants aussi.
- 🏷️ **Page de l’intégration** (Paramètres → Appareils et services → Souvenirs et Célébrations) : le bouton « Ajouter un hub » devient **« Ajouter un événement »** (traduction `config.initiate_flow.user`, 22 langues), et la section des entrées s’appelle **« Services »** au lieu de « Ponts » (`integration_type` : `hub` → `service`, comme les intégrations de calcul de dates du cœur : Workday, Season, Moon, Sun). Aucun effet sur les entrées, appareils, capteurs ou automatisations existants.
- Tests : `tests/test_libelles.py`.

## 1.2.20 — 2026-11-20

### Ajouté
- 📅 **Calendrier des mémoriaux** : l’anniversaire du décès apparaît chaque année (à partir de l’année suivant le décès, 29 février → 28 février) avec un texte sobre « Jeanne Martin - Mémorial (Anniversaire du décès : 6 ans) », traduit en fr, en, de, es, it. Toujours affiché, indépendamment de l’option de notification `death_anniversary`. L’état du calendrier (prochain événement) prend la date la plus proche entre anniversaire de naissance et anniversaire du décès.
- 🌍 **Catégories d’âge et noces en allemand, espagnol et italien** (121 catégories, 60 noces par langue) ; repli anglais conservé pour les autres langues.
- 🚻 **Formes féminines pour toutes les catégories d’âge** en fr, en, de, es, it (« Impératrice », « Königin », « Emperatriz », « Campionessa », « Weise »…) ; titres épicènes inchangés.
- 🎨 Éditeurs des cartes Lovelace et sélecteur de cartes en allemand, espagnol et italien.
- Tests : `tests/test_finitions.py` (tables complètes, féminin de chaque catégorie dans chaque langue, noces, calendrier des mémoriaux, clés des éditeurs).

### Modifié
- Formes féminines appliquées par mot entier (plus de remplacement partiel) ; nouveau module `i18n_data.py` pour les tables de/es/it.

### Corrigé
- 🐛 **Options → Modifier un événement** : l’écran « Sélectionnez un événement à modifier » s’affichait d’emblée avec l’erreur « Veuillez sélectionner un événement… », même avec l’événement coché. L’étape de sélection était appelée avec une saisie vide (`{}`) au lieu d’être simplement affichée. Le formulaire s’affiche maintenant sans erreur, le premier événement est pré-sélectionné et la valeur est validée de façon robuste.
- Message d’erreur « event_required » : « dans la liste » au lieu de « dans la liste déroulante » (fr, en).
- Tests : `tests/test_options_flow.py` (parcours complet des Options : sélection → type → édition → sauvegarde, notifications ; entrées migrées depuis 1.2.18 et neuves, un ou plusieurs événements).

## 1.2.19 — 2026-11-20

### Ajouté
- 🔔 **Entités de notification modernes** : nouveau champ « Entités de notification » (`entities`) dans *Configurer les notifications*, envoi via `notify.send_message` avec `entity_id`, combinable avec les services `notify.*` classiques. Une ancienne cible `targets` qui n’est plus un service mais une entité est envoyée automatiquement par `notify.send_message`.
- 🕯️ **Rappel de l’anniversaire du décès** (mémoriaux, option `death_anniversary`) : notification distincte à la date anniversaire du décès (29 février → 28 février les années non bissextiles), et rappel J-N si réglé ; anti-doublon séparé. Attribut `days_to_death_anniversary`.
- 🚻 **Genre par événement** (*Non précisé* / *Homme* / *Femme*) dans l’assistant et les Options (anniversaires, mémoriaux, retraites, promotions) : accords des notifications (« Disparue », « Thinking of her »), des catégories d’âge au féminin (« Super-Héroïne », « Reine », « Impératrice »…) et des cartes Lovelace. Attribut `gender`.
- 🌍 **Textes générés traduits selon la langue de Home Assistant** : noms des capteurs via `translation_key` (22 langues), notifications, types, médailles et résumés du calendrier (fr, en, de, es, it), catégories d’âge et noces (fr, en) ; repli anglais.
- 🌍 **Cartes Lovelace multilingues** (fr, en, de, es, it selon `hass.locale.language`, repli anglais) ; éditeurs et sélecteur de cartes en fr / en.
- Listes « Type d’événement », « Type de carrière » et « Genre » de l’assistant traduites (`translation_key` des sélecteurs).
- Tests : `tests/test_ameliorations.py` (langues, genre, anniversaire du décès, entités notify, migration, calendrier).

### Modifié
- Migration douce des entrées (version 1.2) : `gender: unspecified` ajouté aux événements existants, textes inchangés.
- Le nom du calendrier affiche le type traduit (« Océane Dupont - Anniversaire ») au lieu de la clé brute (`birthday`).
- Les attributs `age_category`, `wedding_type` et `work_medal` suivent la langue de Home Assistant (en français pour une instance en français, comme avant).
- Aperçu `docs/apercu-cartes.html` : paramètre `?lang=` et genres d’exemple.

## 1.2.18 — 2026-11-20

### Ajouté
- 🌍 **Traductions de l’interface en 22 langues** : allemand (`de`), espagnol (`es`), italien (`it`), portugais (`pt`), portugais du Brésil (`pt-BR`), néerlandais (`nl`), polonais (`pl`), russe (`ru`), suédois (`sv`), norvégien bokmål (`nb`), danois (`da`), finnois (`fi`), tchèque (`cs`), slovaque (`sk`), hongrois (`hu`), turc (`tr`), grec (`el`), roumain (`ro`), ukrainien (`uk`) et catalan (`ca`), en plus du français et de l’anglais. Couvre l’assistant d’ajout, les Options, les notifications, le service de test et les messages d’erreur.
- Script `scripts/check_translations.py` (et test `tests/test_translations.py`) : chaque fichier de traduction doit être du JSON valide, avoir exactement les mêmes clés que `en.json` et les mêmes placeholders `{...}`.
- 📋 **Carte Liste / Agenda** `custom:date-countdown-list-card` : tous les capteurs de l'intégration détectés automatiquement, sections par type (🎂 💍 🕯️ 🏆 ⭐ 🏖️) ou liste unique, badge J-N coloré, âge à venir, noces, catégorie d'âge, médaille, date en français, 🔔, filtres (types, horizon, max, masquer aujourd'hui / retraites passées), mode compact.
- ⏳ **Carte Compte à rebours** `custom:date-countdown-countdown-card` : un événement en grand (prochain automatique ou choisi), anneau de progression, sous-titre, confettis CSS le jour J (désactivables, respectent « réduire les animations »).
- 📅 **Carte Frise des mois** `custom:date-countdown-timeline-card` : les 12 (ou N) prochains mois en frise verticale ou en grille, puces colorées par type, légende.
- 🕯️ **Carte Mémoriaux** `custom:date-countdown-memorial-card` : ton sobre, « aurait eu N ans », « disparu(e) depuis N ans », date et âge au décès.
- Éditeur visuel natif en français, aperçu dans le sélecteur de cartes, thème clair/sombre, clic = fiche de l'entité, compatibles vue *sections*.
- Attributs de capteur `notifications_enabled` et `retirement_date` (retraites), utilisés par les cartes.
- Exemples `examples/lovelace/`, aperçu local `docs/apercu-cartes.html` et captures `docs/cartes/`.

### Corrigé
- `fr.json` : titres des étapes d’ajout et erreur `creation_failed` manquants.
- `strings.json` aligné sur `en.json` / `fr.json` (étapes et erreurs des Options qui manquaient).

### Remarque
- Les textes générés en Python (messages de notification, catégories d’âge, noces, noms des capteurs, listes de types) et les cartes Lovelace restent en français pour l’instant.

## 1.2.17 — 2026-11-20

### Ajouté
- 🔔 **Notifications natives le jour J** : dans les Options de chaque événement (*Configurer les notifications*), choix d’une ou plusieurs cibles `notify.*`, de l’heure d’envoi (09:00 par défaut, heure locale HA), d’un rappel J-N (0 = désactivé) et d’une notification persistante HA.
  - Messages en français adaptés au type (âge et catégorie d’âge, noces, âge qu’aurait eu la personne, retraite et médaille, promotion, événement spécial).
  - Anti-doublon persistant (`.storage/date_countdown.notifications`) et rattrapage si HA redémarre après l’heure prévue le jour J.
  - Un échec sur une cible n’empêche pas les autres ; nouvel essai 10 minutes plus tard si tout a échoué.
- Service `date_countdown.send_test_notification` (par `entry_id` ou `entity_id`).
- Tests automatisés (`tests/`, pytest-homeassistant-custom-component).

### Corrigé
- Options : le menu ne s’ouvrait plus sur les versions récentes de Home Assistant (`_config_entry_id` réservé par HA).
- Options : la modification d’un événement échouait (`KeyError` après le choix du type, erreur à l’enregistrement) ; les autres options de l’entrée sont désormais conservées.
- Traductions des étapes des Options (section `options`).
- README : 6 types d’événements (ajout de la retraite et des médailles du travail) ; l’Options flow permet de modifier un événement (et ses notifications), sans ajout ni suppression. L’ajout se fait via « Ajouter une entrée » (une entrée par événement), la suppression en supprimant l’entrée.
- Les occurrences d’une date au 29 février tombent le 28 février les années non bissextiles (usage courant en France), pour le prochain événement, le calendrier (50 ans) et la date de retraite estimée.

### Modifié
- CI : `actions/checkout` v4 → v7 dans le workflow du zip de release (Dependabot, #9).
- `manifest.json` et `const.py` (`VERSION`, cache de la carte) : version 1.2.17.

## 1.2.16 — 2026-10-31

### Modifié
- README : images en URLs raw (affichage correct dans HACS).
- `manifest.json` : version 1.2.16.

## 1.2.15 — 2026-10-31

### Modifié
- README : badges d’en-tête alignés (HACS, release, Hassfest, validation HACS, licence, téléchargements, version, Home Assistant), bouton Buy Me a Coffee, badges My Home Assistant (dépôt HACS et config flow).
- `manifest.json` : version 1.2.15.

## 1.2.14 — 2026-10-31

### Ajouté
- Traduction anglaise (`translations/en.json`).

### Corrigé
- Traductions : options d’action déplacées vers le sélecteur (conformité hassfest).

### Modifié
- `manifest.json` : version 1.2.14.

## 1.2.13 — 2026-10-31

### Ajouté
- Carte Lovelace native **« Informations » 🎂** (`custom:date-countdown-informations-card`), servie et enregistrée automatiquement par l'intégration (aucune ressource manuelle).
  - Affiche l'anniversaire du jour (« Aujourd'hui, c'est l'anniversaire de … ! ») ou « Aujourd'hui, pas d'anniversaire. »
  - Affiche le prochain anniversaire : nombre de jours, âge (« Océane aura 25 ans ») et catégorie d'âge (« et sera un(e) Super-Héros des To-Do Lists ! »).
  - Éditeur visuel en français (`getConfigForm`) : titre, choix des capteurs d'événements, options d'affichage ; détection automatique des anniversaires.
- Exemple YAML : `examples/lovelace/carte-informations.yaml`.

### Modifié
- `manifest.json` : dépendances `http` et `frontend`, version 1.2.13.
