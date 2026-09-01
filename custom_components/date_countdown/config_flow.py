"""Config flow for Date Countdown integration.

This module handles the configuration flow for the Date Countdown integration,
allowing users to edit events through the Home Assistant UI.
The 'Saint du jour' and 'Jour férié' sensors are enabled by default and not configurable.
"""

import logging
from typing import Any, Dict, Optional
import re
import voluptuous as vol
from datetime import date
from homeassistant import config_entries
from homeassistant.core import callback
from homeassistant.data_entry_flow import FlowResult

from .const import DOMAIN, EVENT_TYPES, DATE_FORMAT

_LOGGER = logging.getLogger(__name__)

def _generate_entry_title(events: list) -> str:
    """Generate a title for the config entry based on the list of events."""
    if not events:
        return "Compte à rebours d'événements (vide)"
    event_type_labels = {
        "birthday": "Anniversaire",
        "anniversary": "Anniversaire de mariage",
        "memorial": "Mémorial",
        "promotion": "Promotion",
        "special_event": "Événement spécial",
        "retirement": "Retraite"
    }
    event_names = []
    for event in events[:2]:
        prefix = f"{event.get('first_name', '')} {event['name']}".strip()
        event_type_name = event_type_labels.get(event["type"], event["type"])
        event_names.append(f"{prefix} - {event_type_name}")
    title = ", ".join(event_names)
    if len(events) > 2:
        title += "..."
    return title

