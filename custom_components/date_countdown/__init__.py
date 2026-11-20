"""Custom component Souvenirs et Célébrations for Home Assistant."""

import voluptuous as vol

from homeassistant.config_entries import ConfigEntry, ConfigEntryState
from homeassistant.const import ATTR_ENTITY_ID
from homeassistant.core import HomeAssistant, ServiceCall, callback
from homeassistant.exceptions import ServiceValidationError
from homeassistant.helpers import config_validation as cv
from homeassistant.helpers import device_registry as dr
from homeassistant.helpers import entity_registry as er

from .const import DOMAIN, EVENT_TYPES, PLATFORMS, SERVICE_SEND_TEST_NOTIFICATION
from .entity import (
    async_device_names,
    async_event_models,
    device_identifier,
    event_device_info,
    find_device,
    person_label,
)
from .frontend import JSModuleRegistration
from .i18n import GENDER_UNSPECIFIED
from .notifications import DATA_NOTIFIERS, NotificationManager, async_get_store

CONFIG_SCHEMA = cv.config_entry_only_config_schema(DOMAIN)

ATTR_ENTRY_ID = "entry_id"

SEND_TEST_SCHEMA = vol.All(
    vol.Schema(
        {
            vol.Optional(ATTR_ENTRY_ID): vol.All(cv.ensure_list, [cv.string]),
            vol.Optional(ATTR_ENTITY_ID): cv.entity_ids,
        }
    ),
    cv.has_at_least_one_key(ATTR_ENTRY_ID, ATTR_ENTITY_ID),
)


_SECONDARY_SUFFIXES = (
    "days_remaining", "next_date", "age", "next_age", "age_category", "years_elapsed", "wedding",
    "age_if_alive", "years_since_death", "death_anniversary_days", "retirement_date", "years_worked",
    "work_medal", "today",
)


def _event_unique_id(unique_id: str) -> str:
    """unique_id d'une entité secondaire (…_days_remaining) → unique_id de l'événement."""
    for suffix in sorted(_SECONDARY_SUFFIXES, key=len, reverse=True):
        if unique_id.endswith(f"_{suffix}"):
            return unique_id[: -len(suffix) - 1]
    return unique_id


async def async_setup(hass: HomeAssistant, config: dict) -> bool:
    """Set up the component."""

    async def _async_send_test_notification(call: ServiceCall) -> None:
        """Service date_countdown.send_test_notification."""
        targets: dict[str, set[str] | None] = {}
        for entry_id in call.data.get(ATTR_ENTRY_ID, []):
            targets[entry_id] = None  # tous les événements de l'entrée
        registry = er.async_get(hass)
        for entity_id in call.data.get(ATTR_ENTITY_ID, []):
            reg_entry = registry.async_get(entity_id)
            if reg_entry is None or reg_entry.platform != DOMAIN or not reg_entry.config_entry_id:
                raise ServiceValidationError(
                    translation_domain=DOMAIN,
                    translation_key="unknown_entity",
                    translation_placeholders={"entity_id": entity_id},
                )
            current = targets.get(reg_entry.config_entry_id, set())
            if current is not None:
                current.add(_event_unique_id(reg_entry.unique_id))
                targets[reg_entry.config_entry_id] = current

        notifiers = hass.data.get(DOMAIN, {}).get(DATA_NOTIFIERS, {})
        for entry_id, event_ids in targets.items():
            entry = hass.config_entries.async_get_entry(entry_id)
            manager = notifiers.get(entry_id)
            if entry is None or entry.domain != DOMAIN or manager is None or entry.state is not ConfigEntryState.LOADED:
                raise ServiceValidationError(
                    translation_domain=DOMAIN,
                    translation_key="unknown_entry",
                    translation_placeholders={"entry_id": entry_id},
                )
            await manager.async_send_test(event_ids)

    hass.services.async_register(
        DOMAIN,
        SERVICE_SEND_TEST_NOTIFICATION,
        _async_send_test_notification,
        schema=SEND_TEST_SCHEMA,
    )
    return True


