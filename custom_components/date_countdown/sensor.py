"""Sensor platform for Date Countdown."""
import logging
from datetime import date
from typing import Any, Dict, Optional

from homeassistant.components.sensor import SensorEntity
from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant
from homeassistant.util import dt as dt_util

from .const import CONF_NOTIFICATIONS, CONF_NOTIFY_ENABLED, DOMAIN, EVENT_TYPES, WEDDING_ANNIVERSARIES, AGE_CATEGORIES, AGE_CATEGORY_ICONS, WORK_MEDAL_LEVELS, WORK_MEDAL_PENIBLE_LEVELS
from .date_utils import anniversary_in_year, years_elapsed
from .i18n import GENDER_UNSPECIFIED, age_category as tr_age_category, medal_name, normalize_gender, wedding_name

_LOGGER = logging.getLogger(__name__)

async def async_setup_entry(hass: HomeAssistant, entry: ConfigEntry, async_add_entities) -> None:
    """Set up Date Countdown sensors from a config entry."""
    sensors = []

    if DOMAIN not in hass.data:
        hass.data[DOMAIN] = {}

    events = entry.options.get("events", [])
    # Notifications natives actives pour cette entrée ? (exposé en attribut pour les cartes 🔔)
    notify_enabled = bool((entry.options.get(CONF_NOTIFICATIONS) or {}).get(CONF_NOTIFY_ENABLED, False))
    if not events:
        _LOGGER.warning("No events configured for Date Countdown integration. No event sensors will be created.")
    for event in events:
        if not all(key in event for key in ["name", "type"]):
            _LOGGER.error("Invalid event configuration, missing required fields: %s", event)
            continue
        if event["type"] not in EVENT_TYPES:
            _LOGGER.error("Invalid event type '%s' for event: %s", event["type"], event)
            continue

        required_keys = ["start_date"] if event["type"] == "retirement" else ["date"]
        for key in required_keys:
            if key not in event:
                _LOGGER.error("Missing required field '%s' for event: %s", key, event)
                continue

        try:
            for key in required_keys:
                day, month, year = map(int, event[key].split('/'))
                date(year, month, day)
            if event.get("death_date"):
                try:
                    day, month, year = map(int, event["death_date"].split('/'))
                    date(year, month, day)
                except (ValueError, TypeError) as e:
                    _LOGGER.error("Invalid death_date format for event %s: %s. Skipping event.", event, e)
                    continue
        except (ValueError, TypeError) as e:
            _LOGGER.error("Invalid date format for event %s: %s. Expected DD/MM/YYYY. Skipping event.", event, e)
            continue

        event_sensor = DateCountdownSensor(
            event["name"],
            event.get("first_name", ""),
            event["type"],
            event.get("date"),
            event.get("death_date"),
            event.get("start_date"),
            event.get("is_penible", False),
            event.get("career_type", "normale"),
            gender=event.get("gender", GENDER_UNSPECIFIED),
            language=hass.config.language,
        )
        event_sensor.notifications_enabled = notify_enabled
        sensors.append(event_sensor)
        _LOGGER.info("Created DateCountdownSensor with unique_id: %s", event_sensor.unique_id)

    if not sensors:
        _LOGGER.warning("No sensors were created for Date Countdown integration. Check configuration and events.")
    else:
        hass.data[DOMAIN][entry.entry_id] = {"sensors": sensors}
        async_add_entities(sensors)

async def async_unload_entry(hass: HomeAssistant, entry: ConfigEntry) -> bool:
    """Unload a config entry."""
    hass.data[DOMAIN].pop(entry.entry_id, None)
    return True

