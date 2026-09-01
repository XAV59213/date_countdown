"""Calendar platform for Date Countdown."""
import logging
from datetime import date, datetime, timedelta, time, timezone
from typing import Optional, Callable, List

from homeassistant.components.calendar import CalendarEntity, CalendarEvent
from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant
from homeassistant.util import dt as dt_util

from .const import (
    DOMAIN,
    EVENT_TYPES,
    WEDDING_ANNIVERSARIES,
    AGE_CATEGORIES,
    AGE_CATEGORY_ICONS,
    WORK_MEDAL_LEVELS,
    WORK_MEDAL_PENIBLE_LEVELS,
)

_LOGGER = logging.getLogger(__name__)

async def async_setup_entry(hass: HomeAssistant, entry: ConfigEntry, async_add_entities: Callable) -> None:
    """Set up Date Countdown calendars from a config entry."""
    calendars = []
    events = entry.options.get("events", [])
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
            entry_id=entry.entry_id
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
        entry_id: str
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
        self._attr_name = f"{first_name} {name} - {event_type}".strip()
        self._entry_id = entry_id
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
    def device_info(self):
        """Return device information."""
        return {
            "identifiers": {(DOMAIN, self._entry_id)},
            "name": "Date Countdown",
            "manufacturer": "XAV59213"
        }

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
            try:
                retirement_date = date(retirement_year, self._event_date.month, self._event_date.day)
            except ValueError as e:
                _LOGGER.error("Invalid retirement date for %s: %s", self._attr_name, e)
                return None

            if retirement_date < today:
                # Retraite passée : indiquer comme événement terminé
                start = datetime.combine(retirement_date, time(0, 0), tzinfo=tzinfo)
                end = datetime.combine(retirement_date, time(23, 59), tzinfo=tzinfo)
                summary = f"{self._attr_name} (Retraite atteinte)"
                return CalendarEvent(start=start, end=end, summary=summary)

            # Retraite future : retourner la date de retraite
            start = datetime.combine(retirement_date, time(0, 0), tzinfo=tzinfo)
            end = datetime.combine(retirement_date, time(23, 59), tzinfo=tzinfo)
            years_worked = retirement_date.year - self._event_date.year
            work_medal = self._calculate_work_medal(years_worked)
            summary = f"{self._attr_name} (Retraite dans {years_worked} ans, Médaille: {work_medal or 'Aucune'})"
            return CalendarEvent(start=start, end=end, summary=summary)

        # Pour les autres types, retourner l'événement annuel le plus proche
        next_date = date(today.year, self._event_date.month, self._event_date.day)
        if next_date < today:
            next_date = date(today.year + 1, self._event_date.month, self._event_date.day)

        start = datetime.combine(next_date, time(0, 0), tzinfo=tzinfo)
        end = datetime.combine(next_date, time(23, 59), tzinfo=tzinfo)
        years = next_date.year - self._event_date.year
        summary = self._generate_event_summary(years)

        return CalendarEvent(start=start, end=end, summary=summary)

    def _calculate_work_medal(self, years_worked: int) -> Optional[str]:
        """Calculate the work medal based on years worked."""
        medal_levels = WORK_MEDAL_PENIBLE_LEVELS if self._is_penible else WORK_MEDAL_LEVELS
        for years_required, level in sorted(medal_levels.items()):
            if years_worked >= years_required:
                return level
        return None

    def _generate_event_summary(self, years: int) -> str:
        """Generate a summary for the calendar event based on event type and years."""
        summary = f"{self._attr_name}"
        if self._event_type == "birthday":
            age_category = None
            for (min_age, max_age), category in AGE_CATEGORIES.items():
                if min_age <= years <= max_age:
                    age_category = category
                    break
            if age_category:
                summary += f" ({years} ans, {age_category})"
            else:
                summary += f" ({years} ans)"
        elif self._event_type == "anniversary":
            wedding_type = WEDDING_ANNIVERSARIES.get(years)
            if wedding_type:
                summary += f" ({years} ans, {wedding_type})"
            else:
                summary += f" ({years} ans)"
        elif self._event_type == "memorial":
            age_if_alive = years
            years_since_death = None
            if self._death_date:
                years_since_death = date.today().year - self._death_date.year
                if (date.today().month, date.today().day) < (self._death_date.month, self._death_date.day):
                    years_since_death -= 1
            if years_since_death is not None:
                summary += f" (Âge si vivant: {age_if_alive} ans, Depuis décès: {years_since_death} ans)"
            else:
                summary += f" (Âge si vivant: {age_if_alive} ans)"
        elif self._event_type in ["promotion", "special_event"]:
            summary += f" ({years} ans)"
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
            try:
                retirement_date = date(retirement_year, self._event_date.month, self._event_date.day)
            except ValueError as e:
                _LOGGER.error("Invalid retirement date for %s: %s", self._attr_name, e)
                return []

            if start_date.date() <= retirement_date <= end_date.date():
                start = datetime.combine(retirement_date, time(0, 0), tzinfo=tzinfo)
                end = datetime.combine(retirement_date, time(23, 59), tzinfo=tzinfo)
                years_worked = retirement_date.year - self._event_date.year
                work_medal = self._calculate_work_medal(years_worked)
                summary = f"{self._attr_name} (Retraite, Médaille: {work_medal or 'Aucune'})"
                events.append(CalendarEvent(start=start, end=end, summary=summary))
            return events

        # Pour les autres types d'événements, générer des occurrences annuelles
        for year in range(start_date.year, end_year + 1):
            try:
                event_date = date(year, self._event_date.month, self._event_date.day)
            except ValueError as e:
                _LOGGER.warning("Invalid date for year %s for %s: %s", year, self._attr_name, e)
                continue

            if start_date.date() <= event_date <= end_date.date():
                start = datetime.combine(event_date, time(0, 0), tzinfo=tzinfo)
                end = datetime.combine(event_date, time(23, 59), tzinfo=tzinfo)
                years = year - self._event_date.year
                summary = self._generate_event_summary(years)
                events.append(CalendarEvent(start=start, end=end, summary=summary))

        _LOGGER.debug("Generated %d events for %s between %s and %s", len(events), self._attr_name, start_date, end_date)
        return events

    async def async_update(self) -> None:
        """Update the next event."""
        self._next_event = self.event
