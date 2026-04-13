"""Device definition for EcoFlow Delta Max.

MQTT key sources:
  - tolwi/hassio-ecoflow-cloud (internal/delta_max.py — confirmed)
  - snell-evan-itt/hassio-ecoflow-cloud-US (internal/delta_max.py — confirmed)

Gen 1 protocol — same key schema as Delta Pro (bmsMaster/ems/bmsSlave).
Key differences vs Delta Pro:
  - No DC Anderson port (mppt.dcdc12vWatts)
  - AC charging max 2000W (vs 2900W on Pro)
  - SET commands use same TCP protocol with id numbers
"""
from __future__ import annotations

# Delta Max shares Gen 1 key schema with Delta Pro
from .delta_pro import (
    # Battery
    KEY_SOC, KEY_SOC_FLOAT, KEY_SOH, KEY_CYCLES,
    KEY_BATT_TEMP, KEY_MIN_CELL_TEMP, KEY_MAX_CELL_TEMP,
    KEY_BATT_VOLT, KEY_BATT_CURR, KEY_MIN_CELL_VOLT, KEY_MAX_CELL_VOLT,
    KEY_REMAIN_CAP, KEY_FULL_CAP, KEY_DESIGN_CAP,
    # EMS
    KEY_EMS_SOC_LCD, KEY_EMS_SOC_FLOAT,
    KEY_CHARGE_TIME, KEY_DSG_TIME,
    KEY_EMS_MAX_CHG_SOC, KEY_EMS_MIN_DSG_SOC,
    KEY_GEN_START, KEY_GEN_STOP,
    # AC
    KEY_AC_IN_W, KEY_AC_OUT_W, KEY_AC_IN_VOLT, KEY_AC_OUT_VOLT, KEY_AC_TEMP,
    KEY_AC_ENABLED, KEY_AC_XBOOST, KEY_AC_STANDBY,
    # Solar
    KEY_SOLAR_W, KEY_SOLAR_VOLT, KEY_SOLAR_AMP,
    KEY_SOLAR_OUT_W, KEY_SOLAR_OUT_VOLT,
    KEY_DC_OUT_STATE,
    # PD
    KEY_IN_W_TOTAL, KEY_OUT_W_TOTAL,
    KEY_USBC1_W, KEY_USBC2_W, KEY_USB1_W, KEY_USB2_W,
    KEY_USB_QC1_W, KEY_USB_QC2_W,
    KEY_LCD_TIMEOUT, KEY_BEEP, KEY_AC_AUTO_OUT,
    # Energy
    KEY_CHG_SUN_POWER, KEY_CHG_POWER_AC, KEY_CHG_POWER_DC,
    KEY_DSG_POWER_AC, KEY_DSG_POWER_DC,
    # Slaves
    KEY_SLV1_SOC, KEY_SLV1_SOC_FLOAT, KEY_SLV1_SOH, KEY_SLV1_TEMP,
    KEY_SLV1_MIN_CT, KEY_SLV1_MAX_CT, KEY_SLV1_VOLT, KEY_SLV1_CURR,
    KEY_SLV1_MIN_CV, KEY_SLV1_MAX_CV,
    KEY_SLV1_REMAIN_CAP, KEY_SLV1_FULL_CAP, KEY_SLV1_DESIGN_CAP,
    KEY_SLV1_CYCLES, KEY_SLV1_INPUT_W, KEY_SLV1_OUTPUT_W,
    KEY_SLV2_SOC, KEY_SLV2_SOC_FLOAT, KEY_SLV2_SOH, KEY_SLV2_TEMP,
    KEY_SLV2_MIN_CT, KEY_SLV2_MAX_CT, KEY_SLV2_VOLT, KEY_SLV2_CURR,
    KEY_SLV2_MIN_CV, KEY_SLV2_MAX_CV,
    KEY_SLV2_REMAIN_CAP, KEY_SLV2_FULL_CAP, KEY_SLV2_DESIGN_CAP,
    KEY_SLV2_CYCLES, KEY_SLV2_INPUT_W, KEY_SLV2_OUTPUT_W,
    # Options
    DC_CHG_CURRENT_OPTIONS,
)

# Delta Max also has DC car out (same key as Pro)
KEY_DC_CAR_OUT_W = "mppt.carOutWatts"

# Delta Max specific: AC charging via inv.cfgSlowChgWatts
KEY_AC_CHG_W = "inv.cfgSlowChgWatts"

# ── Constants ────────────────────────────────────────────────────────────────
AC_CHG_WATTS_MIN    = 100
AC_CHG_WATTS_MAX    = 2000   # Delta Max = 2000W (vs 2900W on Pro)
AC_CHG_WATTS_STEP   = 100

DEVICE_MODEL = "Delta Max"
