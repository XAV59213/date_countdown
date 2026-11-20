"""Notifications modernes, genre, anniversaire du décès, langues (1.2.19)."""
from datetime import date, datetime, timedelta

import pytest
from freezegun.api import FrozenDateTimeFactory
from pytest_homeassistant_custom_component.common import MockConfigEntry, async_fire_time_changed

from homeassistant import config_entries
from homeassistant.core import HomeAssistant, ServiceCall
from homeassistant.data_entry_flow import FlowResultType
from homeassistant.helpers import entity_registry as er
from homeassistant.util import dt as dt_util

from custom_components.date_countdown.const import DOMAIN
from custom_components.date_countdown.i18n import age_category, resolve_language, wedding_name
from custom_components.date_countdown.notifications import compute_due_messages

BIRTHDAY = {"name": "Dupont", "first_name": "Océane", "type": "birthday", "date": "15/06/2001"}
MEMORIAL = {"name": "Martin", "first_name": "Jeanne", "type": "memorial", "date": "01/03/1946",
            "death_date": "10/10/2020", "gender": "female"}


# --- Langues ---------------------------------------------------------------

def test_resolve_language():
    assert resolve_language("fr") == "fr"
    assert resolve_language("fr-CA") == "fr"
    assert resolve_language("pt-BR") == "en"  # repli anglais
    assert resolve_language(None) == "en"
    assert resolve_language("de") == "de"


def test_messages_english_and_german():
    assert compute_due_messages(BIRTHDAY, date(2026, 6, 15), 0, "en") == [
        ("jour_j", "🎂 Today, Océane turns 25! Superhero of To-Do Lists")
    ]
    assert compute_due_messages(BIRTHDAY, date(2026, 6, 8), 7, "en") == [
        ("rappel_7", "⏳ In 7 days: Océane’s birthday (25 years)")
    ]
    assert compute_due_messages(BIRTHDAY, date(2026, 6, 15), 0, "de")[0][1].startswith("🎂 Heute wird Océane 25!")
    wedding = {"name": "Paul et Marie", "type": "anniversary", "date": "20/11/2001"}
    assert compute_due_messages(wedding, date(2026, 11, 20), 0, "en") == [
        ("jour_j", "💍 Today, Paul et Marie celebrate 25 years of marriage: Silver anniversary!")
    ]


def test_categories_translated_and_gendered():
    assert age_category(25, "fr", "female") == "Super-Héroïne des To-Do Lists"
    assert age_category(5, "fr", "female") == "Reine des Toboggans"
    assert age_category(5, "fr", "male") == "Roi des Toboggans"
    assert age_category(5, "en", "female") == "Queen of the Slides"
    assert wedding_name(50, "en") == "Gold anniversary"
    assert wedding_name(50, "fr") == "Noces d'Or"


# --- Genre -----------------------------------------------------------------

def test_gendered_texts():
    msg = compute_due_messages(MEMORIAL, date(2026, 3, 1), 0, "fr")[0][1]
    assert msg == "🕯️ Aujourd’hui, Jeanne aurait eu 80 ans. Disparue depuis 5 ans. Une pensée en sa mémoire."
    male = {**MEMORIAL, "first_name": "Jean", "gender": "male"}
    assert "Disparu depuis 5 ans." in compute_due_messages(male, date(2026, 3, 1), 0, "fr")[0][1]
    neutral = {k: v for k, v in MEMORIAL.items() if k != "gender"}
    assert "Disparu(e) depuis 5 ans." in compute_due_messages(neutral, date(2026, 3, 1), 0, "fr")[0][1]
    assert compute_due_messages(MEMORIAL, date(2026, 3, 1), 0, "en")[0][1].endswith("Thinking of her.")


# --- Anniversaire du décès -------------------------------------------------

def test_death_anniversary():
    today = date(2026, 10, 10)
    assert compute_due_messages(MEMORIAL, today, 0, "fr") == []  # option désactivée
    assert compute_due_messages(MEMORIAL, today, 0, "fr", True) == [
        ("anniv_deces", "🕯️ Il y a 6 ans aujourd’hui, Jeanne nous quittait. Une pensée en sa mémoire.")
    ]
    assert compute_due_messages(MEMORIAL, date(2026, 10, 3), 7, "fr", True) == [
        ("rappel_deces_7", "⏳ Dans 7 jours : anniversaire du décès de Jeanne (6 ans)")
    ]
    # Pas de notification l'année même du décès
    assert compute_due_messages(MEMORIAL, date(2020, 10, 10), 0, "fr", True) == []


