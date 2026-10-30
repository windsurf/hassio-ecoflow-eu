"""Device registry — maps serial number prefix to device model.

Usage:
    from .devices.registry import detect_model
    model = detect_model("D361XXXXXXXXXXX")
    # returns "Delta 3 1500"

When a SN prefix is unknown, returns "Unknown EcoFlow Device".
Platform files (sensor.py, switch.py, etc.) use the model string
to look up the correct description tuples.
"""
from __future__ import annotations

import logging

_LOGGER = logging.getLogger(__name__)

# SN prefix -> model name. Longest prefix wins, so a family prefix (R65) can sit
# next to a specific one (R651).
#
# Sources (details and licences: README2, "Serial prefix sources"). Only the
# serial prefix of a model is taken from them, no code and no text:
#   [R]   reported by an owner in a repository issue, or from our own devices
#   [IO]  foxthefox/ioBroker.ecoflow-mqtt, lib/ecoflow_data.js (MIT)
#   [HI]  MichelFR/ha-ecoflow-iot, KNOWN_PREFIXES.md (MIT); it cites EcoFlow
#         developer-doc example serials [E] and the EcoFlow Android app's
#         device-code registry [A]
#   [SH]  shuette42/ecoflow-energy-ha, README and const.py (MIT)
#   [ZB]  zarbjustin/uk.co.zarb.ecoflow, README and tests (GPL-3.0)
#   [P]   carried over from earlier versions, no outside source found
# Where a model shares the profile of a sibling, the comment says so: the entity
# list is then the sibling's and has not been verified on that model.
_SN_PREFIX_MAP: dict[str, str] = {
    # -- Delta 3 series ---------------------------------------------------
    "D361":  "Delta 3 1500",         # [R] own device
    "P231":  "Delta 3 1500",         # [IO][SH] base Delta 3, shares the Delta 3 profile
    "D362":  "Delta 3 Plus",         # [P]
    "P351":  "Delta 3 Plus",         # [IO][SH]
    "D381":  "Delta 3 Max",          # [P]
    "D3N1":  "Delta 3 Max",          # [HI][SH]
    "D3M1":  "Delta 3 Max Plus",     # [R][HI] shared with the Max; own flat-key profile

    # -- Delta Pro series -------------------------------------------------
    "DCAB":  "Delta Pro",            # [HI][E] sn=DCABZ...; was Delta Max before v0.4.1
    "DCEB":  "Delta Pro",            # [HI][IO]
    "DGEA":  "Delta Pro 3",          # [P]
    "MR5":   "Delta Pro 3",          # [HI][A][IO] MR51
    "Y71":   "Delta Pro Ultra",      # [HI][A]; DGEB was Delta Pro Ultra before v0.4.1
    "DGEB":  "Smart Generator",      # [IO] README: "DGEB...." is the generator; no profile yet

    # -- Delta 2 series ---------------------------------------------------
    "R33":   "Delta 2",              # [HI][E][IO] R331
    "R35":   "Delta 2 Max",          # [HI][A][IO] R351

    # -- Delta (generation 1) ---------------------------------------------
    "DAAB":  "Delta Max",            # [R] issue #3, firmware V1.6.2.89
    "DAEB":  "Delta Max",            # [IO] listed for Delta, Delta Max and Delta Mini alike; was Delta Pro
    "DAAZ":  "Delta Mini",           # [P]
    "DBEB":  "Delta Mini",           # [R] issue #2
    "DBKB":  "Delta Mini",           # [R] diagnostics dump
    "DBAB":  "Delta Mini",           # [HI] field-observed; REST answers error 1006 (MQTT only)

    # -- River 3 series ---------------------------------------------------
    "R64":   "River 3",              # [P] R641
    "R65":   "River 3",              # [R][SH][IO] R651 (issue #4), R655
    "R63":   "River 3 Plus",         # [SH][IO][R] R631 (issue #1)

    # -- River 2 series ---------------------------------------------------
    "R60":   "River 2",              # [HI] field-observed (256 Wh); R601/R602 below stay River Max/Pro [P]
    "R61":   "River 2 Max",          # [HI][SH] R611
    "R62":   "River 2 Pro",          # [HI][A]; R621 was River 2 before v0.4.1

    # -- River (generation 1) ---------------------------------------------
    "R601":  "River Max",            # [P] conflicts with R60 = River 2 [HI]; unverified
    "R602":  "River Pro",            # [P] idem
    "R501":  "River Mini",           # [P]

    # -- Stream series ----------------------------------------------------
    "BK11":  "Stream Ultra",         # [SH][ZB][IO]
    "BK12":  "Stream Ultra",         # [ZB][HI] Stream Pro; shares the Stream Ultra profile
    "BK31":  "Stream AC Pro",        # [SH][ZB][IO]
    "BK41":  "Stream AC Pro",        # [SH][ZB] Stream Max (AC-coupled); shares the Stream AC Pro profile
    "BK51":  "Stream AC",            # [SH][ZB]
    "BK61":  "Stream Ultra",         # [SH][ZB][IO] Stream Ultra X; shares the Stream Ultra profile
    "BK01":  "Stream Microinverter", # [SH][ZB] no profile yet
    "BK21":  "Smart Meter",          # [HI][IO][ZB] no profile yet

    # -- PowerStream and Smart Plug ---------------------------------------
    "HW51":  "PowerStream",          # [HI][A][IO] 600 W and 800 W alike; HW52 was PowerStream 800W before v0.4.1
    "HW52":  "Smart Plug",           # [HI][A][IO]

    # -- Smart Home Panel -------------------------------------------------
    "SH10":  "Smart Home Panel",     # [IO]
    "SP10":  "Smart Home Panel",     # [HI] medium confidence; was Smart Plug before v0.4.1
    "SH20":  "Smart Home Panel 2",   # [IO]
    "HD3":   "Smart Home Panel 2",   # [HI][A]

    # -- PowerKit ---------------------------------------------------------
    "M10":   "PowerKit",             # [HI][A][IO] M106

    # -- PowerOcean -------------------------------------------------------
    # Read-only stubs; the decoder follows when test data is available.
    "HJ3":   "PowerOcean",           # [HI][A][IO] HJ31
    "J32":   "PowerOcean",           # [HI][SH] J327, J32D, J32E
    "HC31":  "PowerOcean Fit",       # [IO]
    "R37":   "PowerOcean Plus",      # [IO][SH] R371..R374

    # -- Climate ----------------------------------------------------------
    "BX1":   "Glacier",              # [HI][A][IO] BX11
    "RF45":  "Glacier 55",           # [IO]
    "KT2":   "Wave 2",               # [HI][A][IO] KT21
    "AC71":  "Wave 3",               # [IO][SH]
}

# Default model for unknown devices
UNKNOWN_MODEL = "Unknown EcoFlow Device"


def detect_model(sn: str) -> str:
    """Detect device model name from serial number prefix.

    Tries longest prefix match first so D361 matches before D36.
    Returns UNKNOWN_MODEL if no prefix matches.
    """
    sn_upper = sn.upper()

    # Sort prefixes longest-first for most specific match
    for prefix in sorted(_SN_PREFIX_MAP.keys(), key=len, reverse=True):
        if sn_upper.startswith(prefix):
            model = _SN_PREFIX_MAP[prefix]
            _LOGGER.info(
                "EcoFlow: detected %s for SN %s (prefix %s)",
                model, sn, prefix,
            )
            return model

    _LOGGER.warning(
        "EcoFlow: no device profile for SN prefix of %s — using diagnostic mode",
        sn,
    )
    return UNKNOWN_MODEL


def get_supported_models() -> list[str]:
    """Return list of unique supported model names (for UI display)."""
    return sorted(set(_SN_PREFIX_MAP.values()))
