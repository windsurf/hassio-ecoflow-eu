"""Per-device profile additions (v0.4.0).

One module per device model, like the device definitions in ``devices/``. Each module may
define SENSORS, NUMBERS, SWITCHES and SELECTS; ``load()`` appends them to the model tables
(only keys the model does not have yet). Everything here is disabled by default.
"""
from __future__ import annotations

import importlib
import logging
import pkgutil

_LOGGER = logging.getLogger(__name__)


def load() -> None:
    """Append every profile module to the model tables (idempotent)."""
    from ..number import NUMBER_DESCRIPTIONS_BY_MODEL
    from ..select import SELECT_DESCRIPTIONS_BY_MODEL
    from ..sensor import SENSOR_DESCRIPTIONS_BY_MODEL
    from ..switch import SWITCH_DESCRIPTIONS_BY_MODEL

    tables = (
        ("SENSORS", SENSOR_DESCRIPTIONS_BY_MODEL),
        ("NUMBERS", NUMBER_DESCRIPTIONS_BY_MODEL),
        ("SWITCHES", SWITCH_DESCRIPTIONS_BY_MODEL),
        ("SELECTS", SELECT_DESCRIPTIONS_BY_MODEL),
    )
    for info in pkgutil.iter_modules(__path__):
        try:
            mod = importlib.import_module(f".{info.name}", __name__)
        except Exception:  # noqa: BLE001 — a broken profile must never stop the integration
            _LOGGER.exception("EcoFlow: could not load profile %s", info.name)
            continue
        model = getattr(mod, "MODEL", None)
        if not model:
            continue
        for attr, table in tables:
            new = getattr(mod, attr, ())
            have = {d.key for d in table.get(model, ())}
            table[model] = tuple(table.get(model, ())) + tuple(d for d in new if d.key not in have)