async def async_migrate_entry(hass: HomeAssistant, entry: ConfigEntry) -> bool:
    """Migration douce : 1.1 → 1.2 ajoute « gender: unspecified » aux événements existants."""
    if entry.version > 1:
        return False  # version future inconnue
    if entry.minor_version < 2:
        events = [
            {**event, "gender": event.get("gender", GENDER_UNSPECIFIED)} if isinstance(event, dict) else event
            for event in entry.options.get("events", []) or []
        ]
        hass.config_entries.async_update_entry(
            entry, options={**entry.options, "events": events}, minor_version=2
        )
    return True


async def async_setup_entry(hass: HomeAssistant, entry: ConfigEntry) -> bool:
    """Set up from a config entry."""
    domain_data = hass.data.setdefault(DOMAIN, {})
    if not domain_data.get("_card_registered"):
        await JSModuleRegistration(hass).async_register()
        domain_data["_card_registered"] = True
    await _async_prepare_devices(hass, entry)
    await hass.config_entries.async_forward_entry_setups(entry, PLATFORMS)
    _async_remove_stale_devices(hass, entry)

    # Notifications natives (jour J / rappel J-N)
    manager = NotificationManager(hass, entry, await async_get_store(hass))
    domain_data.setdefault(DATA_NOTIFIERS, {})[entry.entry_id] = manager
    await manager.async_start()
    entry.async_on_unload(manager.async_stop)

    entry.async_on_unload(entry.add_update_listener(async_update_entry))
    return True


def _valid_events(entry: ConfigEntry) -> list[dict]:
    return [
        event
        for event in entry.options.get("events", []) or []
        if isinstance(event, dict) and event.get("type") in EVENT_TYPES and event.get("name")
    ]


async def _async_prepare_devices(hass: HomeAssistant, entry: ConfigEntry) -> None:
    """Un appareil par événement.

    L'ancien appareil unique « Date Countdown » de l'entrée (identifiant = entry_id) est repris
    par le premier événement (même device_id : pièce, étiquettes et nom personnalisé conservés).
    Le nom, le modèle et la version des appareils existants sont mis à jour sans toucher à
    ``name_by_user``.
    """
    events = _valid_events(entry)
    if not events:
        return
    dev_reg = dr.async_get(hass)
    old = find_device(dev_reg, (DOMAIN, entry.entry_id), entry.entry_id)
    first_id = device_identifier(entry.entry_id, events[0])
    if old is not None and find_device(dev_reg, first_id, entry.entry_id) is None:
        dev_reg.async_update_device(old.id, new_identifiers={first_id})

    names = await async_device_names(hass)
    models = await async_event_models(hass)
    for event in events:
        device = find_device(dev_reg, device_identifier(entry.entry_id, event), entry.entry_id)
        if device is None:
            continue
        info = event_device_info(entry.entry_id, event, models, hass.config.language)
        template = names.get(event["type"]) or "{person}"
        dev_reg.async_update_device(
            device.id,
            name=template.replace("{person}", person_label(event)),
            manufacturer=info["manufacturer"],
            model=info["model"],
            sw_version=info["sw_version"],
            entry_type=info["entry_type"],
        )


@callback
def _async_remove_stale_devices(hass: HomeAssistant, entry: ConfigEntry) -> None:
    """Supprime les appareils de l’entrée qui ne correspondent plus à aucun événement."""
    dev_reg = dr.async_get(hass)
    current = {device_identifier(entry.entry_id, event) for event in _valid_events(entry)}
    for device in dr.async_entries_for_config_entry(dev_reg, entry.entry_id):
        if not device.identifiers & current:
            dev_reg.async_remove_device(device.id)


async def async_update_entry(hass: HomeAssistant, entry: ConfigEntry) -> None:
    """Handle config entry updates."""
    await hass.config_entries.async_reload(entry.entry_id)


async def async_unload_entry(hass: HomeAssistant, entry: ConfigEntry) -> bool:
    """Unload a config entry."""
    unloaded = await hass.config_entries.async_unload_platforms(entry, PLATFORMS)
    if unloaded:
        hass.data.get(DOMAIN, {}).get(DATA_NOTIFIERS, {}).pop(entry.entry_id, None)
    return unloaded