def test_death_anniversary_29_february():
    event = {**MEMORIAL, "death_date": "29/02/2020"}
    assert compute_due_messages(event, date(2027, 2, 28), 0, "fr", True)[0][0] == "anniv_deces"


# --- Entités notify modernes ------------------------------------------------

def _register(hass: HomeAssistant, service: str) -> list[ServiceCall]:
    calls: list[ServiceCall] = []

    async def _handler(call: ServiceCall) -> None:
        calls.append(call)

    hass.services.async_register("notify", service, _handler)
    return calls


async def _setup(hass: HomeAssistant, options: dict, minor_version: int = 2) -> MockConfigEntry:
    entry = MockConfigEntry(domain=DOMAIN, title="Test", data={}, options=options, minor_version=minor_version)
    entry.add_to_hass(hass)
    assert await hass.config_entries.async_setup(entry.entry_id)
    await hass.async_block_till_done()
    return entry


async def test_send_to_notify_entities(hass: HomeAssistant):
    hass.config.language = "fr"
    send = _register(hass, "send_message")
    legacy = _register(hass, "mobile_app_pixel")
    hass.states.async_set("notify.telephone", "unknown")
    hass.states.async_set("notify.tablette", "unknown")
    notif = {
        "enabled": True,
        "targets": ["notify.mobile_app_pixel", "notify.tablette"],  # notify.tablette : entité, pas un service
        "entities": ["notify.telephone"],
        "time": "09:00:00", "reminder_days": 0, "persistent": False,
    }
    entry = await _setup(hass, {"events": [BIRTHDAY], "notifications": notif})
    await hass.services.async_call(DOMAIN, "send_test_notification", {"entry_id": entry.entry_id}, blocking=True)
    assert len(legacy) == 1
    assert sorted(c.data["entity_id"] for c in send) == ["notify.tablette", "notify.telephone"]
    assert send[0].data["title"] == "Souvenirs et Célébrations"
    assert send[0].data["message"].startswith("🧪 Test – ")


async def test_old_options_still_work(hass: HomeAssistant):
    """Options 1.2.17/1.2.18 (sans entities / death_anniversary) : rétro-compatibles."""
    legacy = _register(hass, "ok")
    notif = {"enabled": True, "targets": ["notify.ok"], "time": "09:00:00", "reminder_days": 0, "persistent": False}
    entry = await _setup(hass, {"events": [BIRTHDAY], "notifications": notif})
    await hass.services.async_call(DOMAIN, "send_test_notification", {"entry_id": entry.entry_id}, blocking=True)
    assert len(legacy) == 1
    assert legacy[0].data["title"] == "Memories and Celebrations"  # langue HA des tests : anglais


async def test_options_flow_entities_and_death(hass: HomeAssistant):
    hass.states.async_set("notify.telephone", "unknown")
    entry = await _setup(hass, {"events": [MEMORIAL]})
    result = await hass.config_entries.options.async_init(entry.entry_id)
    result = await hass.config_entries.options.async_configure(result["flow_id"], {"action": "notifications"})
    result = await hass.config_entries.options.async_configure(
        result["flow_id"],
        {"enabled": True, "targets": [], "entities": ["notify.telephone"], "time": "09:00",
         "reminder_days": 3, "death_anniversary": True, "persistent": False},
    )
    assert result["type"] is FlowResultType.CREATE_ENTRY
    await hass.async_block_till_done()
    notif = entry.options["notifications"]
    assert notif["entities"] == ["notify.telephone"]
    assert notif["death_anniversary"] is True
    assert notif["targets"] == []


async def test_death_anniversary_sent_once(hass: HomeAssistant, freezer: FrozenDateTimeFactory):
    await hass.config.async_set_time_zone("Europe/Paris")
    hass.config.language = "fr"
    freezer.move_to(dt_util.as_utc(datetime(2026, 10, 10, 10, 0, tzinfo=dt_util.get_default_time_zone())))
    calls = _register(hass, "ok")
    notif = {"enabled": True, "targets": ["notify.ok"], "time": "09:00:00", "reminder_days": 0,
             "persistent": False, "death_anniversary": True}
    entry = await _setup(hass, {"events": [MEMORIAL], "notifications": notif})
    assert [c.data["message"] for c in calls] == [
        "🕯️ Il y a 6 ans aujourd’hui, Jeanne nous quittait. Une pensée en sa mémoire."
    ]
    await hass.config_entries.async_reload(entry.entry_id)
    await hass.async_block_till_done()
    assert len(calls) == 1  # anti-doublon


