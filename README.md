# Souvenirs et Célébrations

[![HACS Custom](https://img.shields.io/badge/HACS-Custom-orange.svg)](https://hacs.xyz) [![Release](https://img.shields.io/github/v/release/XAV59213/date_countdown?label=release)](https://github.com/XAV59213/date_countdown/releases/latest) [![Hassfest](https://img.shields.io/github/actions/workflow/status/XAV59213/date_countdown/hassfest.yml?branch=main&label=Hassfest&logo=github)](https://github.com/XAV59213/date_countdown/actions/workflows/hassfest.yml) [![HACS validation](https://img.shields.io/github/actions/workflow/status/XAV59213/date_countdown/hacs.yml?branch=main&label=HACS%20validation&logo=github)](https://github.com/XAV59213/date_countdown/actions/workflows/hacs.yml) [![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](LICENSE) [![Downloads](https://img.shields.io/github/downloads/XAV59213/date_countdown/total.svg?label=Downloads)](https://github.com/XAV59213/date_countdown/releases) [![Version](https://img.shields.io/github/v/release/XAV59213/date_countdown?label=VERSION&color=blue)](https://github.com/XAV59213/date_countdown/releases/latest) [![Home Assistant](https://img.shields.io/badge/HOME%20ASSISTANT-%3E%3D2024.6.0-41BDF5.svg)](https://www.home-assistant.io)

[![Buy Me A Coffee](https://img.buymeacoffee.com/button-api/?text=xav59213&emoji=&slug=xav59213&button_colour=5F7FFF&font_colour=ffffff&font_family=Cookie&outline_colour=000000&coffee_colour=FFDD00)](https://www.buymeacoffee.com/xav59213)

## Via HACS (recommandé)

[![Open your Home Assistant instance and open a repository inside the Home Assistant Community Store.](https://my.home-assistant.io/badges/hacs_repository.svg)](https://my.home-assistant.io/redirect/hacs_repository/?owner=XAV59213&repository=date_countdown&category=integration)

[![Open your Home Assistant instance and start setting up a new integration.](https://my.home-assistant.io/badges/config_flow_start.svg)](https://my.home-assistant.io/redirect/config_flow_start/?domain=date_countdown)


<p align="center">
  <img src="https://raw.githubusercontent.com/XAV59213/date_countdown/main/brand/logo.png" alt="Souvenirs et Célébrations" width="640">
</p>

**Souvenirs et Célébrations** (`date_countdown`) est une intégration personnalisée pour [Home Assistant](https://www.home-assistant.io) qui permet de suivre les jours restants avant des événements personnels : anniversaires, anniversaires de mariage, promotions, mémoriaux, retraites ou événements spéciaux.

Entièrement configurable via l’interface graphique, aucun YAML requis. Les capteurs sont automatiquement créés pour vos dashboards Lovelace, automatisations, notifications ou alertes.

<p align="center">
  <img src="https://raw.githubusercontent.com/XAV59213/date_countdown/main/brand/icon.png" alt="Icône" width="128">
</p>

<a href="https://www.buymeacoffee.com/xav59213"> <img src="https://img.buymeacoffee.com/button-api/?text=xav59213&emoji=&slug=xav59213&button_colour=5F7FFF&font_colour=ffffff&font_family=Cookie&outline_colour=000000&coffee_colour=FFDD00" />

---

## ✨ Fonctionnalités

- ✅ Interface graphique pour ajouter, modifier ou supprimer des événements
- 📅 Types d’événements :
  - 🎂 Anniversaire
  - 💍 Anniversaire de mariage (avec intitulés des noces)
  - 🕯️ Mémorial (âge qu’aurait eu la personne, années depuis le décès)
  - 🏆 Promotion
  - 🌟 Événement spécial
  - 🏖️ Retraite (estimation de la date, médailles du travail)
- ⚙️ Capteurs automatiques :
  - État = nombre de jours restants
  - Attributs : type, date, prénom, années, intitulé des noces, etc.
- 🎨 Icônes dynamiques selon le type
- 🌍 Interface de configuration traduite en 22 langues (voir [Langues](#-langues))
- 🔔 Prêt pour Lovelace, automatisations, TTS, notifications

---

## 🧱 Prérequis

- Home Assistant `>= 2024.6.0`
- [HACS](https://hacs.xyz) installé

---

## ⚙️ Installation via HACS

1. Ouvrez **HACS > Intégrations**
2. Cliquez sur **⋮ > Dépôt personnalisé**
3. Ajoutez ce dépôt :
   ```
   https://github.com/XAV59213/date_countdown
   ```
   Type : **Intégration**
4. Installez **Souvenirs et Célébrations**
5. Redémarrez Home Assistant
6. Allez dans **Paramètres > Appareils & Services > Ajouter une intégration**
7. Recherchez **Souvenirs et Célébrations** ou **Date Countdown**

---

## 🔧 Configuration

### ➕ Ajouter un événement

- Dans **Paramètres > Appareils & services**, cliquez sur **Ajouter une intégration**, puis recherchez **Souvenirs et Célébrations**. Chaque événement correspond à une entrée distincte.
- Type : sélectionnez parmi les 6 types disponibles
- Nom (obligatoire), Prénom (optionnel)
- Date : `JJ/MM/AAAA`
- Pour les mémoriaux : date de décès (optionnelle)
- Pour la retraite : date de début du travail, type de carrière, option « travaux pénibles »

### 🔁 Modifier un événement

- Dans l’entrée de l’intégration : `⋮ > Options`
- L’Options flow permet de **modifier** l’événement de cette entrée et de **configurer ses notifications** (voir [🔔 Notifications](#-notifications)) ; pas d’ajout ni de suppression d’événement.

### 🗑️ Supprimer un événement

- Supprimez l’entrée correspondante dans **Paramètres > Appareils & services**.

### 📅 29 février

Les événements datés du 29 février sont observés le **28 février** les années non bissextiles (usage courant en France). Les années bissextiles, la date reste le 29 février. La date d’origine saisie n’est pas modifiée.

---

## 🐞 Capteurs générés

Format :
```
sensor.<type>_<nom>_<date>
```

Exemple :

```yaml
sensor.memorial_jean_01011950:
  state: 15
  attributes:
    friendly_name: "Jean - Mémorial"
    first_name: "Jean"
    event_type: "memorial"
    event_date: "01/01/1950"
    years: 76
    death_date: "15/06/2000"
    age_if_alive: 75
    years_since_death: 25
```

---

## 🎂 Carte Lovelace

L'intégration fournit sa propre carte **« Informations »**, chargée automatiquement (aucune ressource à ajouter, rien à copier dans `www`).

**Ajout via l'interface** : Tableau de bord → ✏️ Modifier → **Ajouter une carte** → chercher **« Souvenirs et Célébrations — Informations »**. L'éditeur permet de régler le titre, de choisir les capteurs d'événements (vide = tous les anniversaires détectés) et les options d'affichage.

Exemple de rendu :

> **Informations** 🎂
> Aujourd'hui, pas d'anniversaire.
> Le prochain anniversaire est dans 54 jours
> Océane aura 25 ans
> et sera un(e) Super-Héros des To-Do Lists !

**YAML** :

```yaml
type: custom:date-countdown-informations-card
title: Informations
entities:            # facultatif
  - sensor.anniversaire_oceane
show_icon: true
show_category: true
show_upcoming: true
```

> Si la carte n'apparaît pas après une mise à jour, vider le cache du navigateur. En dernier recours, ajouter manuellement la ressource `/date_countdown/date-countdown-card.js` (module JavaScript).

## 🖼️ Exemple Lovelace (mémoriaux à venir)

```yaml
type: markdown
content: |
  ## 🕯️ Mémoriaux à venir
  {% set ns = namespace(events=[]) %}
  {% for entity in states.sensor if entity.entity_id.endswith('memorial') %}
    {% if (entity.state | int(0)) > 0 %}
      {% set ns.events = ns.events + [entity] %}
    {% endif %}
  {% endfor %}
  {% for e in ns.events | sort(attribute='state') | slice(2) %}
  - **{{ state_attr(e.entity_id, 'friendly_name') }}** : {{ e.state }} jours
    - Âge au prochain anniversaire : {{ state_attr(e.entity_id, 'years') }} ans
    - Âge s’il était en vie : {{ state_attr(e.entity_id, 'age_if_alive') }}
    {% if state_attr(e.entity_id, 'death_date') %}
    - Décès : {{ state_attr(e.entity_id, 'death_date') }} ({{ state_attr(e.entity_id, 'years_since_death') }} ans)
    {% endif %}
  {% endfor %}
```

---

## 🔔 Notifications

Chaque événement peut envoyer **une notification native le jour J**, sans automatisation à écrire.

**Réglage :** *Paramètres → Appareils et services → Souvenirs et Célébrations → (votre événement) → Configurer → Configurer les notifications 🔔*

| Option | Clé | Défaut | Description |
|---|---|---|---|
| Activer les notifications | `enabled` | désactivé | Active l’envoi pour cette entrée |
| Cibles de notification | `targets` | — | Un ou plusieurs services `notify.*` (ex. `notify.mobile_app_mon_telephone`) ; la liste est construite à partir des services notify disponibles, saisie manuelle possible |
| Heure d’envoi | `time` | `09:00` | Heure locale de Home Assistant |
| Rappel J-N | `reminder_days` | `0` | Rappel N jours avant (ex. `7`) ; `0` = désactivé |
| Notification persistante | `persistent` | désactivé | Affiche aussi le message dans les notifications de Home Assistant |

Les options sont enregistrées dans les options de l’entrée, sous la clé `notifications`.

**Exemples de messages :**

| Type | Jour J |
|---|---|
| 🎂 Anniversaire | « 🎂 Aujourd’hui, Océane a 25 ans ! Super-Héros des To-Do Lists » |
| 💍 Mariage | « 💍 Aujourd’hui, Paul et Marie fête 25 ans de mariage : Noces d'Argent ! » |
| 🕯️ Mémorial | « 🕯️ Aujourd’hui, Jean aurait eu 80 ans. Disparu(e) depuis 5 ans. Une pensée en sa mémoire. » |
| 🏆 Promotion | « 🏆 Aujourd’hui, Luc Dupont fête 5 ans de promotion ! » |
| ⭐ Événement spécial | « ⭐ Aujourd’hui : Rencontre (10 ans) ! » |
| 🏖️ Retraite | « 🏖️ Aujourd’hui, Alain part à la retraite après 45 ans de travail ! Médaille du travail : … » |

Rappel J-N : « ⏳ Dans 7 jours : anniversaire d’Océane (25 ans) » (« Demain : … » pour J-1).

**Fonctionnement :**
- le jour J est celui où le capteur vaut `0` (même calcul que le capteur) ; pour la retraite, uniquement le jour du départ ;
- **anti-doublon** : chaque envoi est mémorisé (`.storage/date_countdown.notifications`), rien n’est renvoyé après un redémarrage ;
- **rattrapage** : si Home Assistant redémarre après l’heure prévue le jour J, la notification est envoyée une fois au démarrage ;
- si une cible échoue, les autres reçoivent quand même le message (avertissement dans les logs) ; si tout échoue, un nouvel essai a lieu 10 minutes plus tard.

**Tester :** *Outils de développement → Actions →* `date_countdown.send_test_notification`

```yaml
action: date_countdown.send_test_notification
data:
  entity_id: sensor.oceane_dupont_anniversaire   # ou entry_id: <id de l’entrée>
```

Le test envoie immédiatement un message (préfixé « 🧪 Test – ») aux cibles configurées, même si les notifications sont désactivées ; sans cible, il crée une notification persistante.

> Les services `notify.*` classiques (`notify.mobile_app_…`, `notify.notify`, `notify.persistent_notification`…) sont pris en charge. Les entités de notification (`notify.send_message` avec `entity_id`) ne le sont pas encore.

---

## 🔔 Exemple d’automatisation

```yaml
automation:
  - alias: "Rappel mémorial 7 jours avant"
    trigger:
      platform: numeric_state
      entity_id: sensor.memorial_jean_01011950
      value: 7
    action:
      service: notify.notify
      data:
        message: >
          📅 Dans 7 jours : anniversaire de {{ state_attr('sensor.memorial_jean_01011950', 'friendly_name') }}.
          Âge s’il était en vie : {{ state_attr('sensor.memorial_jean_01011950', 'age_if_alive') }} ans.
```

---

## 🛠️ Dépannage

### Les capteurs n’apparaissent pas ?
- Vérifiez que les dates sont bien au format `JJ/MM/AAAA`
- Redémarrez Home Assistant après ajout ou suppression d’événements

### Problème avec les mémoriaux ?
- `death_date` : format `JJ/MM/AAAA`
- Vérifiez les attributs dans **Développeur > États**

### Activer les logs de debug

```yaml
logger:
  default: info
  logs:
    custom_components.date_countdown: debug
```

---

## 🌍 Langues

L’interface de configuration (assistant d’ajout, Options, notifications, service de test, messages d’erreur) est traduite en **22 langues** :

🇫🇷 français (`fr`) · 🇬🇧 anglais (`en`) · 🇩🇪 allemand (`de`) · 🇪🇸 espagnol (`es`) · 🇮🇹 italien (`it`) · 🇵🇹 portugais (`pt`) · 🇧🇷 portugais du Brésil (`pt-BR`) · 🇳🇱 néerlandais (`nl`) · 🇵🇱 polonais (`pl`) · 🇷🇺 russe (`ru`) · 🇸🇪 suédois (`sv`) · 🇳🇴 norvégien bokmål (`nb`) · 🇩🇰 danois (`da`) · 🇫🇮 finnois (`fi`) · 🇨🇿 tchèque (`cs`) · 🇸🇰 slovaque (`sk`) · 🇭🇺 hongrois (`hu`) · 🇹🇷 turc (`tr`) · 🇬🇷 grec (`el`) · 🇷🇴 roumain (`ro`) · 🇺🇦 ukrainien (`uk`) · catalan (`ca`)

Home Assistant choisit automatiquement la langue de votre profil.

> ⚠️ **Restent en français pour l’instant**, quelle que soit la langue : les textes générés par le code Python, c’est-à-dire les messages des notifications, les catégories d’âge humoristiques, les intitulés des noces, les noms et attributs des capteurs et du calendrier, les listes de choix « Type d’événement » et « Type de carrière » de l’assistant, ainsi que la carte Lovelace « Informations ».

Pour vérifier les fichiers de traduction (JSON valide, mêmes clés et mêmes placeholders `{...}` que `en.json`) :

```bash
python3 scripts/check_translations.py
```

---

## 📁 Structure technique

| Fichier                                | Rôle                                             |
|----------------------------------------|--------------------------------------------------|
| `__init__.py`                          | Initialisation du composant                     |
| `config_flow.py`                       | Flux de configuration UI                        |
| `sensor.py`                            | Création et mise à jour des capteurs            |
| `calendar.py`                          | Calendrier des occurrences (50 ans)             |
| `date_utils.py`                        | Dates d’anniversaire, y compris le 29 février   |
| `const.py`                             | Types, formats, intitulés, noces                |
| `translations/*.json`                  | Traductions de l’interface (22 langues)         |
| `manifest.json`                        | Métadonnées HACS                                |
| `brand/icon.png`                       | Icône HACS (512×512)                            |
| `brand/logo.png`                       | Logo                                            |

---

## 👨‍💻 Crédits

- Auteur : [@XAV59213](https://github.com/XAV59213)
- Licence : [MIT](https://github.com/XAV59213/date_countdown/blob/main/LICENSE)
- Dépôt : [https://github.com/XAV59213/date_countdown](https://github.com/XAV59213/date_countdown)

---

## 📢 Support

💬 Pour toute question, bug ou suggestion :
➡️ [Créer une issue sur GitHub](https://github.com/XAV59213/date_countdown/issues)
