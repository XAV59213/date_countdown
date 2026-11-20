"""Cohérence des fichiers de traduction (clés et placeholders identiques à en.json)."""
import importlib.util
from pathlib import Path

SCRIPT = Path(__file__).resolve().parent.parent / "scripts" / "check_translations.py"


def test_translations_consistent():
    spec = importlib.util.spec_from_file_location("check_translations", SCRIPT)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    assert module.check() == []
