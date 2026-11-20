"""Capteurs supplémentaires, appareil par événement et migration de l'ancien appareil « Date Countdown »."""
from datetime import datetime, timedelta

import pytest
from freezegun.api import FrozenDateTimeFactory
from pytest_homeassistant_custom_component.common import MockConfigEntry, async_fire_time_changed

from homeassistant.core import HomeAssistant
from homeassistant.helpers import device_registry as dr
from homeassistant.helpers import entity_registry as er
from homeassistant.util import dt as dt_util

from custom_components.date_countdown.const import DOMAIN, VERSION
from custom_components.date_countdown.entity import event_unique_id, find_device

BIRTHDAY = {"name": "Descamps", "first_name": "Anais", "type": "birthday", "date": "15/06/2001", "gender": "female"}
WEDDING = {"name": "Paul et Marie", "type": "anniversary", "date": "20/11/2001", "gender": "unspecified"}
MEMORIAL = {"name": "Martin", "first_name": "Jeanne", "type": "memorial", "date": "01/03/1946",
            "death_date": "10/10/2020", "gender": "female"}
MEMORIAL_NO_DEATH = {"name": "Durand", "first_name": "Louis", "type": "memorial", "date": "05/05/1930", "gender": "male"}
PROMOTION = {"name": "Promo", "first_name": "Léa", "type": "promotion", "date": "01/09/2020", "gender": "female"}
SPECIAL = {"name": "Fête", "type": "special_event", "date": "14/07/2010", "gender": "unspecified"}
RETIREMENT = {"name": "Leroy", "first_name": "Marc", "type": "retirement", "start_date": "01/09/2000",
              "is_penible": False, "career_type": "normale", "gender": "male"}

UID = {
    "birthday": "birthday_descamps_15062001",
    "anniversary": "anniversary_paul_et_marie_20112001",
    "memorial": "memorial_martin_01031946",
    "retirement": "retirement_leroy_01092000",
}


async def _setup(hass, freezer, events, when=datetime(2026, 4, 22, 12, 0), language="fr", entry=None):
    await hass.config.async_set_time_zone("Europe/Paris")
    hass.config.language = language
    freezer.move_to(dt_util.as_utc(when.replace(tzinfo=dt_util.get_default_time_zone())))
    if entry is None:
        entry = MockConfigEntry(domain=DOMAIN, title="Test", data={}, options={"events": events}, minor_version=2)
        entry.add_to_hass(hass)
    assert await hass.config_entries.async_setup(entry.entry_id)
    await hass.async_block_till_done()
    return entry


def _entities(hass, entry):
    reg = er.async_get(hass)
    return {e.unique_id: e for e in er.async_entries_for_config_entry(reg, entry.entry_id)}


def _state(hass, entry, domain, unique_id):
    entity_id = er.async_get(hass).async_get_entity_id(domain, DOMAIN, unique_id)
    assert entity_id, unique_id
    return hass.states.get(entity_id)


async def test_device_and_birthday_sensors(hass: HomeAssistant, freezer: FrozenDateTimeFactory):
    entry = await _setup(hass, freezer, [BIRTHDAY])
    uid = UID["birthday"]
    dev_reg = dr.async_get(hass)
    device = find_device(dev_reg, (DOMAIN, f"{entry.entry_id}_{uid}"), entry.entry_id)
    assert device is not None
    assert device.name == "Anais Descamps - Anniversaire"
    assert device.model == "Anniversaire"
    assert device.manufacturer == "XAV59213"
    assert device.sw_version == VERSION
    assert device.entry_type is dr.DeviceEntryType.SERVICE

    entities = _entities(hass, entry)
    expected = {uid, f"{uid}_days_remaining", f"{uid}_next_date", f"{uid}_age", f"{uid}_next_age",
                f"{uid}_age_category", f"{uid}_birth_date", f"{uid}_today"}
    assert set(entities) == expected
    # Tout est rattaché à l'appareil de l'événement (y compris le capteur principal et le calendrier)
    assert {e.device_id for e in entities.values()} == {device.id}

    freezer.tick(timedelta(seconds=60))  # premier rafraîchissement du capteur principal (scrutation)
    async_fire_time_changed(hass)
    await hass.async_block_till_done()
    main = _state(hass, entry, "sensor", uid)
    assert main.name == "Anais Descamps - Anniversaire"  # pas de doublon
    assert main.state == "54"
    assert main.attributes["age_category"] == "Super-Héroïne des To-Do Lists"  # attributs inchangés

    days = _state(hass, entry, "sensor", f"{uid}_days_remaining")
    assert days.name == "Anais Descamps - Anniversaire Jours restants"
    assert days.state == "54"
    assert days.attributes["unit_of_measurement"] == "d"
    assert days.attributes["device_class"] == "duration"
    assert days.attributes["state_class"] == "measurement"
    assert _state(hass, entry, "sensor", f"{uid}_next_date").state == "2026-06-15"
    age = _state(hass, entry, "sensor", f"{uid}_age")
    assert age.state == "24"
    assert age.attributes["unit_of_measurement"] == "ans"  # unité localisée (1.2.23)
    assert _state(hass, entry, "sensor", f"{uid}_next_age").state == "25"
    assert _state(hass, entry, "sensor", f"{uid}_age_category").state == "Super-Héroïne des To-Do Lists"
    today = _state(hass, entry, "binary_sensor", f"{uid}_today")
    assert today.name == "Anais Descamps - Anniversaire Aujourd'hui (jour J)"
    assert today.state == "off"
    calendar = _state(hass, entry, "calendar", uid)
    assert calendar.name == "Anais Descamps - Anniversaire"


