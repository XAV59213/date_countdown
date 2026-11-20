"""Tests des notifications natives."""
from datetime import date, datetime

import pytest
from freezegun.api import FrozenDateTimeFactory
from pytest_homeassistant_custom_component.common import MockConfigEntry, async_fire_time_changed

from homeassistant.core import HomeAssistant, ServiceCall
from homeassistant.data_entry_flow import FlowResultType
from homeassistant.helpers import entity_registry as er
from homeassistant.util import dt as dt_util

from custom_components.date_countdown.const import DOMAIN
from custom_components.date_countdown.notifications import (
    compute_due_messages,
)

BIRTHDAY = {"name": "Dupont", "first_name": "Océane", "type": "birthday", "date": "15/06/2001"}


def _entry(notifications=None, events=None):
    options = {"events": events or [BIRTHDAY]}
    if notifications is not None:
        options["notifications"] = notifications
    return MockConfigEntry(domain=DOMAIN, title="Océane Dupont - Anniversaire", data={}, options=options)


def _register_notify(hass: HomeAssistant, name: str, fail: bool = False) -> list[ServiceCall]:
    calls: list[ServiceCall] = []

    async def _handler(call: ServiceCall) -> None:
        if fail:
            raise RuntimeError("boom")
        calls.append(call)

    hass.services.async_register("notify", name, _handler)
    return calls


# --- Messages (purs) -------------------------------------------------------

@pytest.mark.parametrize(
    ("event", "today", "expected"),
    [
        (BIRTHDAY, date(2026, 6, 15), "🎂 Aujourd’hui, Océane a 25 ans ! Super-Héros des To-Do Lists"),
        (
            {"name": "Paul et Marie", "type": "anniversary", "date": "20/11/2001"},
            date(2026, 11, 20),
            "💍 Aujourd’hui, Paul et Marie fête 25 ans de mariage : Noces d'Argent !",
        ),
        (
            {"name": "Martin", "first_name": "Jean", "type": "memorial", "date": "01/03/1946", "death_date": "10/10/2020"},
            date(2026, 3, 1),
            "🕯️ Aujourd’hui, Jean aurait eu 80 ans. Disparu(e) depuis 5 ans. Une pensée en sa mémoire.",
        ),
        (
            {"name": "Dupont", "first_name": "Luc", "type": "promotion", "date": "02/09/2021"},
            date(2026, 9, 2),
            "🏆 Aujourd’hui, Luc Dupont fête 5 ans de promotion !",
        ),
        (
            {"name": "Rencontre", "type": "special_event", "date": "14/02/2016"},
            date(2026, 2, 14),
            "⭐ Aujourd’hui : Rencontre (10 ans) !",
        ),
    ],
)
def test_day_messages(event, today, expected):
    due = compute_due_messages(event, today, 0)
    assert due == [("jour_j", expected)]


def test_reminder_message():
    due = compute_due_messages(BIRTHDAY, date(2026, 6, 8), 7)
    assert due == [("rappel_7", "⏳ Dans 7 jours : anniversaire d’Océane (25 ans)")]
    assert compute_due_messages(BIRTHDAY, date(2026, 6, 9), 7) == []
    assert compute_due_messages(BIRTHDAY, date(2026, 6, 8), 0) == []


def test_retirement_only_on_the_day():
    event = {"name": "Durand", "first_name": "Alain", "type": "retirement", "start_date": "01/09/1981", "career_type": "normale"}
    # 1981 + 45 = 01/09/2026
    due = compute_due_messages(event, date(2026, 9, 1), 0)
    assert len(due) == 1 and due[0][0] == "jour_j"
    assert due[0][1].startswith("🏖️ Aujourd’hui, Alain part à la retraite après 45 ans de travail !")
    # Le capteur reste à 0 ensuite : pas de nouvelle notification
    assert compute_due_messages(event, date(2026, 9, 2), 0) == []
    assert compute_due_messages(event, date(2026, 8, 31), 0) == []


# --- Options flow ----------------------------------------------------------

async def test_options_flow_notifications(hass: HomeAssistant):
    _register_notify(hass, "mobile_app_pixel")
    entry = _entry()
    entry.add_to_hass(hass)
    assert await hass.config_entries.async_setup(entry.entry_id)
    await hass.async_block_till_done()

    result = await hass.config_entries.options.async_init(entry.entry_id)
    assert result["type"] is FlowResultType.FORM and result["step_id"] == "init"
    result = await hass.config_entries.options.async_configure(result["flow_id"], {"action": "notifications"})
    assert result["step_id"] == "notifications"

    # Activé sans cible -> erreur
    result2 = await hass.config_entries.options.async_configure(
        result["flow_id"],
        {"enabled": True, "targets": [], "time": "08:30:00", "reminder_days": 7, "persistent": False},
    )
    assert result2["errors"] == {"base": "no_notify_target"}

    result3 = await hass.config_entries.options.async_configure(
        result["flow_id"],
        {"enabled": True, "targets": ["notify.mobile_app_pixel"], "time": "08:30", "reminder_days": 7.0, "persistent": True},
    )
    assert result3["type"] is FlowResultType.CREATE_ENTRY
    await hass.async_block_till_done()
    # Migration douce : genre « non précisé » ajouté à l'événement existant
    assert entry.options["events"] == [{**BIRTHDAY, "gender": "unspecified"}]
    assert entry.options["notifications"] == {
        "enabled": True,
        "targets": ["notify.mobile_app_pixel"],
        "time": "08:30:00",
        "reminder_days": 7,
        "persistent": True,
        "entities": [],
        "death_anniversary": False,
    }


