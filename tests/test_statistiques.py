"""Unité des années localisée : les statistiques existantes (« years ») sont renommées, sans réparation."""
from datetime import datetime, timedelta, timezone

import pytest
from freezegun.api import FrozenDateTimeFactory
from pytest_homeassistant_custom_component.common import MockConfigEntry
from pytest_homeassistant_custom_component.components.recorder.common import async_wait_recording_done

from homeassistant.core import HomeAssistant
from homeassistant.helpers import entity_registry as er

from custom_components.date_countdown.const import DOMAIN

from .test_unites_diagnostics import BIRTHDAY, _setup


@pytest.fixture(autouse=True)
def auto_enable_custom_integrations(recorder_db_url, enable_custom_integrations):
    """Le recorder doit être préparé avant hass (ordre des fixtures)."""
    yield


async def test_statistics_unit_relabelled(recorder_mock, hass: HomeAssistant, freezer: FrozenDateTimeFactory):
    """Statistiques existantes en « years » (1.2.21-1.2.22) → métadonnées renommées en « ans », sans réparation."""
    from homeassistant.components.recorder import get_instance, statistics
    from homeassistant.components.recorder.models import StatisticMeanType
    from homeassistant.helpers import issue_registry as ir

    entry = MockConfigEntry(domain=DOMAIN, title="Test", data={}, options={"events": [BIRTHDAY]}, minor_version=2)
    entry.add_to_hass(hass)
    entity_id = er.async_get(hass).async_get_or_create(
        "sensor", DOMAIN, "birthday_descamps_15062001_age", config_entry=entry, suggested_object_id="age_anais"
    ).entity_id
    start = datetime(2026, 4, 1, tzinfo=timezone.utc)
    statistics.async_import_statistics(
        hass,
        {"mean_type": StatisticMeanType.ARITHMETIC, "has_sum": False, "name": None, "source": "recorder",
         "statistic_id": entity_id, "unit_class": None, "unit_of_measurement": "years"},
        [{"start": start, "mean": 24, "min": 24, "max": 24}],
    )
    await async_wait_recording_done(hass)

    await _setup(hass, freezer, None, entry=entry)
    await async_wait_recording_done(hass)
    meta = await get_instance(hass).async_add_executor_job(
        lambda: statistics.get_metadata(hass, statistic_ids={entity_id})
    )
    assert meta[entity_id][1]["unit_of_measurement"] == "ans"
    assert hass.states.get(entity_id).attributes["unit_of_measurement"] == "ans"
    # Pas de réparation « unité modifiée » pour ce capteur
    issues = [i for i in ir.async_get(hass).issues.values() if entity_id in (i.issue_id or "")]
    assert not issues
    # Les données sont conservées
    stats = await get_instance(hass).async_add_executor_job(
        lambda: statistics.statistics_during_period(hass, start - timedelta(hours=1), None, {entity_id}, "hour", None, {"mean"})
    )
    assert stats[entity_id][0]["mean"] == 24
