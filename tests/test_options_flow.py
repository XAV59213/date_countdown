"""Parcours complet des Options (non-régression : sélection d'un événement).

Bug 1.2.19 : après « Modifier un événement » + Valider, l'écran de sélection
s'affichait directement avec l'erreur « Veuillez sélectionner un événement… »
alors que l'événement (unique) était déjà coché.
"""
import pytest
from pytest_homeassistant_custom_component.common import MockConfigEntry

from homeassistant.core import HomeAssistant
from homeassistant.data_entry_flow import FlowResultType

from custom_components.date_countdown.const import DOMAIN

ANAIS = {"name": "Descamps", "first_name": "Anais", "type": "birthday", "date": "12/03/2015"}
MEMORIAL = {
    "name": "Martin", "first_name": "Jeanne", "type": "memorial",
    "date": "02/05/1930", "death_date": "10/11/2010",
}
WEDDING = {"name": "Mariage", "first_name": "", "type": "anniversary", "date": "20/06/2009"}
RETIREMENT = {
    "name": "Descamps", "first_name": "Xavier", "type": "retirement",
    "start_date": "01/09/1995", "is_penible": False, "career_type": "normale",
}


def _entry(events, minor_version=2, notifications=None):
    """minor_version=1 : entrée créée avant 1.2.19 (migrée au démarrage)."""
    if minor_version >= 2:
        events = [{**e, "gender": "unspecified"} if e["type"] != "anniversary" else dict(e) for e in events]
    options = {"events": [dict(e) for e in events]}
    if notifications is not None:
        options["notifications"] = notifications
    return MockConfigEntry(
        domain=DOMAIN, title="Anais Descamps - Anniversaire", data={}, options=options,
        version=1, minor_version=minor_version,
    )


async def _setup(hass: HomeAssistant, entry: MockConfigEntry) -> MockConfigEntry:
    hass.config.language = "fr"
    entry.add_to_hass(hass)
    assert await hass.config_entries.async_setup(entry.entry_id)
    await hass.async_block_till_done()
    return entry


async def _open_select(hass: HomeAssistant, entry: MockConfigEntry) -> dict:
    result = await hass.config_entries.options.async_init(entry.entry_id)
    assert result["type"] is FlowResultType.FORM and result["step_id"] == "init"
    result = await hass.config_entries.options.async_configure(result["flow_id"], {"action": "edit"})
    assert result["type"] is FlowResultType.FORM and result["step_id"] == "select_event"
    return result


def _schema_field(result: dict, name: str):
    for key in result["data_schema"].schema:
        if str(key) == name:
            return key
    raise AssertionError(f"champ {name} absent")


@pytest.mark.parametrize("minor_version", [1, 2], ids=["migree-1.2.18", "neuve-1.2.19"])
@pytest.mark.parametrize("events", [[ANAIS], [ANAIS, MEMORIAL, WEDDING, RETIREMENT]], ids=["1-evenement", "plusieurs"])
async def test_select_event_shown_without_error(hass: HomeAssistant, minor_version, events):
    """L'écran de sélection ne doit PAS arriver avec une erreur déjà affichée."""
    entry = await _setup(hass, _entry(events, minor_version))
    result = await _open_select(hass, entry)
    assert not result.get("errors")
    # Le premier événement est pré-sélectionné (valeur par défaut envoyée au frontend)
    assert _schema_field(result, "event").default() == "0"


@pytest.mark.parametrize("minor_version", [1, 2], ids=["migree-1.2.18", "neuve-1.2.19"])
async def test_single_event_full_edit(hass: HomeAssistant, minor_version):
    """Sélection → type → édition → sauvegarde avec un seul événement (cas Anais)."""
    notif = {"enabled": True, "targets": ["notify.x"], "time": "09:00:00", "reminder_days": 3, "persistent": False}
    entry = await _setup(hass, _entry([ANAIS], minor_version, notif))
    result = await _open_select(hass, entry)
    result = await hass.config_entries.options.async_configure(result["flow_id"], {"event": "0"})
    assert result["step_id"] == "edit_event_type" and not result.get("errors")
    result = await hass.config_entries.options.async_configure(result["flow_id"], {"type": "birthday"})
    assert result["step_id"] == "edit_event"
    result = await hass.config_entries.options.async_configure(
        result["flow_id"],
        {"name": "Descamps", "first_name": "Anaïs", "date": "13/03/2015", "gender": "female"},
    )
    assert result["type"] is FlowResultType.CREATE_ENTRY
    await hass.async_block_till_done()
    assert entry.options["events"] == [
        {"name": "Descamps", "first_name": "Anaïs", "type": "birthday", "date": "13/03/2015", "gender": "female"}
    ]
    assert entry.options["notifications"] == notif
    assert entry.title == "Anaïs Descamps - Anniversaire"


async def test_select_event_submitted_with_defaults(hass: HomeAssistant):
    """Valider sans toucher au radio : la valeur par défaut (1er événement) suffit."""
    entry = await _setup(hass, _entry([ANAIS], 1))
    result = await _open_select(hass, entry)
    result = await hass.config_entries.options.async_configure(result["flow_id"], {})
    assert result["step_id"] == "edit_event_type" and not result.get("errors")