class DateCountdownConfigFlow(config_entries.ConfigFlow, domain=DOMAIN):
    """Handle a config flow for Date Countdown."""

    VERSION = 1

    def __init__(self):
        """Initialize the config flow."""
        self._event_type = None

    async def async_step_user(self, user_input: Optional[Dict[str, Any]] = None) -> FlowResult:
        """Handle the initial step to select event type."""
        _LOGGER.debug("Starting async_step_user with user_input: %s", user_input)
        if user_input is not None:
            self._event_type = user_input["type"]
            _LOGGER.info("Selected event type: %s", self._event_type)
            return await self.async_step_event_details()

        event_type_options = {
            "birthday": "Anniversaire",
            "anniversary": "Anniversaire de mariage",
            "memorial": "Mémorial",
            "promotion": "Promotion",
            "special_event": "Événement spécial",
            "retirement": "Retraite"
        }

        _LOGGER.info("Showing form for step 'user' to select event type")
        return self.async_show_form(
            step_id="user",
            data_schema=vol.Schema({
                vol.Required("type", description="Type d'événement"): vol.In(event_type_options),
            }),
            description_placeholders={"date_format": DATE_FORMAT}
        )

    async def async_step_event_details(self, user_input: Optional[Dict[str, Any]] = None) -> FlowResult:
        """Handle the step to collect event details."""
        _LOGGER.debug("async_step_event_details called with user_input: %s", user_input)
        errors = {}

        if user_input is not None:
            _LOGGER.debug("Processing event details: %s", user_input)
            # Validation des dates
            if self._event_type == "retirement":
                if not re.match(r"^\d{2}/\d{2}/\d{4}$", user_input["start_date"]):
                    errors["start_date"] = "invalid_date_format"
                    _LOGGER.error("Invalid start date format: %s", user_input["start_date"])
                if not errors:
                    try:
                        day, month, year = map(int, user_input["start_date"].split('/'))
                        date(year, month, day)
                    except (ValueError, TypeError) as e:
                        errors["start_date"] = "invalid_date_format"
                        _LOGGER.error("Date validation failed for start_date %s: %s", user_input["start_date"], e)
            else:
                if not re.match(r"^\d{2}/\d{2}/\d{4}$", user_input["date"]):
                    errors["date"] = "invalid_date_format"
                    _LOGGER.error("Invalid date format: %s", user_input["date"])
                elif self._event_type == "memorial" and user_input.get("death_date"):
                    if not re.match(r"^\d{2}/\d{2}/\d{4}$", user_input["death_date"]):
                        errors["death_date"] = "invalid_memorial_date"
                        _LOGGER.error("Invalid death date format: %s", user_input["death_date"])
                    else:
                        try:
                            day, month, year = map(int, user_input["death_date"].split('/'))
                            date(year, month, day)
                        except (ValueError, TypeError) as e:
                            errors["death_date"] = "invalid_memorial_date"
                            _LOGGER.error("Date validation failed for death_date %s: %s", user_input["death_date"], e)
                if not errors:
                    try:
                        day, month, year = map(int, user_input["date"].split('/'))
                        date(year, month, day)
                    except (ValueError, TypeError) as e:
                        errors["date"] = "invalid_date_format"
                        _LOGGER.error("Date validation failed for date %s: %s", user_input["date"], e)

            if not errors:
                _LOGGER.info("Creating entry with initial event: %s", user_input)
                initial_events = [
                    {
                        "name": user_input["name"],
                        "first_name": user_input.get("first_name", ""),
                        "type": self._event_type
                    }
                ]
                if self._event_type == "retirement":
                    initial_events[0]["start_date"] = user_input["start_date"]
                    initial_events[0]["is_penible"] = user_input.get("is_penible", False)
                    initial_events[0]["career_type"] = user_input.get("career_type", "normale")
                elif self._event_type == "memorial" and user_input.get("death_date"):
                    initial_events[0]["death_date"] = user_input["death_date"]
                    initial_events[0]["date"] = user_input["date"]
                else:
                    initial_events[0]["date"] = user_input["date"]
                _LOGGER.debug("Prepared initial_events: %s", initial_events)
                try:
                    result = self.async_create_entry(
                        title=_generate_entry_title(initial_events),
                        data={},
                        options={"events": initial_events}
                    )
                    _LOGGER.info("Entry created successfully, title: %s", _generate_entry_title(initial_events))
                    return result
                except Exception as e:
                    _LOGGER.error("Failed to create entry: %s", e)
                    errors["base"] = "creation_failed"

        # Schéma pour la retraite
        if self._event_type == "retirement":
            career_type_options = {
                "longue": "Carrière longue (début avant 18 ans)",
                "normale": "Carrière normale (début après 18 ans)"
            }
            schema = {
                vol.Required("name", description="Nom de l'événement ou de la personne"): str,
                vol.Optional("first_name", description="Prénom (optionnel)"): str,
                vol.Required("start_date", description=f"Date de début du travail (format: {DATE_FORMAT})"): str,
                vol.Optional("is_penible", description="Travaux pénibles (réduit les années pour la médaille)"): bool,
                vol.Required("career_type", description="Type de carrière", default="normale"): vol.In(career_type_options)
            }
        else:
            date_label = "Date de naissance" if self._event_type == "memorial" else "Date"
            schema = {
                vol.Required("name", description="Nom de l'événement ou de la personne"): str,
                vol.Optional("first_name", description="Prénom (optionnel)"): str,
                vol.Required("date", description=f"{date_label} (format: {DATE_FORMAT})"): str,
            }
            if self._event_type == "memorial":
                schema[vol.Optional("death_date", description=f"Date de décès (format: {DATE_FORMAT})")] = str

        _LOGGER.info("Showing form for step 'event_details' with event_type: %s", self._event_type)
        return self.async_show_form(
            step_id="event_details",
            data_schema=vol.Schema(schema),
            errors=errors,
            description_placeholders={"date_format": DATE_FORMAT}
        )

    @staticmethod
    @callback
    def async_get_options_flow(config_entry: config_entries.ConfigEntry) -> config_entries.OptionsFlow:
        """Get the options flow for this handler."""
        _LOGGER.debug("Initializing options flow for config_entry: %s", config_entry.entry_id)
        return DateCountdownOptionsFlow(config_entry)