class DateCountdownSensor(SensorEntity):
    """Representation of a Date Countdown sensor."""

    def __init__(
        self,
        name: str,
        first_name: str,
        event_type: str,
        event_date: Optional[str] = None,
        death_date: Optional[str] = None,
        start_date: Optional[str] = None,
        is_penible: bool = False,
        career_type: str = "normale",
        gender: str = GENDER_UNSPECIFIED,
        language: str = "fr",
    ) -> None:
        """Initialize the sensor."""
        self._name = name
        self._first_name = first_name
        self._event_type = event_type
        self._event_date = event_date
        self._death_date = death_date
        self._start_date = start_date
        self._is_penible = is_penible
        self._career_type = career_type
        self._state = None
        self._years = None
        self._wedding_type = None
        self._age_if_alive = None
        self._years_since_death = None
        self._age_category = None
        self._years_remaining = None
        self._years_retired = None
        self._work_medal = None
        self._age_at_death = None  # Nouvelle variable pour l'âge au décès
        self._retirement_date = None
        self._days_to_death_anniversary = None
        self._gender = normalize_gender(gender)
        self._language = language
        self.notifications_enabled = False
        unique_id_base = f"{event_type}_{name.lower().replace(' ', '_')}"
        unique_id_date = (start_date or event_date or "").replace('/', '')
        self._attr_unique_id = f"{unique_id_base}_{unique_id_date}"
        # Nom traduit par Home Assistant (translations/*.json : entity.sensor.<type>.name)
        self._attr_has_entity_name = True
        self._attr_translation_key = event_type
        self._attr_translation_placeholders = {"person": self._person_label()}
        self._attr_unit_of_measurement = "days"
        self._attr_icon = {
            "birthday": "mdi:cake",
            "anniversary": "mdi:ring",
            "memorial": "mdi:candle",
            "promotion": "mdi:briefcase",
            "special_event": "mdi:star",
            "retirement": "mdi:beach"
        }.get(event_type, "mdi:calendar")
        _LOGGER.debug("Initialized DateCountdownSensor: unique_id=%s, name=%s, date=%s, start_date=%s, is_penible=%s, career_type=%s",
                      self._attr_unique_id, self._person_label(), self._event_date, self._start_date, self._is_penible, self._career_type)

    def _person_label(self) -> str:
        """« Prénom Nom » (ou le nom seul)."""
        return f"{self._first_name} {self._name}".strip() if self._first_name else self._name

    @property
    def language(self) -> str:
        """Langue des textes générés : celle de Home Assistant si l'entité est ajoutée."""
        hass = getattr(self, "hass", None)
        return (hass.config.language if hass is not None else None) or self._language

    @property
    def state(self) -> Optional[int]:
        """Return the state of the sensor (days until event)."""
        return self._state

    @property
    def extra_state_attributes(self) -> Dict[str, Any]:
        """Return the state attributes."""
        attributes = {
            "event_type": self._event_type,
            "first_name": self._first_name,
            "gender": self._gender,
            "notifications_enabled": self.notifications_enabled,
        }
        if self._event_type == "retirement":
            attributes["start_date"] = self._start_date
            attributes["is_penible"] = self._is_penible
            attributes["career_type"] = self._career_type
            if self._retirement_date is not None:
                attributes["retirement_date"] = self._retirement_date.strftime("%d/%m/%Y")
            if self._years is not None:
                attributes["years_worked"] = self._years
            if self._years_remaining is not None:
                attributes["years_remaining"] = self._years_remaining
            if self._years_retired is not None:
                attributes["years_retired"] = self._years_retired
            if self._work_medal:
                attributes["work_medal"] = medal_name(self._work_medal, self.language)
        else:
            attributes["event_date"] = self._event_date
            if self._years is not None:
                attributes["years"] = self._years
            if self._event_type == "birthday" and self._age_category:
                attributes["age_category"] = tr_age_category(self._years, self._age_category, self.language, self._gender)
            if self._event_type == "anniversary" and self._wedding_type:
                attributes["wedding_type"] = wedding_name(self._years, self._wedding_type, self.language)
            if self._event_type == "memorial":
                if self._death_date:
                    attributes["death_date"] = self._death_date
                if self._age_if_alive is not None:
                    attributes["age_if_alive"] = self._age_if_alive
                if self._years_since_death is not None:
                    attributes["years_since_death"] = self._years_since_death
                if self._age_at_death is not None:
                    attributes["age_at_death"] = self._age_at_death
                if self._days_to_death_anniversary is not None:
                    attributes["days_to_death_anniversary"] = self._days_to_death_anniversary
        _LOGGER.debug("Returning attributes for sensor %s: %s", self._attr_unique_id, attributes)
        return attributes

    async def async_update(self) -> None:
        """Update the sensor."""
        self.update_for_date(dt_util.now().date())

    def update_for_date(self, today: date) -> None:
        """Calcule l'état et les attributs pour une date donnée (réutilisé par les notifications)."""

        if self._event_type == "retirement":
            try:
                day, month, year = map(int, self._start_date.split('/'))
                start_date = date(year, month, day)
            except (ValueError, TypeError) as e:
                _LOGGER.error("Failed to parse start date %s for sensor %s: %s", self._start_date, self._attr_unique_id, e)
                self._state = None
                self._years = None
                self._years_remaining = None
                self._years_retired = None
                self._work_medal = None
                self._retirement_date = None
                return

            # Calculer les années travaillées
            self._years = years_elapsed(start_date, today)
            _LOGGER.debug("Sensor %s: Years worked calculated as %s", self._attr_unique_id, self._years)

            # Estimer la date de retraite
            if self._career_type == "longue":
                # Carrière longue : début à 17 ans, retraite à 60 ans
                age_at_start = 17
                retirement_age = 60
                years_to_retirement = retirement_age - age_at_start  # 43 ans
            else:
                # Carrière normale : début à 19 ans, retraite à 64 ans
                age_at_start = 19
                retirement_age = 64
                years_to_retirement = retirement_age - age_at_start  # 45 ans

            retirement_year = start_date.year + years_to_retirement
            retirement_date = anniversary_in_year(start_date.month, start_date.day, retirement_year)
            self._retirement_date = retirement_date

            # Gérer retraite passée ou future
            if retirement_date <= today:
                self._state = 0
                self._years_remaining = 0
                self._years_retired = years_elapsed(retirement_date, today)
                _LOGGER.debug("Sensor %s: Retirement passed, years retired=%s", self._attr_unique_id, self._years_retired)
            else:
                self._state = (retirement_date - today).days
                self._years_remaining = retirement_date.year - today.year
                if (today.month, today.day) > (retirement_date.month, retirement_date.day):
                    self._years_remaining -= 1
                self._years_retired = None
                _LOGGER.debug("Sensor %s: State=%s days, Years remaining=%s", self._attr_unique_id, self._state, self._years_remaining)

            # Déterminer la médaille du travail
            medal_levels = WORK_MEDAL_PENIBLE_LEVELS if self._is_penible else WORK_MEDAL_LEVELS
            self._work_medal = None
            for years_required, level in sorted(medal_levels.items()):
                if self._years >= years_required:
                    self._work_medal = level
                else:
                    break
            _LOGGER.debug("Sensor %s: Work medal determined as %s", self._attr_unique_id, self._work_medal)

        else:
            try:
                day, month, year = map(int, self._event_date.split('/'))
                event_date = date(year, month, day)
            except (ValueError, TypeError) as e:
                _LOGGER.error("Failed to parse event date %s for sensor %s: %s", self._event_date, self._attr_unique_id, e)
                self._state = None
                self._years = None
                self._wedding_type = None
                self._age_if_alive = None
                self._years_since_death = None
                self._age_category = None
                self._age_at_death = None
                return

            next_event = anniversary_in_year(event_date.month, event_date.day, today.year)
            if next_event < today:
                next_event = anniversary_in_year(event_date.month, event_date.day, today.year + 1)

            self._state = (next_event - today).days
            self._years = next_event.year - event_date.year
            _LOGGER.debug("Sensor %s: State=%s days, Years=%s", self._attr_unique_id, self._state, self._years)

            if self._event_type == "anniversary" and self._years in WEDDING_ANNIVERSARIES:
                self._wedding_type = WEDDING_ANNIVERSARIES[self._years]
            else:
                self._wedding_type = None

            self._days_to_death_anniversary = None
            if self._event_type == "memorial":
                self._age_if_alive = years_elapsed(event_date, today)
                if self._death_date:
                    try:
                        day, month, year = map(int, self._death_date.split('/'))
                        death_date = date(year, month, day)
                        self._years_since_death = years_elapsed(death_date, today)
                        next_death = anniversary_in_year(death_date.month, death_date.day, today.year)
                        if next_death < today:
                            next_death = anniversary_in_year(death_date.month, death_date.day, today.year + 1)
                        self._days_to_death_anniversary = (next_death - today).days
                        self._age_at_death = death_date.year - event_date.year
                        if (death_date.month, death_date.day) < (event_date.month, event_date.day):
                            self._age_at_death -= 1
                    except (ValueError, TypeError) as e:
                        _LOGGER.error("Failed to parse death date %s for sensor %s: %s", self._death_date, self._attr_unique_id, e)
                        self._years_since_death = None
                        self._age_at_death = None
                else:
                    self._years_since_death = None
                    self._age_at_death = None
            else:
                self._age_if_alive = None
                self._years_since_death = None
                self._age_at_death = None

            if self._event_type == "birthday":
                self._age_category = None
                for (min_age, max_age), category in AGE_CATEGORIES.items():
                    if min_age <= self._years <= max_age:
                        self._age_category = category
                        self._attr_icon = AGE_CATEGORY_ICONS.get(category, "mdi:cake")
                        break
                _LOGGER.debug("Sensor %s: Age category=%s", self._attr_unique_id, self._age_category)
