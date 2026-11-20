"""Sensor platform for Date Countdown."""
import logging
from datetime import date, datetime, timedelta
from typing import Any, Dict, Optional

from homeassistant.components.sensor import SensorDeviceClass, SensorEntity, SensorStateClass
from homeassistant.const import UnitOfTime
from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant, callback
from homeassistant.helpers.device_registry import DeviceInfo
from homeassistant.helpers.entity import Entity
from homeassistant.helpers.event import async_track_time_change
from homeassistant.util import dt as dt_util

from .const import (
    AGE_CATEGORY_ICONS,
    AGE_CATEGORY_MAX,
    CONF_NOTIFICATIONS,
    CONF_NOTIFY_ENABLED,
    DOMAIN,
    EVENT_TYPES,
    WEDDING_ANNIVERSARIES,
    WORK_MEDAL_LEVELS,
    WORK_MEDAL_PENIBLE_LEVELS,
)
from .date_utils import anniversary_in_year, years_elapsed
from .entity import async_event_models, event_device_info
from .i18n import GENDER_UNSPECIFIED, age_category as tr_age_category, medal_name, normalize_gender, wedding_name

_LOGGER = logging.getLogger(__name__)

async def async_setup_entry(hass: HomeAssistant, entry: ConfigEntry, async_add_entities) -> None:
    """Set up Date Countdown sensors from a config entry."""
    sensors = []

    if DOMAIN not in hass.data:
        hass.data[DOMAIN] = {}

    events = entry.options.get("events", [])
    models = await async_event_models(hass)
    extra: list[SensorEntity] = []
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
        # Rattaché à l'appareil de l'événement ; nom = nom de l'appareil (« Anais Descamps - Anniversaire »)
        device_info = event_device_info(entry.entry_id, event, models, hass.config.language)
        event_sensor._attr_device_info = device_info
        event_sensor._attr_name = None
        sensors.append(event_sensor)
        extra.extend(build_extra_sensors(event, device_info, hass.config.language))
        _LOGGER.info("Created DateCountdownSensor with unique_id: %s", event_sensor.unique_id)

    if not sensors:
        _LOGGER.warning("No sensors were created for Date Countdown integration. Check configuration and events.")
    else:
        hass.data[DOMAIN][entry.entry_id] = {"sensors": sensors}
        async_add_entities(sensors + extra)

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
                attributes["work_medal_key"] = self._work_medal
        else:
            attributes["event_date"] = self._event_date
            if self._years is not None:
                attributes["years"] = self._years
            if self._event_type == "birthday" and self._age_category is not None:
                attributes["age_category"] = tr_age_category(self._age_category, self.language, self._gender)
            if self._event_type == "anniversary" and self._wedding_type:
                attributes["wedding_type"] = wedding_name(self._years, self.language)
                attributes["wedding_key"] = self._wedding_type
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
                # Clé stable de la catégorie = l'âge (libellé traduit à l'affichage)
                if self._years is not None and 0 <= self._years <= AGE_CATEGORY_MAX:
                    self._age_category = self._years
                    self._attr_icon = AGE_CATEGORY_ICONS[self._years]
                _LOGGER.debug("Sensor %s: Age category=%s", self._attr_unique_id, self._age_category)


def new_calculator(event: dict[str, Any], language: str) -> "DateCountdownSensor":
    """Moteur de calcul (non ajouté à HA) partagé par les entités secondaires."""
    return DateCountdownSensor(
        event["name"],
        event.get("first_name", ""),
        event["type"],
        event.get("date"),
        event.get("death_date"),
        event.get("start_date"),
        event.get("is_penible", False),
        event.get("career_type", "normale"),
        gender=event.get("gender", GENDER_UNSPECIFIED),
        language=language,
    )


class DateCountdownEventEntity(Entity):
    """Base des entités secondaires : même appareil, recalcul au démarrage et à minuit."""

    _attr_has_entity_name = True
    _attr_should_poll = False

    def __init__(self, event: dict[str, Any], device_info: DeviceInfo, key: str, language: str) -> None:
        self._event = event
        self._calc = new_calculator(event, language)
        self._key = key
        self._attr_translation_key = key
        self._attr_unique_id = f"{self._calc.unique_id}_{key}"
        self._attr_device_info = device_info
        self._today: date | None = None
        self.refresh()

    def refresh(self, today: date | None = None) -> None:
        self._today = today or dt_util.now().date()
        self._calc.update_for_date(self._today)

    async def async_added_to_hass(self) -> None:
        self._calc.hass = self.hass  # langue de HA pour les textes traduits
        self.refresh()

        @callback
        def _midnight(now: datetime) -> None:
            self.refresh(dt_util.as_local(now).date())
            self.async_write_ha_state()

        self.async_on_remove(async_track_time_change(self.hass, _midnight, hour=0, minute=0, second=1))

    # Valeurs calculées communes
    def _event_date(self) -> date | None:
        try:
            day, month, year = map(int, str(self._event.get("date")).split("/"))
            return date(year, month, day)
        except (ValueError, TypeError):
            return None

    def _death(self) -> date | None:
        try:
            day, month, year = map(int, str(self._event.get("death_date")).split("/"))
            return date(year, month, day)
        except (ValueError, TypeError):
            return None


