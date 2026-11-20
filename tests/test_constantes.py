"""Constantes sans texte en dur : clés stables + traductions (22 langues quand c'est possible)."""
import ast
from datetime import datetime, timedelta
import json
from pathlib import Path

import pytest
from freezegun.api import FrozenDateTimeFactory
from pytest_homeassistant_custom_component.common import MockConfigEntry, async_fire_time_changed

from homeassistant.core import HomeAssistant
from homeassistant.helpers import entity_registry as er
from homeassistant.util import dt as dt_util

from custom_components.date_countdown import const
from custom_components.date_countdown.const import (
    AGE_CATEGORY_ICONS, AGE_CATEGORY_MAX, DOMAIN, WEDDING_ANNIVERSARIES, WORK_MEDAL_LEVELS, WORK_MEDAL_PENIBLE_LEVELS,
)
from custom_components.date_countdown.i18n import (
    MEDAL_KEYS, SUPPORTED, age_category, catalog_language, empty_entry_title, event_type_label, medal_key,
    medal_name, no_medal_label, notify_title, wedding_key, wedding_name,
)
from custom_components.date_countdown.i18n_data import (
    AGE_CATEGORIES_DE, AGE_CATEGORIES_EN, AGE_CATEGORIES_ES, AGE_CATEGORIES_FR, AGE_CATEGORIES_IT,
    WEDDINGS_DE, WEDDINGS_EN, WEDDINGS_ES, WEDDINGS_FR, WEDDINGS_IT,
)

ROOT = Path(__file__).resolve().parent.parent / "custom_components" / DOMAIN
LANGS = sorted(p.stem for p in (ROOT / "translations").glob("*.json"))


def _tr(lang):
    return json.loads((ROOT / "translations" / f"{lang}.json").read_text(encoding="utf-8"))


def test_const_has_only_stable_ascii_strings():
    """Plus aucun libellé (accents, espaces de phrase) dans les valeurs de const.py."""
    tree = ast.parse((ROOT / "const.py").read_text(encoding="utf-8"))
    for node in ast.walk(tree):
        if isinstance(node, ast.Constant) and isinstance(node.value, str):
            if node.value.startswith(('"""', "Constants")):
                continue
            assert node.value.isascii(), node.value
    assert not hasattr(const, "AGE_CATEGORIES") and not hasattr(const, "NOTIFY_TITLE")


def test_stable_keys():
    assert len(LANGS) == 22
    assert len(AGE_CATEGORY_ICONS) == AGE_CATEGORY_MAX + 1 and all(i.startswith("mdi:") for i in AGE_CATEGORY_ICONS)
    assert sorted(WEDDING_ANNIVERSARIES) == list(range(1, 61))
    assert len(set(WEDDING_ANNIVERSARIES.values())) == 60
    assert WEDDING_ANNIVERSARIES[25] == "silver" and WEDDING_ANNIVERSARIES[50] == "gold" and WEDDING_ANNIVERSARIES[60] == "diamond"
    for levels in (WORK_MEDAL_LEVELS, WORK_MEDAL_PENIBLE_LEVELS):
        assert list(levels.values()) == list(MEDAL_KEYS)


def test_tables_aligned():
    for table in (AGE_CATEGORIES_FR, AGE_CATEGORIES_EN, AGE_CATEGORIES_DE, AGE_CATEGORIES_ES, AGE_CATEGORIES_IT):
        assert len(table) == AGE_CATEGORY_MAX + 1 and all(table)
    for table in (WEDDINGS_FR, WEDDINGS_EN, WEDDINGS_DE, WEDDINGS_ES, WEDDINGS_IT):
        assert len(table) == 60 and all(table)


@pytest.mark.parametrize("lang", SUPPORTED)
def test_age_and_wedding_every_supported_language(lang):
    assert age_category(0, lang)
    assert age_category(AGE_CATEGORY_MAX, lang)
    assert age_category(AGE_CATEGORY_MAX + 1, lang) is None
    assert age_category(None, lang) is None
    assert all(wedding_name(y, lang) for y in range(1, 61))
    assert wedding_name(61, lang) is None and wedding_name(None, lang) is None


def test_examples_unchanged_in_french_and_english():
    assert age_category(0, "fr") == "Mini Big Bang"
    assert age_category(25, "fr") == "Super-Héros des To-Do Lists"
    assert wedding_name(25, "fr") == "Noces d'Argent"
    assert wedding_name(25, "en") == "Silver anniversary"
    assert wedding_name(25, "pl") == "Silver anniversary"  # repli anglais
    assert wedding_key(25) == "silver" and wedding_key(70) is None