class DateCountdownOptionsFlow(config_entries.OptionsFlow):
    """Handle options flow for Date Countdown, limited to editing events."""

    def __init__(self, config_entry: config_entries.ConfigEntry):
        """Initialize options flow."""
        _LOGGER.debug("Initializing DateCountdownOptionsFlow with config_entry: %s", config_entry.entry_id)
        self._config_entry_id = config_entry.entry_id
        self.events = None
        self._event_type = None

    async def async_step_init(self, user_input: Optional[Dict[str, Any]] = None) -> FlowResult:
        """Manage the options, limited to editing."""
        _LOGGER.debug("async_step_init called with user_input: %s", user_input)
        if self.events is None:
            config_entry = self.hass.config_entries.async_get_entry(self._config_entry_id)
            if not config_entry:
                _LOGGER.error("Config entry %s not found", self._config_entry_id)
                return self.async_show_form(
                    step_id="init",
                    data_schema=vol.Schema({
                        vol.Required("action"): vol.In(["edit"])
                    }),
                    errors={"base": "config_entry_not_found"}
                )
            self.events = config_entry.options.get("events", [])
            _LOGGER.debug("Initialized events: %s", self.events)

        if not self.events:
            _LOGGER.warning("No events available for editing")
            return self.async_show_form(
                step_id="init",
                data_schema=vol.Schema({
                    vol.Required("action"): vol.In(["edit"])
                }),
                errors={"base": "no_events"}
            )

        if user_input is not None:
            action = user_input.get("action")
            _LOGGER.debug("Action selected: %s", action)
            if action != "edit":
                _LOGGER.warning("Invalid action received: %s", action)
                return self.async_show_form(
                    step_id="init",
                    data_schema=vol.Schema({
                        vol.Required("action"): vol.In(["edit"])
                    }),
                    errors={"action": "invalid_action"}
                )
            _LOGGER.info("Selected action: edit")
            return await self.async_step_select_event({})

        _LOGGER.info("Showing form for step 'init' with action: edit")
        return self.async_show_form(
            step_id="init",
            data_schema=vol.Schema({
                vol.Required("action", default="edit"): vol.In(["edit"])
            })
        )

    async def async_step_select_event(self, user_input: Optional[Dict[str, Any]] = None) -> FlowResult:
        """Handle selecting an event to edit."""
        _LOGGER.debug("async_step_select_event called with user_input: %s", user_input)
        if not self.events:
            _LOGGER.warning("No events available for selection")
            return self.async_show_form(
                step_id="init",
                data_schema=vol.Schema({
                    vol.Required("action"): vol.In(["edit"])
                }),
                errors={"base": "no_events"}
            )

        event_options = {}
        for i, event in enumerate(self.events):
            if "name" in event and "type" in event:
                event_options[str(i)] = f"{event['name']} ({event['type']})"
            else:
                _LOGGER.warning("Invalid event at index %s: %s", i, event)
                continue

        if not event_options:
            _LOGGER.error("No valid events found for selection")
            return self.async_show_form(
                step_id="init",
                data_schema=vol.Schema({
                    vol.Required("action"): vol.In(["edit"])
                }),
                errors={"base": "no_events"}
            )

        if user_input is not None:
            if "event" not in user_input or user_input["event"] not in event_options:
                _LOGGER.warning("No valid event selected in user_input: %s", user_input)
                return self.async_show_form(
                    step_id="select_event",
                    data_schema=vol.Schema({
                        vol.Required("event"): vol.In(event_options),
                    }),
                    errors={"event": "event_required"}
                )

            event_index = int(user_input["event"])
            _LOGGER.info("Selected event index: %s for editing", event_index)
            self._event_type = self.events[event_index]["type"]
            return await self.async_step_edit_event_type({"event_index": event_index})

        _LOGGER.info("Showing form for step 'select_event' with %d options", len(event_options))
        return self.async_show_form(
            step_id="select_event",
            data_schema=vol.Schema({
                vol.Required("event"): vol.In(event_options),
            })
        )

    async def async_step_edit_event_type(self, user_input: Optional[Dict[str, Any]] = None) -> FlowResult:
        """Handle selecting the event type for editing an event."""
        _LOGGER.debug("async_step_edit_event_type called with user_input: %s", user_input)
        event_index = user_input.get("event_index", 0)
        if user_input is not None and "type" in user_input:
            self._event_type = user_input["type"]
            _LOGGER.info("Selected event type for edit: %s", self._event_type)
            user_input["event_index"] = event_index
            return await self.async_step_edit_event(user_input)

        event = self.events[event_index]
        event_type_options = {
            "birthday": "Anniversaire",
            "anniversary": "Anniversaire de mariage",
            "memorial": "Mémorial",
            "promotion": "Promotion",
            "special_event": "Événement spécial",
            "retirement": "Retraite"
        }

        return self.async_show_form(
            step_id="edit_event_type",
            data_schema=vol.Schema({
                vol.Required("type", description="Type d'événement", default=event["type"]): vol.In(event_type_options),
            }),
            description_placeholders={"date_format": DATE_FORMAT}
        )

    async def async_step_edit_event(self, user_input: Optional[Dict[str, Any]] = None) -> FlowResult:
        """Handle editing an event."""
        _LOGGER.debug("async_step_edit_event called with user_input: %s", user_input)
        errors = {}
        event_index = user_input.get("event_index", 0)
        event = self.events[event_index]
        _LOGGER.debug("Editing event at index %s: %s", event_index, event)

        if user_input is not None:
            _LOGGER.debug("Processing edit event: %s", user_input)
            if self._event_type == "retirement":
                if not re.match(r"^\d{2}/\d{2}/\d{4}$", user_input["start_date"]):
                    errors["start_date"] = "invalid_date_format"
                    _LOGGER.error("Invalid start date format for edit: %s", user_input["start_date"])
                if not errors:
                    try:
                        day, month, year = map(int, user_input["start_date"].split('/'))
                        date(year, month, day)
                    except (ValueError, TypeError) as e:
                        errors["start_date"] = "invalid_date_format"
                        _LOGGER.error("Date validation failed for edit start_date %s: %s", user_input["start_date"], e)
            else:
                if not re.match(r"^\d{2}/\d{2}/\d{4}$", user_input["date"]):
                    errors["date"] = "invalid_date_format"
                    _LOGGER.error("Invalid date format for edit: %s", user_input["date"])
                elif self._event_type == "memorial" and user_input.get("death_date"):
                    if not re.match(r"^\d{2}/\d{2}/\d{4}$", user_input["death_date"]):
                        errors["death_date"] = "invalid_memorial_date"
                        _LOGGER.error("Invalid death date format for edit: %s", user_input["death_date"])
                    else:
                        try:
                            day, month, year = map(int, user_input["death_date"].split('/'))
                            date(year, month, day)
                        except (ValueError, TypeError) as e:
                            errors["death_date"] = "invalid_memorial_date"
                            _LOGGER.error("Date validation failed for edit death_date %s: %s", user_input["death_date"], e)
                if not errors:
                    try:
                        day, month, year = map(int, user_input["date"].split('/'))
                        date(year, month, day)
                    except (ValueError, TypeError) as e:
                        errors["date"] = "invalid_date_format"
                        _LOGGER.error("Date validation failed for edit date %s: %s", user_input["date"], e)

            if not errors:
                _LOGGER.info("Updating event at index %s: %s", event_index, user_input)
                event_data = {
                    "name": user_input["name"],
                    "first_name": user_input.get("first_name", ""),
                    "type": self._event_type
                }
                if self._event_type == "retirement":
                    event_data["start_date"] = user_input["start_date"]
                    event_data["is_penible"] = user_input.get("is_penible", False)
                    event_data["career_type"] = user_input.get("career_type", "normale")
                elif self._event_type == "memorial" and user_input.get("death_date"):
                    event_data["death_date"] = user_input["death_date"]
                    event_data["date"] = user_input["date"]
                else:
                    event_data["date"] = user_input["date"]
                self.events[event_index] = event_data
                _LOGGER.info("Updated events list: %s", self.events)
                try:
                    self.hass.config_entries.async_update_entry(
                        self.hass.config_entries.async_get_entry(self._config_entry_id),
                        title=_generate_entry_title(self.events),
                        options={"events": self.events}
                    )
                    await self.hass.config_entries.async_reload(self._config_entry_id)
                    _LOGGER.info("Reloaded config entry %s after editing event", self._config_entry_id)
                    return self.async_create_entry(
                        title=_generate_entry_title(self.events),
                        data={},
                        options={"events": self.events}
                    )
                except Exception as e:
                    _LOGGER.error("Failed to update entry after editing event: %s", e)
                    errors["base"] = "update_failed"

        if self._event_type == "retirement":
            career_type_options = {
                "longue": "Carrière longue (début avant 18 ans)",
                "normale": "Carrière normale (début après 18 ans)"
            }
            schema = {
                vol.Required("name", description="Nom de l'événement ou de la personne", default=event.get("name", "")): str,
                vol.Optional("first_name", description="Prénom (optionnel)", default=event.get("first_name", "")): str,
                vol.Required("start_date", description=f"Date de début du travail (format: {DATE_FORMAT})", default=event.get("start_date", "")): str,
                vol.Optional("is_penible", description="Travaux pénibles (réduit les années pour la médaille)", default=event.get("is_penible", False)): bool,
                vol.Required("career_type", description="Type de carrière", default=event.get("career_type", "normale")): vol.In(career_type_options)
            }
        else:
            date_label = "Date de naissance" if self._event_type == "memorial" else "Date"
            schema = {
                vol.Required("name", description="Nom de l'événement ou de la personne", default=event.get("name", "")): str,
                vol.Optional("first_name", description="Prénom (optionnel)", default=event.get("first_name", "")): str,
                vol.Required("date", description=f"{date_label} (format: {DATE_FORMAT})", default=event.get("date", "")): str,
            }
            if self._event_type == "memorial":
                schema[vol.Optional("death_date", description=f"Date de décès (format: {DATE_FORMAT})", default=event.get("death_date", ""))] = str

        _LOGGER.info("Showing form for step 'edit_event' with event_type: %s", self._event_type)
        return self.async_show_form(
            step_id="edit_event",
            data_schema=vol.Schema(schema),
            errors=errors,
            description_placeholders={"date_format": DATE_FORMAT}
        )