@pytest.mark.parametrize("minor_version", [1, 2], ids=["migree-1.2.18", "neuve-1.2.19"])
async def test_multiple_events_edit_each_type(hass: HomeAssistant, minor_version):
    """Plusieurs événements : on modifie le 2e (mémorial) puis le 4e (retraite)."""
    entry = await _setup(hass, _entry([ANAIS, MEMORIAL, WEDDING, RETIREMENT], minor_version))

    result = await _open_select(hass, entry)
    result = await hass.config_entries.options.async_configure(result["flow_id"], {"event": "1"})
    assert result["step_id"] == "edit_event_type"
    assert _schema_field(result, "type").default() == "memorial"
    result = await hass.config_entries.options.async_configure(result["flow_id"], {"type": "memorial"})
    assert result["step_id"] == "edit_event"
    result = await hass.config_entries.options.async_configure(
        result["flow_id"],
        {"name": "Martin", "first_name": "Jeanne", "date": "02/05/1930", "death_date": "11/11/2010", "gender": "female"},
    )
    assert result["type"] is FlowResultType.CREATE_ENTRY
    await hass.async_block_till_done()
    assert entry.options["events"][1]["death_date"] == "11/11/2010"
    assert entry.options["events"][1]["gender"] == "female"
    assert entry.options["events"][0]["first_name"] == "Anais"

    result = await _open_select(hass, entry)
    result = await hass.config_entries.options.async_configure(result["flow_id"], {"event": "3"})
    result = await hass.config_entries.options.async_configure(result["flow_id"], {"type": "retirement"})
    assert result["step_id"] == "edit_event"
    result = await hass.config_entries.options.async_configure(
        result["flow_id"],
        {"name": "Descamps", "first_name": "Xavier", "start_date": "01/09/1996",
         "is_penible": True, "career_type": "longue", "gender": "male"},
    )
    assert result["type"] is FlowResultType.CREATE_ENTRY
    await hass.async_block_till_done()
    assert entry.options["events"][3]["start_date"] == "01/09/1996"
    assert entry.options["events"][3]["career_type"] == "longue"
    assert len(entry.options["events"]) == 4


async def test_edit_invalid_date_then_fix(hass: HomeAssistant):
    entry = await _setup(hass, _entry([ANAIS]))
    result = await _open_select(hass, entry)
    result = await hass.config_entries.options.async_configure(result["flow_id"], {"event": "0"})
    result = await hass.config_entries.options.async_configure(result["flow_id"], {"type": "birthday"})
    result = await hass.config_entries.options.async_configure(
        result["flow_id"], {"name": "Descamps", "first_name": "Anais", "date": "31/02/2015"}
    )
    assert result["step_id"] == "edit_event" and result["errors"] == {"date": "invalid_date_format"}
    result = await hass.config_entries.options.async_configure(
        result["flow_id"], {"name": "Descamps", "first_name": "Anais", "date": "28/02/2015"}
    )
    assert result["type"] is FlowResultType.CREATE_ENTRY
    await hass.async_block_till_done()
    assert entry.options["events"][0]["date"] == "28/02/2015"


async def test_edit_change_type(hass: HomeAssistant):
    """Changer le type (anniversaire → mémorial) en cours d'édition."""
    entry = await _setup(hass, _entry([ANAIS, WEDDING]))
    result = await _open_select(hass, entry)
    result = await hass.config_entries.options.async_configure(result["flow_id"], {"event": "0"})
    result = await hass.config_entries.options.async_configure(result["flow_id"], {"type": "memorial"})
    assert "death_date" in [str(k) for k in result["data_schema"].schema]
    result = await hass.config_entries.options.async_configure(
        result["flow_id"],
        {"name": "Descamps", "first_name": "Anais", "date": "12/03/2015", "death_date": "01/01/2020"},
    )
    assert result["type"] is FlowResultType.CREATE_ENTRY
    await hass.async_block_till_done()
    assert entry.options["events"][0]["type"] == "memorial"
    assert entry.options["events"][1] == WEDDING


@pytest.mark.parametrize("minor_version", [1, 2], ids=["migree-1.2.18", "neuve-1.2.19"])
async def test_notifications_step_keeps_events(hass: HomeAssistant, minor_version):
    entry = await _setup(hass, _entry([ANAIS, MEMORIAL], minor_version))
    events_before = [dict(e) for e in entry.options["events"]]
    result = await hass.config_entries.options.async_init(entry.entry_id)
    result = await hass.config_entries.options.async_configure(result["flow_id"], {"action": "notifications"})
    assert result["step_id"] == "notifications" and not result.get("errors")
    result = await hass.config_entries.options.async_configure(
        result["flow_id"],
        {"enabled": True, "targets": [], "time": "08:00:00", "reminder_days": 2,
         "death_anniversary": True, "persistent": True},
    )
    assert result["type"] is FlowResultType.CREATE_ENTRY
    await hass.async_block_till_done()
    assert entry.options["events"] == events_before
    assert entry.options["notifications"]["persistent"] is True
    assert entry.options["notifications"]["death_anniversary"] is True
    assert entry.options["notifications"]["reminder_days"] == 2
