"""Unité des années localisée (sans réparation des statistiques), capteurs de dates, diagnostics."""
from datetime import datetime, timedelta, timezone
import json

import pytest
from freezegun.api import FrozenDateTimeFactory
from pytest_homeassistant_custom_component.common import MockConfigEntry, async_fire_time_changed

from homeassistant.core import HomeAssistant
from homeassistant.helpers import device_registry as dr
from homeassistant.helpers import entity_registry as er
from homeassistant.util import dt as dt_util

from custom_components.date_countdown.const import DOMAIN, VERSION
from custom_components.date_countdown.diagnostics import (
    async_get_config_entry_diagnostics,
    async_get_device_diagnostics,
)
from custom_components.date_countdown.entity import device_identifier, find_device
from custom_components.date_countdown.i18n import year_unit

BIRTHDAY = {"name": "Descamps", "first_name": "Anais", "type": "birthday", "date": "15/06/2001", "gender": "female"}
MEMORIAL = {"name": "Martin", "first_name": "Jeanne", "type": "memorial", "date": "01/03/1946",
            "death_date": "10/10/2020", "gender": "female"}
WEDDING = {"name": "Paul et Marie", "type": "anniversary", "date": "20/11/2001"}
PROMOTION = {"name": "Promo", "first_name": "Léa", "type": "promotion", "date": "01/09/2020"}
SPECIAL = {"name": "Fête", "type": "special_event", "date": "14/07/2010"}
RETIREMENT = {"name": "Leroy", "first_name": "Marc", "type": "retirement", "start_date": "01/09/2000",
              "is_penible": False, "career_type": "normale"}
NOTIF = {"enabled": True, "targets": ["notify.mobile_app_anais"], "entities": ["notify.telephone_anais"],
         "time": "09:00:00", "reminder_days": 0, "persistent": False}


async def _setup(hass, freezer, events, language="fr", entry=None, when=datetime(2026, 4, 22, 12, 0), options=None):
    await hass.config.async_set_time_zone("Europe/Paris")
    hass.config.language = language
    freezer.move_to(dt_util.as_utc(when.replace(tzinfo=dt_util.get_default_time_zone())))
    if entry is None:
        entry = MockConfigEntry(domain=DOMAIN, title="Anais Descamps", data={},
                                options=options or {"events": events}, minor_version=2)
        entry.add_to_hass(hass)
    assert await hass.config_entries.async_setup(entry.entry_id)
    await hass.async_block_till_done()
    return entry


def _state(hass, domain, unique_id):
    entity_id = er.async_get(hass).async_get_entity_id(domain, DOMAIN, unique_id)
    assert entity_id, unique_id
    return hass.states.get(entity_id)


# --- Unité des années ------------------------------------------------------------

def test_year_unit():
    assert year_unit("fr") == "ans"
    assert year_unit("fr-CA") == "ans"
    assert year_unit("pt-BR") == "anos"
    assert year_unit("de") == "Jahre"
    assert year_unit("en-GB") == "years"
    assert year_unit("xx") == "years"
    assert year_unit(None) == "years"


@pytest.mark.parametrize(("language", "unit"), [("fr", "ans"), ("en", "years"), ("de", "Jahre"), ("pl", "lat")])
async def test_years_unit_follows_language(hass: HomeAssistant, freezer: FrozenDateTimeFactory, language, unit):
    await _setup(hass, freezer, [BIRTHDAY, RETIREMENT, MEMORIAL], language)
    for uid in ("birthday_descamps_15062001_age", "birthday_descamps_15062001_next_age",
                "retirement_leroy_01092000_years_worked", "memorial_martin_01031946_age_if_alive",
                "memorial_martin_01031946_years_since_death"):
        state = _state(hass, "sensor", uid)
        assert state.attributes["unit_of_measurement"] == unit, uid
        assert state.attributes["state_class"] == "measurement"
    # Les jours restent en « d » (durée, convertible) 
    assert _state(hass, "sensor", "birthday_descamps_15062001_days_remaining").attributes["unit_of_measurement"] == "d"


# --- Capteurs de dates ----------------------------------------------------------

@pytest.mark.parametrize(
    ("event", "key", "name", "value"),
    [
        (BIRTHDAY, "birth_date", "Anais Descamps - Anniversaire Date de naissance", "2001-06-15"),
        (MEMORIAL, "birth_date", "Jeanne Martin - Mémorial Date de naissance", "1946-03-01"),
        (MEMORIAL, "death_date", "Jeanne Martin - Mémorial Date de décès", "2020-10-10"),
        (WEDDING, "wedding_date", "Paul et Marie - Anniversaire de mariage Date du mariage", "2001-11-20"),
        (PROMOTION, "promotion_date", "Léa Promo - Promotion Date de la promotion", "2020-09-01"),
        (SPECIAL, "event_date", "Fête - Événement spécial Date de l'événement", "2010-07-14"),
        (RETIREMENT, "start_date", "Marc Leroy - Retraite Date de début de carrière", "2000-09-01"),
    ],
)
async def test_origin_date_sensors(hass: HomeAssistant, freezer: FrozenDateTimeFactory, event, key, name, value):
    from custom_components.date_countdown.entity import event_unique_id

    await _setup(hass, freezer, [event])
    state = _state(hass, "sensor", f"{event_unique_id(event)}_{key}")
    assert state.name == name
    assert state.state == value
    assert state.attributes["device_class"] == "date"


