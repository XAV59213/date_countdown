"""Diagnostics (Paramètres → Appareils et services → … → Télécharger les diagnostics).

Données incluses : version, langue / fuseau, options et événements (types, dates, genre),
appareils, entités (états et attributs), anti-doublon des notifications de l'entrée.

Données masquées :
- noms et prénoms des personnes : remplacés par un alias stable « event_1 », « event_2 »…
  partout (options, entity_id, unique_id, noms d'appareils, friendly_name, clés de l'anti-doublon) ;
- titre de l'entrée, noms personnalisés des appareils (``name_by_user``) et des entités : **REDACTED**
  (y compris dans les ``friendly_name``) ;
- cibles de notification (services ``notify.*`` et entités notify) : **REDACTED**.

Les dates (naissance, mariage, décès, début de carrière) sont conservées : sans elles, un calcul
de jours ou d'âge ne peut pas être vérifié. Sans les noms, elles ne permettent pas d'identifier
une personne. Relisez le fichier avant de le partager publiquement.
"""
from __future__ import annotations

from typing import Any

from homeassistant.components.diagnostics import async_redact_data
from homeassistant.config_entries import ConfigEntry
from homeassistant.const import __version__ as HA_VERSION
from homeassistant.core import HomeAssistant
from homeassistant.helpers import device_registry as dr
from homeassistant.helpers import entity_registry as er
from homeassistant.util import slugify

from .const import CONF_NOTIFICATIONS, DOMAIN, VERSION
from .entity import device_identifier, event_unique_id, person_label
from .notifications import DATA_NOTIFIERS, DATA_STORE

REDACTED_KEYS = {"targets", "entities", "title", "name_by_user"}
_PERSON_KEYS = {"name", "first_name"}


class _Anonymizer:
    """Remplace les noms des personnes (et ce qui en dérive) par un alias par événement."""

    def __init__(self, hass: HomeAssistant, entry: ConfigEntry) -> None:
        self.aliases: dict[str, str] = {}  # unique_id de l'événement → alias
        self._pairs: list[tuple[str, str]] = []
        # Noms personnalisés (appareils, entités) : souvent un prénom → masqués aussi
        for device in dr.async_entries_for_config_entry(dr.async_get(hass), entry.entry_id):
            if device.name_by_user:
                self._pairs.append((device.name_by_user, "**REDACTED**"))
        for entity in er.async_entries_for_config_entry(er.async_get(hass), entry.entry_id):
            if entity.name:
                self._pairs.append((entity.name, "**REDACTED**"))
        for index, event in enumerate(_events(entry), start=1):
            alias = f"event_{index}"
            self.aliases[event_unique_id(event)] = alias
            self._pairs.append((event_unique_id(event), alias))
            label = person_label(event)
            pieces = {label, str(event.get("name") or ""), str(event.get("first_name") or "")}
            for piece in sorted((p.strip() for p in pieces if p and p.strip()), key=len, reverse=True):
                self._pairs.append((piece, alias))
                self._pairs.append((slugify(piece), alias))
        # Les plus longues d'abord (« Anais Descamps » avant « Anais »)
        self._pairs.sort(key=lambda pair: len(pair[0]), reverse=True)

    def text(self, value: Any) -> Any:
        if not isinstance(value, str):
            return value
        for old, new in self._pairs:
            if old and len(old) > 1:
                value = value.replace(old, new)
        return value

    def data(self, value: Any) -> Any:
        if isinstance(value, dict):
            return {key: ("**REDACTED**" if key in _PERSON_KEYS and val else self.data(val)) for key, val in value.items()}
        if isinstance(value, list):
            return [self.data(item) for item in value]
        return self.text(value)


def _events(entry: ConfigEntry) -> list[dict[str, Any]]:
    return [e for e in entry.options.get("events", []) or [] if isinstance(e, dict) and e.get("type") and e.get("name")]


def _event_info(anon: _Anonymizer, event: dict[str, Any]) -> dict[str, Any]:
    info = {k: v for k, v in event.items() if k not in _PERSON_KEYS}
    info["alias"] = anon.aliases.get(event_unique_id(event))
    info["has_first_name"] = bool(event.get("first_name"))
    return info


