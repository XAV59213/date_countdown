"""Attributs utilisés par les cartes Lovelace (🔔 et date de départ en retraite)."""
from datetime import datetime, timedelta

from freezegun.api import FrozenDateTimeFactory
from pytest_homeassistant_custom_component.common import MockConfigEntry, async_fire_time_changed

from homeassistant.core import HomeAssistant
from homeassistant.util import dt as dt_util

from custom_components.date_countdown.const import DOMAIN

BIRTHDAY = {"name": "Dupont", "first_name": "Océane", "type": "birthday", "date": "15/06/2001"}
RETIREMENT = {"name": "Martin", "first_name": "Paul", "type": "retirement", "start_date": "01/09/1985"}


async def _setup(hass: HomeAssistant, freezer: FrozenDateTimeFactory, options: dict) -> None:
    entry = MockConfigEntry(domain=DOMAIN, title="Test", data={}, options=options)
    entry.add_to_hass(hass)
    assert await hass.config_entries.async_setup(entry.entry_id)
    await hass.async_block_till_done()
    # Premier rafraîchissement des capteurs (polling)
    freezer.tick(timedelta(seconds=60))
    async_fire_time_changed(hass)
    await hass.async_block_till_done()


def _by_type(hass: HomeAssistant, event_type: str):
    return next(st for st in hass.states.async_all("sensor") if st.attributes.get("event_type") == event_type)


async def test_notifications_enabled_attribute(hass: HomeAssistant, freezer: FrozenDateTimeFactory):
    await hass.config.async_set_time_zone("Europe/Paris")
    freezer.move_to(dt_util.as_utc(datetime(2026, 4, 22, 12, 0, tzinfo=dt_util.get_default_time_zone())))
    notif = {"enabled": True, "targets": ["notify.x"], "time": "09:00:00", "reminder_days": 0, "persistent": False}
    await _setup(hass, freezer, {"events": [BIRTHDAY], "notifications": notif})
    st = _by_type(hass, "birthday")
    assert st.attributes["notifications_enabled"] is True
    assert st.state == "54"
    assert st.attributes["years"] == 25


async def test_notifications_disabled_and_retirement_date(hass: HomeAssistant, freezer: FrozenDateTimeFactory):
    await hass.config.async_set_time_zone("Europe/Paris")
    freezer.move_to(dt_util.as_utc(datetime(2026, 4, 22, 12, 0, tzinfo=dt_util.get_default_time_zone())))
    await _setup(hass, freezer, {"events": [RETIREMENT]})
    st = _by_type(hass, "retirement")
    assert st.attributes["notifications_enabled"] is False
    # Carrière normale : 45 ans après le début -> 01/09/2030
    assert st.attributes["retirement_date"] == "01/09/2030"
