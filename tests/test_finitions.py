"""Finitions 1.2.20 : calendrier des mémoriaux, catégories et noces de/es/it, formes féminines, éditeurs."""
from datetime import datetime, timedelta
import json
from pathlib import Path
import re
import subprocess
import shutil

import pytest
from freezegun.api import FrozenDateTimeFactory
from pytest_homeassistant_custom_component.common import MockConfigEntry, async_fire_time_changed

from homeassistant.components.calendar import DOMAIN as CALENDAR_DOMAIN
from homeassistant.core import HomeAssistant
from homeassistant.helpers import entity_registry as er
from homeassistant.util import dt as dt_util

from custom_components.date_countdown.const import DOMAIN
from custom_components.date_countdown.i18n import SUPPORTED, age_category, wedding_name
from custom_components.date_countdown.i18n_data import (
    AGE_CATEGORIES_DE, AGE_CATEGORIES_ES, AGE_CATEGORIES_IT, WEDDINGS_DE, WEDDINGS_ES, WEDDINGS_IT,
)
from custom_components.date_countdown.notifications import compute_due_messages

MEMORIAL = {"name": "Martin", "first_name": "Jeanne", "type": "memorial", "date": "01/03/1946",
            "death_date": "10/10/2020", "gender": "female"}

# Titres masculins qui ne doivent plus apparaître en tête (fr/es/it) ou comme mot (en/de) au féminin
MASCULINE = {
    "fr": r"^(Super-Héros|Héros|Roi|Empereur|Maître|Sorcier|Champion|Majeur)\b|TikTokeur",
    "en": r"\b(Superhero|Hero|King|Emperor|Wizard)\b",
    "de": r"(?<![\wÀ-ÿ])(Superheld|Held|König|Kaiser|Meister|Zauberer|Sieger|Pirat|Künstler|Rebell|Philosoph|Visionär|Weiser|TikToker|Intergalaktischer)(?![\wÀ-ÿ])",
    "es": r"^(Superhéroe|Héroe|Rey|Emperador|Maestro|Mago|Campeón|Filósofo|Visionario|Sabio)\b|Intergaláctico",
    "it": r"^(Supereroe|Eroe|Re|Imperatore|Maestro|Mago|Campione|Filosofo|Visionario|Saggio)\b|Intergalattico",
}


def test_tables_complete():
    for table in (AGE_CATEGORIES_DE, AGE_CATEGORIES_ES, AGE_CATEGORIES_IT):
        assert len(table) == 121 and all(table)
    for table in (WEDDINGS_DE, WEDDINGS_ES, WEDDINGS_IT):
        assert len(table) == 60 and len(set(table)) == 60


@pytest.mark.parametrize("lang", SUPPORTED)
def test_all_categories_feminine(lang):
    """Chaque catégorie a une forme féminine correcte (identique si le titre est épicène)."""
    for age in range(121):
        fem = age_category(age, lang, "female")
        assert fem and not re.search(MASCULINE[lang], fem), (lang, age, fem)
        assert age_category(age, lang, "male") == age_category(age, lang)


@pytest.mark.parametrize(
    ("lang", "age", "male", "female"),
    [
        ("de", 5, "König der Rutschen", "Königin der Rutschen"),
        ("de", 101, "Intergalaktischer Superheld", "Intergalaktische Superheldin"),
        ("de", 8, "Lego-Meister", "Lego-Meisterin"),
        ("es", 9, "Emperador de las Cabañas", "Emperatriz de las Cabañas"),
        ("es", 57, "Gurú de los Sabios Consejos", "Gurú de los Sabios Consejos"),
        ("it", 5, "Re degli Scivoli", "Regina degli Scivoli"),
        ("it", 7, "Campione delle Rotelle", "Campionessa delle Rotelle"),
        ("fr", 11, "Pré-Ado TikTokeur", "Pré-Ado TikTokeuse"),
        ("fr", 120, "Héros Intergalactique", "Héroïne Intergalactique"),
        ("en", 120, "Intergalactic Hero", "Intergalactic Heroine"),
    ],
)
def test_category_examples(lang, age, male, female):
    assert age_category(age, lang, "male") == male
    assert age_category(age, lang, "female") == female


def test_weddings_translated():
    assert wedding_name(25, "de") == "Silberhochzeit"
    assert wedding_name(50, "de") == "Goldene Hochzeit"
    assert wedding_name(60, "de-AT") == "Diamantene Hochzeit"
    assert wedding_name(25, "es") == "Bodas de Plata"
    assert wedding_name(50, "it") == "Nozze d'Oro"
    assert wedding_name(1, "it") == "Nozze di Cotone"
    assert wedding_name(25, "pt") == "Silver anniversary"  # repli anglais


