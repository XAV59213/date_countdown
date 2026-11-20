"""Cartes Lovelace (node) : entités secondaires → capteur principal, doublons, éditeurs."""
from pathlib import Path
import shutil
import subprocess

import pytest

ROOT = Path(__file__).parents[1]


@pytest.mark.skipif(shutil.which("node") is None, reason="node absent")
def test_cards_resolve_secondary_entities():
    result = subprocess.run(
        ["node", str(ROOT / "tests/js/resolve_test.js"),
         str(ROOT / "custom_components/date_countdown/frontend/date-countdown-card.js")],
        capture_output=True, text=True,
    )
    assert result.returncode == 0, result.stderr
    assert result.stdout.strip() == "OK"
