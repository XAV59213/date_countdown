"""Load config flow from the implementation package."""
from __future__ import annotations

import importlib.util
from pathlib import Path

_IMPL = Path(__file__).resolve().parent.parent / "date-countdown" / "config_flow.py"
_spec = importlib.util.spec_from_file_location("_date_countdown_config_flow", _IMPL)
_mod = importlib.util.module_from_spec(_spec)
assert _spec.loader is not None
_spec.loader.exec_module(_mod)

DateCountdownConfigFlow = _mod.DateCountdownConfigFlow
DateCountdownOptionsFlow = _mod.DateCountdownOptionsFlow
