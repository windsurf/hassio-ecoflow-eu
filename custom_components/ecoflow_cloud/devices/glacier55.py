"""Device definition for EcoFlow Glacier 55 (dual-zone portable refrigerator).

The Glacier 55 is the larger sibling of the Glacier (BX11) but uses a
fundamentally different protocol: protobuf cmdFunc=254 (Stream AC family),
not the Gen 2 moduleType JSON used by the original Glacier.

Glacier 55 features (dual-zone fridge/freezer with battery):
  - Two independent temperature zones (left/right) — float setpoints in °C
  - Cooling mode selection (ECO/MAX/SLEEP)
  - Child lock, simple mode, temperature alert, battery protection
  - Lid status sensor, water-in detection
  - 298Wh removable LFP battery + AC/DC/PV charging

PROTOCOL NOTES:
  - Telemetry: cmdFunc=254, cmdId=21 (DisplayPropertyUpload) — 43 proto fields
  - Keepalive: foxthefox 'latestQuotas' minimal setMessage (same as Stream AC)
  - SET commands: cmdFunc=254, cmdId=17 (ConfigWrite) — 11 settable fields
  - IMPORTANT: Glacier 55 ConfigWrite does NOT include cfgUtcTime — unlike
    Stream AC which always prepends cfgUtcTime. Uses dedicated builders.
  - setPointLeft/Right are FLOAT values (wire type 5, IEEE 754 32-bit).
    Other SET fields are varint (uint32/int32).

SN PREFIX: foxthefox does not document a confirmed SN prefix for Glacier 55.
Placeholder "BX55" used analogous to original Glacier (BX11). Update in
registry.py when an owner reports their actual SN via GitHub issue.

Source: foxthefox/ioBroker.ecoflow-mqtt (ef_glacier55_data.js)
"""
from __future__ import annotations

# ══════════════════════════════════════════════════════════════════════════════
# Protobuf field numbers → coordinator key names
# Source: foxthefox DisplayPropertyUpload proto definition (cmdFunc=254, cmdId=21)
# ══════════════════════════════════════════════════════════════════════════════

DISPLAY_FIELDS: dict[int, str] = {
    # ── System status ───────────────────────────────────────────────────────
    1:    "errcode",                    # System error code
    2:    "sysStatus",                  # System on/off status
    3:    "powInSumW",                  # Total input power (W) — float
    4:    "powOutSumW",                 # Total output power (W) — float
    5:    "lcdLight",                   # Screen brightness (0-100)
    7:    "energyBackupEn",             # Energy backup enabled (0/1)

    # ── Standby / display ───────────────────────────────────────────────────
    17:   "devStandbyTime",             # Device timeout (min)
    18:   "screenOffTime",              # Screen timeout (min)

    # ── BMS / battery ───────────────────────────────────────────────────────
    102:  "batTemp102",                 # Battery temperature reading
    140:  "bmsErrCode",                 # BMS error code
    195:  "enBeep",                     # Beep enabled (0/1)
    213:  "pdErrCode",                  # PD module error code

    # ── CMS overall (system-wide) ───────────────────────────────────────────
    262:  "cmsBattSoc",                 # Overall SOC (%) — float
    268:  "cmsDsgRemTime",              # Discharge time remaining (min)
    269:  "cmsChgRemTime",              # Charge time remaining (min)
    270:  "cmsMaxChgSoc",               # Max charge SOC limit (%)
    271:  "cmsMinDsgSoc",               # Min discharge SOC limit (%)
    282:  "cmsChgDsgState",             # Overall charge/discharge state
    288:  "cmsBattDesignCap",           # Battery design capacity (mAh)

    # ── Inputs ──────────────────────────────────────────────────────────────
    362:  "plugInInfoPvFlag",           # PV connected (0/1)
    363:  "plugInInfoPvType",           # PV source type
    392:  "bmsMainSn",                  # BMS main serial number
    426:  "plugInInfoDcpInFlag",        # DC plug-in connected (0/1)

    # ── Battery power limits ────────────────────────────────────────────────
    459:  "cmsBattPowOutMax",           # Max battery discharge power (W)
    460:  "cmsBattPowInMax",            # Max battery charge power (W)
    512:  "tempUnit",                   # Display temp unit (Celsius/Fahrenheit)

    # ── Cooling system (the unique Glacier 55 features) ─────────────────────
    736:  "setPointLeft",               # Left zone setpoint (°C) — float
    737:  "setPointRight",              # Right zone setpoint (°C) — float
    738:  "childLock",                  # Child lock enabled (0/1)
    739:  "simpleMode",                 # Simple mode enabled (0/1)
    740:  "batProtect",                 # Battery protection level (0=low, 1=med, 2=high)
    741:  "coolingMode",                # Cooling mode (0=eco, 1=max, 2=sleep)
    742:  "tempMonitorLeft",            # Left zone current temperature (°C) — float
    743:  "tempMonitorRight",           # Right zone current temperature (°C) — float
    744:  "lidStatus",                  # Lid open/closed (0/1)
    745:  "zoneStatus",                 # Zone status (single/dual)
    748:  "tempAlert",                  # Temperature alert enabled (0/1)
    749:  "uptime749",                  # System uptime counter
    777:  "inputVolt777",               # Input voltage (V) — float

    # ── Diagnostic fields with unknown semantics (foxthefox-tagged) ─────────
    623:  "unknown623",                 # Diagnostic — meaning unknown
    631:  "unknown631",                 # Diagnostic — meaning unknown
    746:  "unknown746",                 # Diagnostic float — meaning unknown
    747:  "unknown747",                 # Diagnostic float — meaning unknown
}

