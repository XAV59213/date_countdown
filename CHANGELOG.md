# Changelog

## 1.2.13 — 2026-10-31

### Ajouté
- Carte Lovelace native **« Informations » 🎂** (`custom:date-countdown-informations-card`), servie et enregistrée automatiquement par l'intégration (aucune ressource manuelle).
  - Affiche l'anniversaire du jour (« Aujourd'hui, c'est l'anniversaire de … ! ») ou « Aujourd'hui, pas d'anniversaire. »
  - Affiche le prochain anniversaire : nombre de jours, âge (« Océane aura 25 ans ») et catégorie d'âge (« et sera un(e) Super-Héros des To-Do Lists ! »).
  - Éditeur visuel en français (`getConfigForm`) : titre, choix des capteurs d'événements, options d'affichage ; détection automatique des anniversaires.
- Exemple YAML : `examples/lovelace/carte-informations.yaml`.

### Modifié
- `manifest.json` : dépendances `http` et `frontend`, version 1.2.13.