@pytest.mark.parametrize("lang", LANGS)
def test_labels_in_22_languages(lang):
    data = _tr(lang)
    for key in ("birthday", "anniversary", "memorial", "promotion", "special_event", "retirement"):
        assert event_type_label(key, lang) == data["selector"]["event_type"]["options"][key]
    for key in MEDAL_KEYS:
        assert medal_name(key, lang) == data["entity"]["sensor"]["work_medal"]["state"][key]
    assert no_medal_label(lang) == data["entity"]["sensor"]["work_medal"]["state"]["none"]
    assert notify_title(lang) == data["config"]["step"]["user"]["title"]


def test_language_resolution_and_legacy_values():
    assert catalog_language("pt-BR") == "pt-BR" and catalog_language("pt_br") == "pt-BR"
    assert catalog_language("de-AT") == "de" and catalog_language("no") == "nb"
    assert catalog_language("zh-Hans") == "en" and catalog_language(None) == "en"
    assert event_type_label("birthday", "zh-Hans") == "Birthday"
    assert medal_name("gold", "pl") == "Złoty"
    # Anciennes valeurs françaises acceptées (compatibilité)
    assert medal_key("Grand Or") == "grand_gold" and medal_name("Argent", "en") == "Silver"
    assert medal_key("inconnu") is None and medal_name(None, "fr") is None
    assert empty_entry_title("fr") == "Compte à rebours d'événements (vide)"
    assert empty_entry_title("sv") == "Event countdown (empty)"


# --- Capteurs : clés stables exposées --------------------------------------

WEDDING = {"name": "Paul et Marie", "type": "anniversary", "date": "20/11/2001", "gender": "unspecified"}
BABY = {"name": "Bébé", "first_name": "Léo", "type": "birthday", "date": "10/10/2026", "gender": "male"}
RETIREMENT = {"name": "Leroy", "first_name": "Marc", "type": "retirement", "start_date": "01/09/1990",
              "is_penible": False, "career_type": "normale", "gender": "male"}


async def _setup(hass, freezer, events, language):
    await hass.config.async_set_time_zone("Europe/Paris")
    hass.config.language = language
    when = datetime(2026, 10, 3, 12, 0)
    freezer.move_to(dt_util.as_utc(when.replace(tzinfo=dt_util.get_default_time_zone())))
    entry = MockConfigEntry(domain=DOMAIN, title="Test", data={}, options={"events": events}, minor_version=2)
    entry.add_to_hass(hass)
    assert await hass.config_entries.async_setup(entry.entry_id)
    await hass.async_block_till_done()
    freezer.tick(timedelta(seconds=60))
    async_fire_time_changed(hass)
    await hass.async_block_till_done()
    return entry


def _main(hass, unique_id):
    entity_id = er.async_get(hass).async_get_entity_id("sensor", DOMAIN, unique_id)
    assert entity_id, unique_id
    return hass.states.get(entity_id)


@pytest.mark.parametrize(
    ("language", "wedding", "category"),
    [
        ("fr", "Noces d'Argent", "Mini Big Bang"),
        ("en", "Silver anniversary", "Mini Big Bang"),
        ("de", "Silberhochzeit", AGE_CATEGORIES_DE[0]),
        ("pl", "Silver anniversary", "Mini Big Bang"),  # noces / catégories : repli anglais
    ],
)
async def test_sensor_attributes_keys(hass: HomeAssistant, freezer: FrozenDateTimeFactory, language, wedding, category):
    await _setup(hass, freezer, [WEDDING, BABY, RETIREMENT], language)
    w = _main(hass, "anniversary_paul_et_marie_20112001")
    assert w.attributes["years"] == 25
    assert w.attributes["wedding_key"] == "silver"
    assert w.attributes["wedding_type"] == wedding
    r = _main(hass, "retirement_leroy_01091990")
    assert r.attributes["years_worked"] == 36
    assert r.attributes["work_medal_key"] == "gold"
    assert r.attributes["work_medal"] == _tr(catalog_language(language))["entity"]["sensor"]["work_medal"]["state"]["gold"]
    # Âge 0 : la catégorie existe (clé 0 gérée malgré sa valeur « fausse » en Python)
    b = _main(hass, "birthday_bébé_10102026")
    assert b.attributes["years"] == 0
    assert b.attributes["age_category"] == category
    assert b.attributes["icon"] == AGE_CATEGORY_ICONS[0]