MEDAL_OPTIONS = ["none", "silver", "vermeil", "gold", "grand_gold"]


class DateCountdownExtraSensor(DateCountdownEventEntity, SensorEntity):
    """Capteur secondaire d'un événement (jours restants, prochaine date, âge…)."""

    def __init__(self, event: dict[str, Any], device_info: DeviceInfo, key: str, language: str) -> None:
        spec = EXTRA_SENSORS[key]
        self._attr_icon = spec.get("icon")
        self._attr_device_class = spec.get("device_class")
        self._attr_state_class = spec.get("state_class")
        self._attr_native_unit_of_measurement = spec.get("unit")
        if spec.get("device_class") == SensorDeviceClass.ENUM:
            self._attr_options = MEDAL_OPTIONS
        super().__init__(event, device_info, key, language)

    @property
    def native_value(self) -> Any:
        c = self._calc
        today = self._today or dt_util.now().date()
        key = self._key
        if key == "days_remaining":
            return c.state
        if key == "next_date":
            return today + timedelta(days=c.state) if c.state is not None else None
        if key == "age":
            born = self._event_date()
            return years_elapsed(born, today) if born else None
        if key == "next_age":
            return c._years
        if key == "years_elapsed":
            start = self._event_date()
            return years_elapsed(start, today) if start else None
        if key == "age_category":
            return tr_age_category(c._age_category, c.language, c._gender) if c._age_category is not None else None
        if key == "wedding":
            return wedding_name(c._years, c.language) if c._wedding_type else None
        if key == "age_if_alive":
            return c._age_if_alive
        if key == "years_since_death":
            return c._years_since_death
        if key == "death_anniversary_days":
            return c._days_to_death_anniversary
        if key == "retirement_date":
            return c._retirement_date
        if key == "years_worked":
            return c._years
        if key == "work_medal":
            return c._work_medal or "none"
        return None

    @property
    def icon(self) -> str | None:
        if self._key == "age_category" and self._calc._age_category is not None:
            return AGE_CATEGORY_ICONS[self._calc._age_category]
        return self._attr_icon


_YEARS = {"state_class": SensorStateClass.MEASUREMENT}
EXTRA_SENSORS: dict[str, dict[str, Any]] = {
    "days_remaining": {"icon": "mdi:timer-sand", "device_class": SensorDeviceClass.DURATION,
                       "unit": UnitOfTime.DAYS, "state_class": SensorStateClass.MEASUREMENT},
    "next_date": {"icon": "mdi:calendar-star", "device_class": SensorDeviceClass.DATE},
    "age": {"icon": "mdi:cake-variant", **_YEARS},
    "next_age": {"icon": "mdi:cake-variant-outline", **_YEARS},
    "age_category": {"icon": "mdi:cake"},
    "years_elapsed": {"icon": "mdi:counter", **_YEARS},
    "wedding": {"icon": "mdi:ring"},
    "age_if_alive": {"icon": "mdi:candle", **_YEARS},
    "years_since_death": {"icon": "mdi:flower-tulip", **_YEARS},
    "death_anniversary_days": {"icon": "mdi:calendar-heart", "device_class": SensorDeviceClass.DURATION,
                               "unit": UnitOfTime.DAYS, "state_class": SensorStateClass.MEASUREMENT},
    "retirement_date": {"icon": "mdi:beach", "device_class": SensorDeviceClass.DATE},
    "years_worked": {"icon": "mdi:briefcase-clock", **_YEARS},
    "work_medal": {"icon": "mdi:medal", "device_class": SensorDeviceClass.ENUM},
}

# Capteurs secondaires créés selon le type d'événement
SENSORS_BY_TYPE: dict[str, tuple[str, ...]] = {
    "birthday": ("days_remaining", "next_date", "age", "next_age", "age_category"),
    "anniversary": ("days_remaining", "next_date", "years_elapsed", "wedding"),
    "memorial": ("days_remaining", "next_date", "age_if_alive", "years_since_death", "death_anniversary_days"),
    "promotion": ("days_remaining", "next_date", "years_elapsed"),
    "special_event": ("days_remaining", "next_date", "years_elapsed"),
    "retirement": ("days_remaining", "retirement_date", "years_worked", "work_medal"),
}
_NEEDS_DEATH_DATE = ("years_since_death", "death_anniversary_days")


def extra_sensor_keys(event: dict[str, Any]) -> list[str]:
    keys = SENSORS_BY_TYPE.get(event.get("type"), ())
    return [k for k in keys if k not in _NEEDS_DEATH_DATE or event.get("death_date")]


def build_extra_sensors(event: dict[str, Any], device_info: DeviceInfo, language: str) -> list[SensorEntity]:
    return [DateCountdownExtraSensor(event, device_info, key, language) for key in extra_sensor_keys(event)]