async def test_no_death_date_sensor_without_death(hass: HomeAssistant, freezer: FrozenDateTimeFactory):
    event = {k: v for k, v in MEMORIAL.items() if k != "death_date"}
    await _setup(hass, freezer, [event])
    reg = er.async_get(hass)
    assert reg.async_get_entity_id("sensor", DOMAIN, "memorial_martin_01031946_death_date") is None
    assert reg.async_get_entity_id("sensor", DOMAIN, "memorial_martin_01031946_birth_date") is not None


async def test_english_date_names(hass: HomeAssistant, freezer: FrozenDateTimeFactory):
    await _setup(hass, freezer, [WEDDING], "en")
    assert _state(hass, "sensor", "anniversary_paul_et_marie_20112001_wedding_date").name == (
        "Paul et Marie - Wedding anniversary Wedding date"
    )


# --- Diagnostics ----------------------------------------------------------------

async def test_config_entry_diagnostics(hass: HomeAssistant, freezer: FrozenDateTimeFactory):
    entry = await _setup(hass, freezer, None, options={"events": [BIRTHDAY, MEMORIAL], "notifications": NOTIF},
                         when=datetime(2026, 6, 15, 10, 0))
    freezer.tick(timedelta(seconds=60))
    async_fire_time_changed(hass)
    await hass.async_block_till_done()
    diag = await async_get_config_entry_diagnostics(hass, entry)
    dump = json.dumps(diag, default=str, ensure_ascii=False)
    for secret in ("Anais", "Descamps", "anais", "descamps", "Jeanne", "Martin", "martin", "mobile_app_anais",
                   "telephone_anais"):
        assert secret not in dump, secret
    assert diag["integration_version"] == VERSION
    assert diag["home_assistant"]["language"] == "fr"
    assert diag["entry"]["title"] == "**REDACTED**"
    assert diag["entry"]["options"]["notifications"]["targets"] == "**REDACTED**"
    assert diag["entry"]["options"]["notifications"]["entities"] == "**REDACTED**"
    assert [e["alias"] for e in diag["events"]] == ["event_1", "event_2"]
    assert diag["events"][0]["date"] == "15/06/2001"  # dates conservées
    assert diag["events"][1]["death_date"] == "10/10/2020"
    assert sorted(d["name"] for d in diag["devices"]) == ["event_1 - Anniversaire", "event_2 - Mémorial"]
    main = next(e for e in diag["entities"] if e["unique_id"] == "event_1" and e["domain"] == "sensor")
    assert main["entity_id"] == "sensor.event_1_anniversaire"
    assert main["state"] == "0"
    assert main["attributes"]["first_name"] == "**REDACTED**"
    assert main["attributes"]["friendly_name"] == "event_1 - Anniversaire"
    assert any(e["unique_id"] == "event_1_days_remaining" for e in diag["entities"])
    # Jour J à 9 h : anti-doublon de l'envoi (clé pseudonymisée)
    assert diag["notifications"]["manager_running"] is True
    assert isinstance(diag["notifications"]["sent"], dict)


async def test_device_diagnostics(hass: HomeAssistant, freezer: FrozenDateTimeFactory):
    entry = await _setup(hass, freezer, [BIRTHDAY, MEMORIAL])
    dev_reg = dr.async_get(hass)
    device = find_device(dev_reg, device_identifier(entry.entry_id, MEMORIAL), entry.entry_id)
    dev_reg.async_update_device(device.id, name_by_user="Mamie Jeanne")
    device = dev_reg.async_get(device.id)
    diag = await async_get_device_diagnostics(hass, entry, device)
    dump = json.dumps(diag, default=str, ensure_ascii=False)
    assert "Jeanne" not in dump and "Martin" not in dump and "Mamie" not in dump
    assert diag["event"]["alias"] == "event_2" and diag["event"]["type"] == "memorial"
    assert diag["device"]["name_by_user"] == "**REDACTED**"
    assert diag["device"]["model"] == "Mémorial"
    assert {e["domain"] for e in diag["entities"]} == {"sensor", "binary_sensor", "calendar"}
    assert all(e["unique_id"].startswith("event_2") for e in diag["entities"])