# --- Config flow, genre, migration -----------------------------------------

async def test_config_flow_with_gender(hass: HomeAssistant):
    result = await hass.config_entries.flow.async_init(DOMAIN, context={"source": config_entries.SOURCE_USER})
    assert result["step_id"] == "user"
    result = await hass.config_entries.flow.async_configure(result["flow_id"], {"type": "memorial"})
    assert result["step_id"] == "event_details"
    assert "gender" in result["data_schema"].schema
    result = await hass.config_entries.flow.async_configure(
        result["flow_id"],
        {"name": "Martin", "first_name": "Jeanne", "date": "01/03/1946", "death_date": "10/10/2020", "gender": "female"},
    )
    assert result["type"] is FlowResultType.CREATE_ENTRY
    assert result["options"]["events"][0]["gender"] == "female"
    assert result["title"] == "Jeanne Martin - Memorial"  # titre dans la langue HA (anglais en test)


async def test_config_flow_no_gender_for_wedding(hass: HomeAssistant):
    result = await hass.config_entries.flow.async_init(DOMAIN, context={"source": config_entries.SOURCE_USER})
    result = await hass.config_entries.flow.async_configure(result["flow_id"], {"type": "anniversary"})
    assert "gender" not in result["data_schema"].schema


async def test_migration_adds_gender(hass: HomeAssistant):
    entry = await _setup(hass, {"events": [BIRTHDAY, {**MEMORIAL}]}, minor_version=1)
    assert entry.minor_version == 2
    assert [e["gender"] for e in entry.options["events"]] == ["unspecified", "female"]


# --- Capteurs et calendrier : langue HA ------------------------------------

async def _refresh(hass: HomeAssistant, freezer: FrozenDateTimeFactory) -> None:
    freezer.tick(timedelta(seconds=60))
    async_fire_time_changed(hass)
    await hass.async_block_till_done()


@pytest.mark.parametrize(
    ("language", "name", "category"),
    [
        ("en", "Océane Dupont - Birthday", "Superheroine of To-Do Lists"),
        ("fr", "Océane Dupont - Anniversaire", "Super-Héroïne des To-Do Lists"),
        ("de", "Océane Dupont - Geburtstag", "Superheldin der To-do-Listen"),
    ],
)
async def test_sensor_follows_language(hass: HomeAssistant, freezer: FrozenDateTimeFactory, language, name, category):
    await hass.config.async_set_time_zone("Europe/Paris")
    hass.config.language = language
    freezer.move_to(dt_util.as_utc(datetime(2026, 4, 22, 12, 0, tzinfo=dt_util.get_default_time_zone())))
    await _setup(hass, {"events": [{**BIRTHDAY, "gender": "female"}]})
    await _refresh(hass, freezer)
    entity_id = er.async_get(hass).async_get_entity_id("sensor", DOMAIN, "birthday_dupont_15062001")
    state = hass.states.get(entity_id)
    assert state.name == name
    assert state.attributes["age_category"] == category
    assert state.attributes["gender"] == "female"


async def test_memorial_attributes_and_calendar(hass: HomeAssistant, freezer: FrozenDateTimeFactory):
    await hass.config.async_set_time_zone("Europe/Paris")
    hass.config.language = "en"
    freezer.move_to(dt_util.as_utc(datetime(2026, 10, 3, 12, 0, tzinfo=dt_util.get_default_time_zone())))
    await _setup(hass, {"events": [MEMORIAL]})
    await _refresh(hass, freezer)
    reg = er.async_get(hass)
    sensor = hass.states.get(reg.async_get_entity_id("sensor", DOMAIN, "memorial_martin_01031946"))
    assert sensor.attributes["days_to_death_anniversary"] == 7
    calendar = hass.states.get(reg.async_get_entity_id("calendar", DOMAIN, "memorial_martin_01031946"))
    # Le prochain événement est l'anniversaire du décès (10/10), avant celui de naissance (01/03)
    assert calendar.attributes["message"] == "Jeanne Martin - Memorial (Anniversary of passing: 6 years)"
    assert calendar.attributes["start_time"] == "2026-10-10 00:00:00"