def test_notifications_use_translated_tables():
    wedding = {"name": "Paul e Maria", "type": "anniversary", "date": "20/11/2001"}
    msg = compute_due_messages(wedding, datetime(2026, 11, 20).date(), 0, "it")[0][1]
    assert "Nozze d'Argento" in msg
    birthday = {"name": "Dupont", "first_name": "Ana", "type": "birthday", "date": "15/06/2001", "gender": "female"}
    assert "Superheroína de las Listas de Tareas" in compute_due_messages(birthday, datetime(2026, 6, 15).date(), 0, "es")[0][1]


# --- Calendrier : anniversaires du décès --------------------------------------

async def _setup(hass: HomeAssistant, language: str, when: datetime, freezer: FrozenDateTimeFactory):
    await hass.config.async_set_time_zone("Europe/Paris")
    hass.config.language = language
    freezer.move_to(dt_util.as_utc(when.replace(tzinfo=dt_util.get_default_time_zone())))
    entry = MockConfigEntry(domain=DOMAIN, data={}, options={"events": [MEMORIAL]}, version=1, minor_version=2)
    entry.add_to_hass(hass)
    assert await hass.config_entries.async_setup(entry.entry_id)
    await hass.async_block_till_done()
    freezer.tick(timedelta(seconds=60))
    async_fire_time_changed(hass)
    await hass.async_block_till_done()
    return er.async_get(hass).async_get_entity_id("calendar", DOMAIN, "memorial_martin_01031946")


async def test_calendar_lists_death_anniversaries(hass: HomeAssistant, freezer: FrozenDateTimeFactory):
    entity_id = await _setup(hass, "fr", datetime(2026, 1, 5, 12), freezer)
    entity = hass.data[CALENDAR_DOMAIN].get_entity(entity_id)
    tz = dt_util.get_default_time_zone()
    result = await entity.async_get_events(hass, datetime(2019, 1, 1, tzinfo=tz), datetime(2022, 12, 31, tzinfo=tz))
    events = [(ev.start.date().isoformat(), ev.summary) for ev in result]
    # Pas d'anniversaire du décès l'année du décès, puis un par an ; tri chronologique
    assert ("2020-10-10", "Jeanne Martin - Mémorial (Anniversaire du décès : 0 ans)") not in events
    assert ("2021-10-10", "Jeanne Martin - Mémorial (Anniversaire du décès : 1 an)") in events
    assert ("2022-10-10", "Jeanne Martin - Mémorial (Anniversaire du décès : 2 ans)") in events
    assert [d for d, _ in events] == sorted(d for d, _ in events)
    assert sum("Anniversaire du décès" in s for _, s in events) == 2
    assert sum("Âge si vivant" in s for _, s in events) == 4  # 2019 à 2022


async def test_calendar_next_event_birth_first(hass: HomeAssistant, freezer: FrozenDateTimeFactory):
    entity_id = await _setup(hass, "de", datetime(2026, 1, 5, 12), freezer)
    state = hass.states.get(entity_id)
    assert state.attributes["start_time"] == "2026-03-01 00:00:00"
    assert state.attributes["message"].startswith("Jeanne Martin - Gedenktag (")


async def test_calendar_next_event_death_first(hass: HomeAssistant, freezer: FrozenDateTimeFactory):
    entity_id = await _setup(hass, "es", datetime(2026, 9, 1, 12), freezer)
    state = hass.states.get(entity_id)
    assert state.attributes["start_time"] == "2026-10-10 00:00:00"
    assert state.attributes["message"] == "Jeanne Martin - Memorial (Aniversario del fallecimiento: 6 años)"


# --- Éditeurs des cartes ------------------------------------------------------

@pytest.mark.skipif(shutil.which("node") is None, reason="node absent")
def test_card_editor_languages():
    js = Path(__file__).parents[1] / "custom_components/date_countdown/frontend/date-countdown-card.js"
    script = (
        "const s=require('fs').readFileSync(process.argv[1],'utf8');"
        "const m=s.match(/const DC_EDITOR_I18N = (\\{[\\s\\S]*?\\n\\});/);"
        "const T=eval('('+m[1]+')');const r={};for(const l in T)r[l]=Object.keys(T[l]).sort();"
        "console.log(JSON.stringify(r));"
    )
    out = json.loads(subprocess.run(["node", "-e", script, str(js)], capture_output=True, text=True, check=True).stdout)
    assert set(out) == {"fr", "en", "de", "es", "it"}
    for lang in out:
        assert out[lang] == out["en"], lang