async def test_midnight_update_and_big_day(hass: HomeAssistant, freezer: FrozenDateTimeFactory):
    entry = await _setup(hass, freezer, [BIRTHDAY], when=datetime(2026, 6, 14, 23, 59, 50))
    uid = UID["birthday"]
    assert _state(hass, entry, "binary_sensor", f"{uid}_today").state == "off"
    assert _state(hass, entry, "sensor", f"{uid}_days_remaining").state == "1"
    freezer.tick(timedelta(seconds=15))  # 00:00:05, le 15/06
    async_fire_time_changed(hass)
    await hass.async_block_till_done()
    today = _state(hass, entry, "binary_sensor", f"{uid}_today")
    assert today.state == "on"
    assert today.attributes["occasion"] == "birthday"
    assert _state(hass, entry, "sensor", f"{uid}_days_remaining").state == "0"
    assert _state(hass, entry, "sensor", f"{uid}_age").state == "25"
    assert _state(hass, entry, "sensor", f"{uid}_next_date").state == "2026-06-15"


@pytest.mark.parametrize(
    ("event", "keys"),
    [
        (WEDDING, {"days_remaining", "next_date", "years_elapsed", "wedding", "wedding_date", "today"}),
        (MEMORIAL, {"days_remaining", "next_date", "age_if_alive", "years_since_death", "death_anniversary_days",
                    "birth_date", "death_date", "today"}),
        (MEMORIAL_NO_DEATH, {"days_remaining", "next_date", "age_if_alive", "birth_date", "today"}),
        (PROMOTION, {"days_remaining", "next_date", "years_elapsed", "promotion_date", "today"}),
        (SPECIAL, {"days_remaining", "next_date", "years_elapsed", "event_date", "today"}),
        (RETIREMENT, {"days_remaining", "retirement_date", "years_worked", "work_medal", "start_date", "today"}),
    ],
)
async def test_entities_by_type(hass: HomeAssistant, freezer: FrozenDateTimeFactory, event, keys):
    entry = await _setup(hass, freezer, [event])
    base = event_unique_id(event)
    uids = set(_entities(hass, entry))
    assert base in uids  # capteur principal (et calendrier)
    assert {u[len(base) + 1:] for u in uids if u != base} == keys


async def test_values_wedding_memorial_retirement(hass: HomeAssistant, freezer: FrozenDateTimeFactory):
    entry = await _setup(hass, freezer, [WEDDING, MEMORIAL, RETIREMENT], when=datetime(2026, 10, 3, 12, 0))
    w, m, r = UID["anniversary"], UID["memorial"], UID["retirement"]
    assert _state(hass, entry, "sensor", f"{w}_years_elapsed").state == "24"
    assert _state(hass, entry, "sensor", f"{w}_wedding").state == "Noces d'Argent"
    assert _state(hass, entry, "sensor", f"{m}_age_if_alive").state == "80"
    assert _state(hass, entry, "sensor", f"{m}_years_since_death").state == "5"
    death = _state(hass, entry, "sensor", f"{m}_death_anniversary_days")
    assert death.state == "7" and death.attributes["unit_of_measurement"] == "d"
    assert _state(hass, entry, "sensor", f"{r}_retirement_date").state == "2045-09-01"
    assert _state(hass, entry, "sensor", f"{r}_years_worked").state == "26"
    medal = _state(hass, entry, "sensor", f"{r}_work_medal")
    assert medal.state == "silver"
    assert medal.attributes["options"] == ["none", "silver", "vermeil", "gold", "grand_gold"]
    # 3 événements → 3 appareils distincts
    devices = dr.async_entries_for_config_entry(dr.async_get(hass), entry.entry_id)
    assert sorted(d.name for d in devices) == [
        "Jeanne Martin - Mémorial", "Marc Leroy - Retraite", "Paul et Marie - Anniversaire de mariage"
    ]
    assert sorted(d.model for d in devices) == ["Anniversaire de mariage", "Mémorial", "Retraite"]


