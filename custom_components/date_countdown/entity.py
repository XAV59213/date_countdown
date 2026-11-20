"""Appareil par événement et outils communs aux entités (capteurs, calendrier, jour J)."""
from __future__ import annotations

from typing import Any

from homeassistant.core import HomeAssistant
from homeassistant.helpers.device_registry import DeviceEntryType, DeviceInfo
from homeassistant.helpers.translation import async_get_translations

from .const import DOMAIN, VERSION
from .i18n import event_type_label

MANUFACTURER = "XAV59213"
_DATA_MODELS = "_device_models"


def event_unique_id(event: dict[str, Any]) -> str:
    """unique_id historique du capteur principal (et du calendrier) d'un événement."""
    base = f"{event['type']}_{str(event['name']).lower().replace(' ', '_')}"
    when = (event.get("start_date") or event.get("date") or "").replace("/", "")
    return f"{base}_{when}"


def person_label(event: dict[str, Any]) -> str:
    """« Prénom Nom » (ou le nom seul)."""
    first = (event.get("first_name") or "").strip()
    name = str(event.get("name") or "").strip()
    return f"{first} {name}".strip() if first else name


def device_identifier(entry_id: str, event: dict[str, Any]) -> tuple[str, str]:
    return (DOMAIN, f"{entry_id}_{event_unique_id(event)}")


async def async_event_models(hass: HomeAssistant) -> dict[str, str]:
    """Libellés des types d'événements dans la langue de HA (22 langues), pour le modèle de l'appareil."""
    language = hass.config.language
    cache = hass.data.setdefault(DOMAIN, {}).setdefault(_DATA_MODELS, {})
    if language not in cache:
        prefix = f"component.{DOMAIN}.selector.event_type.options."
        translations = await async_get_translations(hass, language, "selector", [DOMAIN])
        cache[language] = {
            key[len(prefix):]: value for key, value in translations.items() if key.startswith(prefix)
        }
    return cache[language]


async def async_device_names(hass: HomeAssistant) -> dict[str, str]:
    """Modèles de noms d'appareil traduits (« {person} - Anniversaire »…)."""
    prefix = f"component.{DOMAIN}.device."
    translations = await async_get_translations(hass, hass.config.language, "device", [DOMAIN])
    return {
        key[len(prefix):-len(".name")]: value
        for key, value in translations.items()
        if key.startswith(prefix) and key.endswith(".name")
    }


def event_device_info(entry_id: str, event: dict[str, Any], models: dict[str, str], language: str) -> DeviceInfo:
    """Un appareil par événement : nom = l'événement (traduit), modèle = type traduit."""
    event_type = event["type"]
    return DeviceInfo(
        identifiers={device_identifier(entry_id, event)},
        translation_key=event_type,
        translation_placeholders={"person": person_label(event)},
        manufacturer=MANUFACTURER,
        model=models.get(event_type) or event_type_label(event_type, language),
        sw_version=VERSION,
        entry_type=DeviceEntryType.SERVICE,
    )


def find_device(dev_reg: Any, identifier: tuple[str, str], entry_id: str) -> Any:
    """Appareil de l'entrée portant cet identifiant (API récente, repli pour les anciennes versions de HA)."""
    if hasattr(dev_reg, "async_get_device_by_identifier"):
        return dev_reg.async_get_device_by_identifier(identifier, entry_id)
    return dev_reg.async_get_device(identifiers={identifier})