async def test_options_edit_keeps_notifications(hass: HomeAssistant):
    notif = {"enabled": True, "targets": ["notify.x"], "time": "09:00:00", "reminder_days": 0, "persistent": False}
    entry = _entry(notif)
    entry.add_to_hass(hass)
    assert await hass.config_entries.async_setup(entry.entry_id)
    await hass.async_block_till_done()

    result = await hass.config_entries.options.async_init(entry.entry_id)
    result = await hass.config_entries.options.async_configure(result["flow_id"], {"action": "edit"})
    assert result["step_id"] == "select_event"
    result = await hass.config_entries.options.async_configure(result["flow_id"], {"event": "0"})
    assert result["step_id"] == "edit_event_type"
    # Les étapes suivantes reposent sur event_index interne ; on vérifie la sauvegarde finale
    result = await hass.config_entries.options.async_configure(result["flow_id"], {"type": "birthday"})
    assert result["step_id"] == "edit_event"
    result = await hass.config_entries.options.async_configure(
        result["flow_id"], {"name": "Dupont", "first_name": "Océane", "date": "16/06/2001"}
    )
    assert result["type"] is FlowResultType.CREATE_ENTRY
    await hass.async_block_till_done()
    assert entry.options["events"][0]["date"] == "16/06/2001"
    assert entry.options["notifications"] == notif


# --- Envoi le jour J + anti-doublon ---------------------------------------

async def _setup(hass, notif):
    hass.config.language = "fr"
    entry = _entry(notif)
    entry.add_to_hass(hass)
    assert await hass.config_entries.async_setup(entry.entry_id)
    await hass.async_block_till_done()
    return entry


async def test_send_on_day_and_no_duplicate(hass: HomeAssistant, freezer: FrozenDateTimeFactory):
    await hass.config.async_set_time_zone("Europe/Paris")
    freezer.move_to(dt_util.as_utc(datetime(2026, 6, 15, 8, 0, tzinfo=dt_util.get_default_time_zone())))
    ok_calls = _register_notify(hass, "ok")
    _register_notify(hass, "ko", fail=True)
    notif = {"enabled": True, "targets": ["notify.ko", "notify.ok"], "time": "09:00:00", "reminder_days": 0, "persistent": False}
    entry = await _setup(hass, notif)
    assert ok_calls == []  # avant l'heure : rien (pas de rattrapage)

    target = dt_util.as_utc(datetime(2026, 6, 15, 9, 0, 0, tzinfo=dt_util.get_default_time_zone()))
    freezer.move_to(target)
    async_fire_time_changed(hass, target)
    await hass.async_block_till_done()
    assert len(ok_calls) == 1  # l'échec de notify.ko n'a pas bloqué notify.ok
    assert ok_calls[0].data["message"] == "🎂 Aujourd’hui, Océane a 25 ans ! Super-Héros des To-Do Lists"

    # Redémarrage (rechargement) après l'heure : déjà envoyé -> pas de doublon
    await hass.config_entries.async_reload(entry.entry_id)
    await hass.async_block_till_done()
    assert len(ok_calls) == 1


async def test_catch_up_after_restart(hass: HomeAssistant, freezer: FrozenDateTimeFactory, hass_storage):
    await hass.config.async_set_time_zone("Europe/Paris")
    freezer.move_to(dt_util.as_utc(datetime(2026, 6, 15, 14, 0, tzinfo=dt_util.get_default_time_zone())))
    calls = _register_notify(hass, "ok")
    notif = {"enabled": True, "targets": ["notify.ok"], "time": "09:00:00", "reminder_days": 0, "persistent": True}
    await _setup(hass, notif)
    assert len(calls) == 1  # rattrapage
    stored = hass_storage["date_countdown.notifications"]["data"]["sent"]
    assert any(k.endswith("|2026-06-15|jour_j") for k in stored)


async def test_service_send_test_notification(hass: HomeAssistant):
    calls = _register_notify(hass, "ok")
    notif = {"enabled": False, "targets": ["notify.ok"], "time": "09:00:00", "reminder_days": 0, "persistent": False}
    entry = await _setup(hass, notif)
    await hass.services.async_call(DOMAIN, "send_test_notification", {"entry_id": entry.entry_id}, blocking=True)
    assert len(calls) == 1
    assert calls[0].data["message"].startswith("🧪 Test – ")


async def test_service_by_entity_id(hass: HomeAssistant):
    calls = _register_notify(hass, "ok")
    notif = {"enabled": True, "targets": ["notify.ok"], "time": "23:59:59", "reminder_days": 0, "persistent": False}
    await _setup(hass, notif)
    entity_id = er.async_get(hass).async_get_entity_id("sensor", DOMAIN, "birthday_dupont_15062001")
    assert hass.states.get(entity_id).name == "Océane Dupont - Anniversaire"
    await hass.services.async_call(DOMAIN, "send_test_notification", {"entity_id": entity_id}, blocking=True)
    assert len(calls) == 1
