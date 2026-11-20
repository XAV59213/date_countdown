"""Libellés de la page de l'intégration (bouton « Ajouter un événement », section)."""
import json
from pathlib import Path

import pytest

from homeassistant.core import HomeAssistant
from homeassistant.helpers.translation import async_get_translations
from homeassistant.loader import async_get_integration

from custom_components.date_countdown.const import DOMAIN

ROOT = Path(__file__).resolve().parent.parent / "custom_components" / DOMAIN


async def test_integration_type_service(hass: HomeAssistant):
    """« service » : section « Services » au lieu de « Ponts » (hub)."""
    integration = await async_get_integration(hass, DOMAIN)
    assert integration.integration_type == "service"


@pytest.mark.parametrize(
    ("language", "label"),
    [("fr", "Ajouter un événement"), ("en", "Add event"), ("de", "Ereignis hinzufügen"), ("es", "Añadir evento")],
)
async def test_add_button_label(hass: HomeAssistant, language, label):
    """Le frontend lit component.<domaine>.config.initiate_flow.user pour le bouton d'ajout."""
    translations = await async_get_translations(hass, language, "config", {DOMAIN})
    assert translations[f"component.{DOMAIN}.config.initiate_flow.user"] == label


def test_label_in_every_language():
    files = sorted((ROOT / "translations").glob("*.json")) + [ROOT / "strings.json"]
    assert len(files) == 23
    for path in files:
        data = json.loads(path.read_text(encoding="utf-8"))
        assert data["config"]["initiate_flow"]["user"].strip(), path.name
