"""Binary sensor « Aujourd'hui » (jour J) de chaque événement."""
from __future__ import annotations

from typing import Any

from homeassistant.components.binary_sensor import BinarySensorEntity
from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant

from .const import EVENT_TYPES
from .entity import async_event_models, event_device_info
from .sensor import DateCountdownEventEntity


async def async_setup_entry(hass: HomeAssistant, entry: ConfigEntry, async_add_entities) -> None:
    models = await async_event_models(hass)
    entities = []
    for event in entry.options.get("events", []) or []:
        if not isinstance(event, dict) or event.get("type") not in EVENT_TYPES or not event.get("name"):
            continue
        if not (event.get("start_date") if event["type"] == "retirement" else event.get("date")):
            continue
        device_info = event_device_info(entry.entry_id, event, models, hass.config.language)
        entities.append(DateCountdownTodaySensor(event, device_info, "today", hass.config.language))
    if entities:
        async_add_entities(entities)


class DateCountdownTodaySensor(DateCountdownEventEntity, BinarySensorEntity):
    """Allumé le jour J (anniversaire de la date ; mémorial : aussi l'anniversaire du décès ; retraite : le jour du départ)."""

    _attr_icon = "mdi:party-popper"

    def _occasion(self) -> str | None:
        c = self._calc
        today = self._today
        if c._event_type == "retirement":
            return "retirement" if c._retirement_date is not None and c._retirement_date == today else None
        if c.state == 0:
            return c._event_type
        if c._event_type == "memorial" and c._days_to_death_anniversary == 0 and self._death() and today.year > self._death().year:
            return "death_anniversary"
        return None

    @property
    def is_on(self) -> bool | None:
        if self._calc.state is None:
            return None
        return self._occasion() is not None

    @property
    def extra_state_attributes(self) -> dict[str, Any]:
        return {"occasion": self._occasion()}
