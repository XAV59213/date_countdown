"""Calendar platform for Date Countdown."""
import logging
from datetime import date, datetime, timedelta, time, timezone
from typing import Optional, Callable, List

from homeassistant.components.calendar import CalendarEntity, CalendarEvent
from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant
from homeassistant.helpers.device_registry import DeviceInfo
from homeassistant.util import dt as dt_util

from .const import (
    DOMAIN,
    EVENT_TYPES,
    WORK_MEDAL_LEVELS,
    WORK_MEDAL_PENIBLE_LEVELS,
)
from .entity import async_event_models, event_device_info
from .date_utils import anniversary_in_year, years_elapsed
from .i18n import GENDER_UNSPECIFIED, Texts, age_category as tr_age_category, event_type_label, medal_name, no_medal_label, wedding_name

_LOGGER = logging.getLogger(__name__)

async def async_setup_entry(hass: HomeAssistant, entry: ConfigEntry, async_add_entities: Callable) -> None:
    """Set up Date Countdown calendars from a config entry."""
    calendars = []
    events = entry.options.get("events", [])
    models = await async_event_models(hass)
    for event in events:
        name = event.get("name")
        first_name = event.get("first_name", "")
        event_type = event.get("type")
        event_date = event.get("date") or event.get("start_date")

        if not name or not event_type or not event_date:
            _LOGGER.warning("Skipping event due to missing required fields: %s", event)
            continue

        if event_type not in EVENT_TYPES:
            _LOGGER.warning("Invalid event type '%s' for event: %s", event_type, event)
            continue

        calendars.append(DateCountdownCalendar(
            name=name,
            first_name=first_name,
            event_type=event_type,
            event_date=event_date,
            death_date=event.get("death_date"),
            is_penible=event.get("is_penible", False),
            career_type=event.get("career_type", "normale"),
            entry_id=entry.entry_id,
            gender=event.get("gender", GENDER_UNSPECIFIED),
            language=hass.config.language,
            device_info=event_device_info(entry.entry_id, event, models, hass.config.language),
        ))

    if calendars:
        async_add_entities(calendars)
        _LOGGER.info("%d Date Countdown calendar(s) created", len(calendars))
    else:
        _LOGGER.warning("No valid events found to create calendars")