# ── Proto field numbers that are FLOAT (wire type 5 = 32-bit IEEE 754) ──────
FLOAT_FIELDS: set[int] = {
    3, 4,                       # powInSumW, powOutSumW
    262,                        # cmsBattSoc
    736, 737,                   # setPointLeft, setPointRight
    742, 743,                   # tempMonitorLeft, tempMonitorRight
    746, 747,                   # unknown floats
    777,                        # inputVolt777
}

# ══════════════════════════════════════════════════════════════════════════════
# ConfigWrite SET command field numbers (cmdFunc=254, cmdId=17)
# Source: foxthefox ConfigWrite proto definition
#
# IMPORTANT: Glacier 55 ConfigWrite does NOT include cfgUtcTime — unlike
# Stream AC which always prepends cfgUtcTime as field 6. This means we
# need a dedicated pdata builder that does NOT add a timestamp prefix.
# ══════════════════════════════════════════════════════════════════════════════

CMD_EN_BEEP_FIELD          = 9      # enBeep (uint32, 0/1)
CMD_DEV_STANDBY_FIELD      = 13     # devStandbyTime (int32, minutes)
CMD_MAX_CHG_SOC_FIELD      = 33     # cmsMaxChgSoc (int32, %)
CMD_MIN_DSG_SOC_FIELD      = 34     # cmsMinDsgSoc (int32, %)
CMD_SET_POINT_LEFT_FIELD   = 226    # setPointLeft (FLOAT, °C)
CMD_SET_POINT_RIGHT_FIELD  = 227    # setPointRight (FLOAT, °C)
CMD_CHILD_LOCK_FIELD       = 228    # childLock (uint32, 0/1)
CMD_SIMPLE_MODE_FIELD      = 229    # simpleMode (uint32, 0/1)
CMD_BAT_PROTECT_FIELD      = 230    # batProtect (uint32, 0=low/1=med/2=high)
CMD_COOLING_MODE_FIELD     = 231    # coolingMode (uint32, 0=eco/1=max/2=sleep)
CMD_TEMP_ALERT_FIELD       = 234    # tempAlert (uint32, 0/1)

DEVICE_MODEL = "Glacier 55"
