"""Device definition for EcoFlow Delta Pro 3.

SN prefix: DGEA (confirmed via EcoFlow developer docs, SN example: MR51ZAS2PG330026)

Protocol: Delta Pro 3 uses a DIFFERENT command format than Delta 2/3:
  - Command envelope: {sn, cmdId:17, cmdFunc:254, dest:2, dirDest:1, dirSrc:1, needAck:true, params:{...}}
  - Quota keys are FLAT (no pd./mppt./inv. prefix): enBeep, acStandbyTime, cmsMaxChgSoc, etc.
  - REST SET: PUT /iot-open/sign/device/quota with DP3 envelope
  - REST GET: POST /iot-open/sign/device/quota with {sn, params:{quotas:[...]}}

Source: EcoFlow Developer Platform docs (developer-eu.ecoflow.com/us/document/deltaPro3)
         PDF export 1 April 2026, 24 pages
"""
from __future__ import annotations

# ══════════════════════════════════════════════════════════════════════════════
# Quota keys — flat namespace (no module prefix)
# These are the keys returned by REST GET and MQTT telemetry push.
# Source: GetCmdResponse column in official developer docs
# ══════════════════════════════════════════════════════════════════════════════

# ── Switches (bool / int 0-1) ─────────────────────────────────────────────
KEY_BEEP             = "enBeep"                     # Beep sound on/off
KEY_XBOOST           = "xboostEn"                   # X-Boost on/off
KEY_AC_HV_OUT        = "flowInfoAcHvOut"             # AC HV (240V) output on/off
KEY_AC_LV_OUT        = "flowInfoAcLvOut"             # AC LV (120V) output on/off
KEY_DC_12V_OUT       = "flowInfo12v"                 # DC 12V output on/off
KEY_ENERGY_BACKUP_EN = "energyBackupEn"              # Energy backup mode on/off
KEY_OIL_SELF_START   = "cmsOilSelfStart"             # Generator auto-start on/off
KEY_GFCI_FLAG        = "llcGFCIFlag"                 # GFCI protection on/off
KEY_AC_ENERGY_SAVING = "acEnergySavingOpen"           # AC energy saving mode on/off

# ── Numbers (int / float) ─────────────────────────────────────────────────
KEY_AC_STANDBY_TIME  = "acStandbyTime"               # AC standby timeout (min)
KEY_DC_STANDBY_TIME  = "dcStandbyTime"               # DC standby timeout (min)
KEY_SCREEN_OFF_TIME  = "screenOffTime"                # Screen off timeout (sec)
KEY_DEV_STANDBY_TIME = "devStandbyTime"               # Device standby timeout (min)
KEY_LCD_LIGHT        = "lcdLight"                     # LCD brightness (0-100)
KEY_AC_OUT_FREQ      = "acOutFreq"                    # AC output frequency (50/60 Hz)
KEY_MAX_CHG_SOC      = "cmsMaxChgSoc"                 # Max charge SOC (%)
KEY_MIN_DSG_SOC      = "cmsMinDsgSoc"                 # Min discharge SOC (%)
KEY_ENERGY_BACKUP_SOC = "energyBackupStartSoc"        # Energy backup start SOC (%)
KEY_PV_LV_DC_AMP_MAX = "plugInInfoPvLDcAmpMax"       # LV solar max charge current (A)
KEY_PV_HV_DC_AMP_MAX = "plugInInfoPvHDcAmpMax"       # HV solar max charge current (A)
KEY_AC_CHG_POW_MAX   = "plugInInfoAcInChgPowMax"     # AC max charging power (W)
KEY_5P8_CHG_POW_MAX  = "plugInInfo5p8ChgPowMax"      # 5.8mm DC max charging power (W)
KEY_OIL_ON_SOC       = "cmsOilOnSoc"                  # Generator start SOC (%)
KEY_OIL_OFF_SOC      = "cmsOilOffSoc"                 # Generator stop SOC (%)
KEY_BLE_STANDBY_TIME = "bleStandbyTime"               # Bluetooth standby timeout (min)
KEY_MULTI_BP_MODE    = "multiBpChgDsgMode"            # Multi-battery charge/discharge mode

# ── Command parameter names (cfgParam → params key in SET command) ────────
# These are the keys used in the SET command params dict
CMD_BEEP             = "cfgBeepEn"
CMD_AC_STANDBY       = "cfgAcStandbyTime"
CMD_DC_STANDBY       = "cfgDcStandbyTime"
CMD_SCREEN_OFF       = "cfgScreenOffTime"
CMD_DEV_STANDBY      = "cfgDevStandbyTime"
CMD_LCD_LIGHT        = "cfgLcdLight"
CMD_AC_HV_OUT        = "cfgHvAcOutOpen"
CMD_AC_LV_OUT        = "cfgLvAcOutOpen"
CMD_AC_OUT_FREQ      = "cfgAcOutFreq"
CMD_DC_12V_OUT       = "cfgDc12vOutOpen"
CMD_XBOOST           = "cfgXboostEn"
CMD_POWER_OFF        = "cfgPowerOff"
CMD_MAX_CHG_SOC      = "cfgMaxChgSoc"
CMD_MIN_DSG_SOC      = "cfgMinDsgSoc"
CMD_ENERGY_BACKUP    = "cfgEnergyBackup"              # nested: {energyBackupStartSoc, energyBackupEn}
CMD_PV_LV_AMP        = "cfgPlugInInfoPvLDcAmpMax"
CMD_PV_HV_AMP        = "cfgPlugInInfoPvHDcAmpMax"
CMD_AC_CHG_POW       = "cfgPlugInInfoAcInChgPowMax"
CMD_5P8_CHG_POW      = "cfgPlugInInfo5p8ChgPowMax"
CMD_OIL_SELF_START   = "cfgCmsOilSelfStart"
CMD_OIL_ON_SOC       = "cfgCmsOilOnSoc"
CMD_OIL_OFF_SOC      = "cfgCmsOilOffSoc"
CMD_GFCI_FLAG        = "cfgLlcGFCIFlag"
CMD_BLE_STANDBY      = "cfgBleStandbyTime"
CMD_AC_ENERGY_SAVING = "cfgAcEnergySavingOpen"
CMD_MULTI_BP_MODE    = "cfgMultiBpChgDsgMode"

# ── DP3 Command envelope constants ────────────────────────────────────────
DP3_CMD_ID     = 17
DP3_CMD_FUNC   = 254
DP3_DEST       = 2
DP3_DIR_DEST   = 1
DP3_DIR_SRC    = 1

DEVICE_MODEL = "Delta Pro 3"