def _device_info(anon: _Anonymizer, device: dr.DeviceEntry) -> dict[str, Any]:
    return {
        "id": device.id,
        "identifiers": [anon.text(f"{domain}:{ident}") for domain, ident in device.identifiers],
        "name": anon.text(device.name),
        "name_by_user": "**REDACTED**" if device.name_by_user else None,
        "manufacturer": device.manufacturer,
        "model": device.model,
        "sw_version": device.sw_version,
        "entry_type": device.entry_type,
        "disabled_by": device.disabled_by,
    }


def _entity_info(hass: HomeAssistant, anon: _Anonymizer, entity: er.RegistryEntry) -> dict[str, Any]:
    state = hass.states.get(entity.entity_id)
    return {
        "entity_id": anon.text(entity.entity_id),
        "unique_id": anon.text(entity.unique_id),
        "domain": entity.domain,
        "device_id": entity.device_id,
        "translation_key": entity.translation_key,
        "disabled_by": entity.disabled_by,
        "hidden_by": entity.hidden_by,
        "has_custom_name": bool(entity.name),
        "state": state.state if state else None,
        "attributes": anon.data(async_redact_data(dict(state.attributes), REDACTED_KEYS)) if state else None,
        "last_changed": state.last_changed.isoformat() if state else None,
    }


def _notifications(hass: HomeAssistant, entry: ConfigEntry, anon: _Anonymizer) -> dict[str, Any]:
    domain_data = hass.data.get(DOMAIN, {})
    store = domain_data.get(DATA_STORE)
    sent = getattr(store, "_sent", {}) or {}
    prefix = f"{entry.entry_id}|"
    return {
        "manager_running": entry.entry_id in domain_data.get(DATA_NOTIFIERS, {}),
        "options": async_redact_data(entry.options.get(CONF_NOTIFICATIONS) or {}, REDACTED_KEYS),
        "sent": {anon.text(key[len(prefix):]): when for key, when in sorted(sent.items()) if key.startswith(prefix)},
    }


async def async_get_config_entry_diagnostics(hass: HomeAssistant, entry: ConfigEntry) -> dict[str, Any]:
    anon = _Anonymizer(hass, entry)
    dev_reg = dr.async_get(hass)
    ent_reg = er.async_get(hass)
    options = {k: v for k, v in entry.options.items() if k != "events"}
    return {
        "integration_version": VERSION,
        "home_assistant": {
            "version": HA_VERSION,
            "language": hass.config.language,
            "time_zone": hass.config.time_zone,
        },
        "entry": {
            "title": "**REDACTED**",
            "version": entry.version,
            "minor_version": entry.minor_version,
            "state": entry.state,
            "data": async_redact_data(dict(entry.data), REDACTED_KEYS),
            "options": anon.data(async_redact_data(options, REDACTED_KEYS)),
        },
        "events": [_event_info(anon, event) for event in _events(entry)],
        "devices": [_device_info(anon, d) for d in dr.async_entries_for_config_entry(dev_reg, entry.entry_id)],
        "entities": [_entity_info(hass, anon, e) for e in er.async_entries_for_config_entry(ent_reg, entry.entry_id)],
        "notifications": _notifications(hass, entry, anon),
    }


async def async_get_device_diagnostics(
    hass: HomeAssistant, entry: ConfigEntry, device: dr.DeviceEntry
) -> dict[str, Any]:
    """Diagnostics d'un appareil (un événement) : même contenu, limité à cet événement."""
    anon = _Anonymizer(hass, entry)
    ent_reg = er.async_get(hass)
    events = [e for e in _events(entry) if device_identifier(entry.entry_id, e) in device.identifiers]
    alias = anon.aliases.get(event_unique_id(events[0])) if events else None
    notifications = _notifications(hass, entry, anon)
    if alias:
        notifications["sent"] = {k: v for k, v in notifications["sent"].items() if k.startswith(f"{alias}|")}
    return {
        "integration_version": VERSION,
        "home_assistant": {"version": HA_VERSION, "language": hass.config.language},
        "event": _event_info(anon, events[0]) if events else None,
        "device": _device_info(anon, device),
        "entities": [_entity_info(hass, anon, e) for e in er.async_entries_for_device(ent_reg, device.id)],
        "notifications": notifications,
    }
