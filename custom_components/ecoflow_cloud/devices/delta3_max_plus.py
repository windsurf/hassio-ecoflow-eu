"""Device definition for EcoFlow Delta 3 Max Plus (SN prefix D3M1).

The Delta 3 Max Plus does NOT use the dotted quota keys of the Delta 3 1500
(pd.soc, inv.outputWatts, ...). It uses the flat key set and the command
envelope of the newer device generation (same family as Delta Pro 3):

  - Telemetry keys are flat: cmsBattSoc, powInSumW, powOutSumW, ...
  - Commands: {sn, cmdId:17, cmdFunc:254, dest:2, dirDest:1, dirSrc:1,
               needAck:true, params:{cfgXxx: value}}
  - Developer API (recommended route):
      MQTT telemetry   /open/<account>/<sn>/quota   (JSON, partial updates)
      MQTT set         /open/<account>/<sn>/set
      MQTT set reply   /open/<account>/<sn>/set_reply
      REST             PUT/POST /iot-open/sign/device/quota
  - App Login route: the device pushes protobuf (cmdFunc 254 / cmdId 21 and
    cmdFunc 32); the decoder yields the same flat key names plus battery data.

Source: EcoFlow Developer Platform, "DELTA 3 MAX PLUS" (HTTP and MQTT mode),
        and live diagnostics dumps from a real device (v0.4.0).
"""
from __future__ import annotations

DEVICE_MODEL = "Delta 3 Max Plus"

# ── Telemetry keys (flat) ───────────────────────────────────────────────────
KEY_SOC             = "cmsBattSoc"            # Battery level (%)
KEY_BMS_SOC         = "bmsBattSoc"            # BMS battery level (%) — App Login route only
KEY_IN_W            = "powInSumW"             # Total input power (W)
KEY_OUT_W           = "powOutSumW"            # Total output power (W)
KEY_AC_IN_W         = "powGetAcIn"            # AC input power (W)
KEY_PV_W            = "powGetPv"              # PV / car input power (W)
KEY_PV2_W           = "powGetPv2"             # PV / car input 2 power (W)
KEY_DC12V_W         = "powGet12v"             # 12 V output power (W)
KEY_DCP_W           = "powGetDcp"             # DCP input power (W) — App Login route only
KEY_USBA1_W         = "powGetQcusb1"          # USB-A 1 output power (W)
KEY_USBA2_W         = "powGetQcusb2"          # USB-A 2 output power (W)
KEY_USBC1_W         = "powGetTypec1"          # USB-C 1 output power (W)
KEY_USBC2_W         = "powGetTypec2"          # USB-C 2 output power (W)
KEY_USBC3_W         = "powGetTypec3"          # USB-C 3 output power (W)
KEY_CHG_DSG_STATE   = "cmsChgDsgState"        # 0 idle, 1 discharging, 2 charging
KEY_CHG_REM_MIN     = "cmsChgRemTime"         # Minutes to full
KEY_DSG_REM_MIN     = "cmsDsgRemTime"         # Minutes of use remaining
KEY_MAX_CELL_TEMP   = "bmsMaxCellTemp"        # °C — App Login route only
KEY_MIN_CELL_TEMP   = "bmsMinCellTemp"        # °C — App Login route only
KEY_AC_CHG_POW_MAX  = "plugInInfoAcInChgPowMax"  # AC max charging power (W) — App Login route only

# ── State keys of controllable functions ────────────────────────────────────
KEY_AC_OUT          = "flowInfoAcOut"         # AC output   (4 = off, otherwise on)
KEY_AC2_OUT         = "flowInfoAc2Out"        # AC2 output  (4 = off, otherwise on)
KEY_DC12V_OUT       = "flowInfo12v"           # 12 V output (4 = off, otherwise on)
KEY_ENERGY_BACKUP   = "energyBackupEn"        # Energy backup mode
KEY_BEEP            = "enBeep"                # Buzzer
KEY_XBOOST          = "xboostEn"              # X-Boost
KEY_BYPASS_DISABLE  = "bypassOutDisable"      # Bypass output disabled
KEY_MAX_CHG_SOC     = "cmsMaxChgSoc"          # Charge upper limit (%)   50-100
KEY_MIN_DSG_SOC     = "cmsMinDsgSoc"          # Discharge lower limit (%) 0-30
KEY_BACKUP_SOC      = "backupReverseSoc"      # Energy backup reserve (%) 0-50

# ── Command parameter names ─────────────────────────────────────────────────
CMD_AC_OUT          = "cfgAcOutOpen"
CMD_AC2_OUT         = "cfgAc2OutOpen"
CMD_DC12V_OUT       = "cfgDc12vOutOpen"
CMD_ENERGY_BACKUP   = "cfgEnergyBackup"       # nested: {"energyBackupEn": bool}
CMD_BEEP            = "cfgBeepEn"
CMD_XBOOST          = "cfgXboostEn"
CMD_BYPASS_DISABLE  = "cfgBypassOutDisable"
CMD_MAX_CHG_SOC     = "cfgMaxChgSoc"
CMD_MIN_DSG_SOC     = "cfgMinDsgSoc"
CMD_BACKUP_SOC      = "cfgBackupReverseSoc"

# ── Value conventions ───────────────────────────────────────────────────────
FLOW_OFF = 4          # flowInfo* value when the output is off
FLOW_ON  = 14         # flowInfo* value observed when the output is on
REMAIN_TIME_NONE = 12927   # cmsChgRemTime / cmsDsgRemTime when the time does not apply
CHG_DSG_STATES = ((0, "idle"), (1, "discharging"), (2, "charging"))
