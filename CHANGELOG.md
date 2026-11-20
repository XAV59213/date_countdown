# Changelog

## Non publié

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