async def test_memorial_today_on_death_anniversary(hass: HomeAssistant, freezer: FrozenDateTimeFactory):
    entry = await _setup(hass, freezer, [MEMORIAL], when=datetime(2026, 10, 10, 12, 0))
    today = _state(hass, entry, "binary_sensor", f"{UID['memorial']}_today")
    assert today.state == "on"
    assert today.attributes["occasion"] == "death_anniversary"


async def test_english(hass: HomeAssistant, freezer: FrozenDateTimeFactory):
    entry = await _setup(hass, freezer, [BIRTHDAY], language="en")
    uid = UID["birthday"]
    device = find_device(dr.async_get(hass), (DOMAIN, f"{entry.entry_id}_{uid}"), entry.entry_id)
    assert device.name == "Anais Descamps - Birthday"
    assert device.model == "Birthday"
    age = _state(hass, entry, "sensor", f"{uid}_age")
    assert age.name == "Anais Descamps - Birthday Age"
    assert age.attributes["unit_of_measurement"] == "years"


async def test_old_device_migrated(hass: HomeAssistant, freezer: FrozenDateTimeFactory):
    """L'ancien appareil « Date Countdown » est repris : même device_id, name_by_user et entity_id conservés."""
    entry = MockConfigEntry(domain=DOMAIN, title="Test", data={}, options={"events": [BIRTHDAY, WEDDING]}, minor_version=2)
    entry.add_to_hass(hass)
    dev_reg = dr.async_get(hass)
    old = dev_reg.async_get_or_create(
        config_entry_id=entry.entry_id, identifiers={(DOMAIN, entry.entry_id)},
        name="Date Countdown", manufacturer="XAV59213",
    )
    dev_reg.async_update_device(old.id, name_by_user="Anniv d'Anaïs", area_id=None)
    ent_reg = er.async_get(hass)
    ent_reg.async_get_or_create("sensor", DOMAIN, UID["birthday"], config_entry=entry,
                                suggested_object_id="anais_descamps_anniversaire")
    ent_reg.async_get_or_create("calendar", DOMAIN, UID["birthday"], config_entry=entry, device_id=old.id,
                                suggested_object_id="anais_descamps_anniversaire")

    await _setup(hass, freezer, None, entry=entry)

    device = dev_reg.async_get(old.id)
    assert device.identifiers == {(DOMAIN, f"{entry.entry_id}_{UID['birthday']}")}
    assert device.name == "Anais Descamps - Anniversaire"
    assert device.name_by_user == "Anniv d'Anaïs"  # jamais écrasé
    assert device.model == "Anniversaire" and device.sw_version == VERSION
    assert ent_reg.async_get_entity_id("sensor", DOMAIN, UID["birthday"]) == "sensor.anais_descamps_anniversaire"
    assert ent_reg.async_get_entity_id("calendar", DOMAIN, UID["birthday"]) == "calendar.anais_descamps_anniversaire"
    assert ent_reg.async_get("sensor.anais_descamps_anniversaire").device_id == old.id
    # Le second événement a son propre appareil ; plus d'appareil « Date Countdown »
    names = sorted(d.name for d in dr.async_entries_for_config_entry(dev_reg, entry.entry_id))
    assert names == ["Anais Descamps - Anniversaire", "Paul et Marie - Anniversaire de mariage"]
    assert find_device(dev_reg, (DOMAIN, entry.entry_id), entry.entry_id) is None


async def test_stale_device_detached(hass: HomeAssistant, freezer: FrozenDateTimeFactory):
    entry = MockConfigEntry(domain=DOMAIN, title="Test", data={}, options={"events": [BIRTHDAY]}, minor_version=2)
    entry.add_to_hass(hass)
    dev_reg = dr.async_get(hass)
    gone = dev_reg.async_get_or_create(
        config_entry_id=entry.entry_id, identifiers={(DOMAIN, f"{entry.entry_id}_birthday_supprime_01012000")},
        name="Ancien événement",
    )
    await _setup(hass, freezer, None, entry=entry)
    assert dev_reg.async_get(gone.id) is None


async def test_service_with_secondary_entity(hass: HomeAssistant, freezer: FrozenDateTimeFactory):
    """send_test_notification accepte aussi une entité secondaire de l'événement."""
    calls = []

    async def _handler(call):
        calls.append(call)

    hass.services.async_register("notify", "ok", _handler)
    notif = {"enabled": True, "targets": ["notify.ok"], "time": "23:59:59", "reminder_days": 0, "persistent": False}
    entry = MockConfigEntry(domain=DOMAIN, title="Test", data={},
                            options={"events": [BIRTHDAY, WEDDING], "notifications": notif}, minor_version=2)
    entry.add_to_hass(hass)
    await _setup(hass, freezer, None, entry=entry)
    entity_id = er.async_get(hass).async_get_entity_id("binary_sensor", DOMAIN, f"{UID['birthday']}_today")
    await hass.services.async_call(DOMAIN, "send_test_notification", {"entity_id": entity_id}, blocking=True)
    assert len(calls) == 1
    assert "Anais" in calls[0].data["message"]