class DateCountdownCalendar(CalendarEntity):
    """A calendar entity for Date Countdown events."""

    def __init__(
        self,
        name: str,
        first_name: str,
        event_type: str,
        event_date: str,
        death_date: Optional[str],
        is_penible: bool,
        career_type: str,
        entry_id: str,
        gender: str = GENDER_UNSPECIFIED,
        language: str = "fr",
        device_info: Optional[DeviceInfo] = None,
    ):
        """Initialize the calendar entity."""
        self._name = name
        self._first_name = first_name
        self._event_type = event_type
        self._event_date_str = event_date
        self._death_date_str = death_date
        self._is_penible = is_penible
        self._career_type = career_type
        self._event_date = self._parse_date(event_date)
        self._death_date = self._parse_date(death_date) if death_date else None
        self._attr_unique_id = f"{event_type}_{name.lower().replace(' ', '_')}_{event_date.replace('/', '')}"
        self._gender = gender
        self._language = language
        self._attr_name = f"{f'{first_name} {name}'.strip()} - {event_type_label(event_type, language)}"
        self._entry_id = entry_id
        # Appareil de l'événement (partagé avec les capteurs) ; repli : ancien appareil de l'entrée
        self._attr_device_info = device_info or DeviceInfo(
            identifiers={(DOMAIN, entry_id)}, name="Date Countdown", manufacturer="XAV59213"
        )
        self._next_event: Optional[CalendarEvent] = None

    def _parse_date(self, date_str: str) -> Optional[date]:
        """Parse a date string in DD/MM/YYYY format."""
        try:
            day, month, year = map(int, date_str.split("/"))
            return date(year, month, day)
        except Exception as e:
            _LOGGER.error("Invalid date format for %s: %s", self._name, e)
            return None

    @property
    def event(self) -> Optional[CalendarEvent]:
        """Return the next upcoming event."""
        if not self._event_date:
            return None

        today = dt_util.now().date()
        tzinfo = dt_util.DEFAULT_TIME_ZONE

        if self._event_type == "retirement":
            # Calculer la date de retraite estimée
            if self._career_type == "longue":
                years_to_retirement = 60 - 17  # Retraite à 60 ans, début à 17 ans
            else:
                years_to_retirement = 64 - 19  # Retraite à 64 ans, début à 19 ans

            retirement_year = self._event_date.year + years_to_retirement
            retirement_date = anniversary_in_year(
                self._event_date.month, self._event_date.day, retirement_year
            )

            if retirement_date < today:
                # Retraite passée : indiquer comme événement terminé
                start = datetime.combine(retirement_date, time(0, 0), tzinfo=tzinfo)
                end = datetime.combine(retirement_date, time(23, 59), tzinfo=tzinfo)
                summary = self._t.fmt("cal_retired", name=self._attr_name)
                return CalendarEvent(start=start, end=end, summary=summary)

            # Retraite future : retourner la date de retraite
            start = datetime.combine(retirement_date, time(0, 0), tzinfo=tzinfo)
            end = datetime.combine(retirement_date, time(23, 59), tzinfo=tzinfo)
            years_worked = retirement_date.year - self._event_date.year
            work_medal = self._calculate_work_medal(years_worked)
            summary = self._t.fmt(
                "cal_retirement", name=self._attr_name, years=self._t.years(years_worked), medal=self._medal(work_medal)
            )
            return CalendarEvent(start=start, end=end, summary=summary)

        # Pour les autres types, retourner l'événement annuel le plus proche
        next_date = anniversary_in_year(self._event_date.month, self._event_date.day, today.year)
        if next_date < today:
            next_date = anniversary_in_year(
                self._event_date.month, self._event_date.day, today.year + 1
            )

        years = next_date.year - self._event_date.year
        summary = self._generate_event_summary(years)

        # Mémorial : l'anniversaire du décès peut arriver avant l'anniversaire de naissance
        death_next = self._next_death_anniversary(today)
        if death_next is not None and death_next < next_date:
            next_date = death_next
            summary = self._death_summary(death_next.year - self._death_date.year)

        start = datetime.combine(next_date, time(0, 0), tzinfo=tzinfo)
        end = datetime.combine(next_date, time(23, 59), tzinfo=tzinfo)
        return CalendarEvent(start=start, end=end, summary=summary)

    def _next_death_anniversary(self, today: date) -> Optional[date]:
        """Prochain anniversaire du décès (mémoriaux), après l'année du décès."""
        if self._event_type != "memorial" or not self._death_date:
            return None
        year = max(today.year, self._death_date.year + 1)
        candidate = anniversary_in_year(self._death_date.month, self._death_date.day, year)
        if candidate < today:
            candidate = anniversary_in_year(self._death_date.month, self._death_date.day, year + 1)
        return candidate

    def _death_summary(self, years_since: int) -> str:
        return self._t.fmt("cal_death", name=self._attr_name, since=self._t.years(years_since))

    def _calculate_work_medal(self, years_worked: int) -> Optional[str]:
        """Calculate the work medal based on years worked."""
        medal_levels = WORK_MEDAL_PENIBLE_LEVELS if self._is_penible else WORK_MEDAL_LEVELS
        for years_required, level in sorted(medal_levels.items()):
            if years_worked >= years_required:
                return level
        return None

    @property
    def _lang(self) -> str:
        hass = getattr(self, "hass", None)
        return (hass.config.language if hass is not None else None) or self._language

    @property
    def _t(self) -> Texts:
        return Texts(self._lang, self._gender)

    def _medal(self, medal: Optional[str]) -> str:
        return medal_name(medal, self._lang) if medal else no_medal_label(self._lang)

    def _generate_event_summary(self, years: int) -> str:
        """Generate a summary for the calendar event based on event type and years."""
        t = self._t
        summary = f"{self._attr_name}"
        if self._event_type == "birthday":
            age_category = tr_age_category(years, self._lang, self._gender)
            summary += f" ({t.years(years)}, {age_category})" if age_category else f" ({t.years(years)})"
        elif self._event_type == "anniversary":
            wedding_type = wedding_name(years, self._lang)
            summary += f" ({t.years(years)}, {wedding_type})" if wedding_type else f" ({t.years(years)})"
        elif self._event_type == "memorial":
            years_since_death = None
            if self._death_date:
                years_since_death = years_elapsed(self._death_date, dt_util.now().date())
            if years_since_death is not None:
                summary = t.fmt("cal_memorial", name=summary, age=t.years(years), since=t.years(years_since_death))
            else:
                summary = t.fmt("cal_memorial_nosince", name=summary, age=t.years(years))
        elif self._event_type in ["promotion", "special_event"]:
            summary += f" ({t.years(years)})"
        return summary

    async def async_get_events(self, hass: HomeAssistant, start_date: datetime, end_date: datetime) -> List[CalendarEvent]:
        """Return calendar events within the specified date range for the next 50 years."""
        if not self._event_date:
            _LOGGER.warning("No valid event date for %s, skipping event generation", self._attr_name)
            return []

        events = []
        tzinfo = dt_util.DEFAULT_TIME_ZONE
        today = dt_util.now().date()
        max_years = 50
        end_year = min(start_date.year + max_years, end_date.year)

        if self._event_type == "retirement":
            # Calculer la date de retraite
            if self._career_type == "longue":
                years_to_retirement = 60 - 17
            else:
                years_to_retirement = 64 - 19

            retirement_year = self._event_date.year + years_to_retirement
            retirement_date = anniversary_in_year(
                self._event_date.month, self._event_date.day, retirement_year
            )

            if start_date.date() <= retirement_date <= end_date.date():
                start = datetime.combine(retirement_date, time(0, 0), tzinfo=tzinfo)
                end = datetime.combine(retirement_date, time(23, 59), tzinfo=tzinfo)
                years_worked = retirement_date.year - self._event_date.year
                work_medal = self._calculate_work_medal(years_worked)
                summary = self._t.fmt("cal_retirement_event", name=self._attr_name, medal=self._medal(work_medal))
                events.append(CalendarEvent(start=start, end=end, summary=summary))
            return events

        # Pour les autres types d'événements, générer des occurrences annuelles
        for year in range(start_date.year, end_year + 1):
            event_date = anniversary_in_year(self._event_date.month, self._event_date.day, year)

            if start_date.date() <= event_date <= end_date.date():
                start = datetime.combine(event_date, time(0, 0), tzinfo=tzinfo)
                end = datetime.combine(event_date, time(23, 59), tzinfo=tzinfo)
                years = year - self._event_date.year
                summary = self._generate_event_summary(years)
                events.append(CalendarEvent(start=start, end=end, summary=summary))

            # Mémorial : anniversaire du décès (toujours affiché, texte sobre)
            if self._event_type == "memorial" and self._death_date and year > self._death_date.year:
                death_day = anniversary_in_year(self._death_date.month, self._death_date.day, year)
                if start_date.date() <= death_day <= end_date.date():
                    events.append(CalendarEvent(
                        start=datetime.combine(death_day, time(0, 0), tzinfo=tzinfo),
                        end=datetime.combine(death_day, time(23, 59), tzinfo=tzinfo),
                        summary=self._death_summary(year - self._death_date.year),
                    ))

        events.sort(key=lambda ev: ev.start)
        _LOGGER.debug("Generated %d events for %s between %s and %s", len(events), self._attr_name, start_date, end_date)
        return events

    async def async_update(self) -> None:
        """Update the next event."""
        self._next_event = self.event
