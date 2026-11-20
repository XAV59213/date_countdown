"""Custom component Souvenirs et Célébrations for Home Assistant."""

import voluptuous as vol

from homeassistant.config_entries import ConfigEntry, ConfigEntryState
from homeassistant.const import ATTR_ENTITY_ID
from homeassistant.core import HomeAssistant, ServiceCall
from homeassistant.exceptions import ServiceValidationError
from homeassistant.helpers import config_validation as cv
from homeassistant.helpers import entity_registry as er

from .const import DOMAIN, PLATFORMS, SERVICE_SEND_TEST_NOTIFICATION
from .frontend import JSModuleRegistration
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
                current.add(reg_entry.unique_id)
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


async def async_setup_entry(hass: HomeAssistant, entry: ConfigEntry) -> bool:
    """Set up from a config entry."""
    domain_data = hass.data.setdefault(DOMAIN, {})
    if not domain_data.get("_card_registered"):
        await JSModuleRegistration(hass).async_register()
        domain_data["_card_registered"] = True
    await hass.config_entries.async_forward_entry_setups(entry, PLATFORMS)

    # Notifications natives (jour J / rappel J-N)
    manager = NotificationManager(hass, entry, await async_get_store(hass))
    domain_data.setdefault(DATA_NOTIFIERS, {})[entry.entry_id] = manager
    await manager.async_start()
    entry.async_on_unload(manager.async_stop)

    entry.async_on_unload(entry.add_update_listener(async_update_entry))
    return True


async def async_update_entry(hass: HomeAssistant, entry: ConfigEntry) -> None:
    """Handle config entry updates."""
    await hass.config_entries.async_reload(entry.entry_id)


async def async_unload_entry(hass: HomeAssistant, entry: ConfigEntry) -> bool:
    """Unload a config entry."""
    unloaded = await hass.config_entries.async_unload_platforms(entry, PLATFORMS)
    if unloaded:
        hass.data.get(DOMAIN, {}).get(DATA_NOTIFIERS, {}).pop(entry.entry_id, None)
    return unloaded
