# Changelog

## Non publié

### Corrigé
- README : 6 types d’événements (ajout de la retraite et des médailles du travail) ; l’Options flow ne permet que de modifier un événement. L’ajout se fait via « Ajouter une entrée » (une entrée par événement), la suppression en supprimant l’entrée.
- Les occurrences d’une date au 29 février tombent le 28 février les années non bissextiles (usage courant en France), pour le prochain événement, le calendrier (50 ans) et la date de retraite estimée.

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
