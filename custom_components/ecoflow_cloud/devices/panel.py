"""Device definition for EcoFlow Smart Home Panel 1 (SHP1) — 10-circuit smart panel.

The Smart Home Panel 1 is EcoFlow's circuit-level home backup panel. It connects
between the grid and the breaker panel, monitoring 10 mains circuits + 2 backup
circuits and routing power based on grid availability and configured priorities.

PROTOCOL: JSON over MQTT, similar to Gen 2 moduleType protocol but with
operateType='TCP' for SET commands. Telemetry pushed as JSON heartbeat
messages on the standard subscribe topic.

Features (circuit-level smart panel):
  - 10 mains circuits (channels 0-9) — independently controllable on/off + priority
  - 2 backup circuits (channels 10-11) — backup-only loads
  - Grid info, split-phase info, area allocation
  - Per-circuit power (chWatt), current (cur), daily watt-hours
  - Backup mode strategies and emergency configuration

KEY NAMING: foxthefox uses flat camelCase keys with channel numbers as suffix
  (chWatt_0, ctrlMode_5, etc.). We adopt the same convention.

SN PREFIX: SH10 (already registered in v0.3.9 — was a stub).

Source: foxthefox/ioBroker.ecoflow-mqtt (ef_panel_data.js)
"""
from __future__ import annotations

# Channel range constants
NUM_MAINS_CHANNELS = 10   # circuits 0..9
NUM_BACKUP_CHANNELS = 2   # circuits 10..11
TOTAL_CHANNELS = NUM_MAINS_CHANNELS + NUM_BACKUP_CHANNELS  # 12

# ── Heartbeat / system status ───────────────────────────────────────────────
KEY_BACKUP_CHA_TIME       = "heartbeat.backupChaTime"     # Backup charge time (min)
KEY_GRID_STA              = "heartbeat.gridSta"           # Grid status (0=off/1=on)
KEY_WORK_TIME             = "heartbeat.workTime"          # System work time (min)
KEY_BACKUP_BAT_PER        = "heartbeat.backupBatPer"      # Backup battery percentage (%)
KEY_BACKUP_FULL_CAP       = "heartbeat.backupFullCap"     # Backup full capacity (Wh)
KEY_BACKUP_DAY_WATTH      = "heartbeat.backupDayWatth"    # Daily backup energy (Wh)
KEY_GRID_DAY_WATTH        = "heartbeat.gridDayWatth"      # Daily grid energy (Wh)

# ── Channel power (per circuit, channels 0-9 mains + 10-11 backup) ──────────
# Templates — actual key names use channel index suffix, e.g. "channelPower.chWatt_0"
KEY_CHANNEL_POWER_FMT     = "channelPower.chWatt_{ch}"        # Per-circuit power (W)
KEY_CHANNEL_POW_TYPE_FMT  = "channelPower.powType_{ch}"       # Per-circuit power type
KEY_CHANNEL_CURR_FMT      = "loadChCurInfo.cur_{ch}"          # Per-circuit current (A)
KEY_CHANNEL_NAME_FMT      = "loadChInfo.chName_{ch}"          # Per-circuit name
KEY_CHANNEL_ICON_FMT      = "loadChInfo.iconNum_{ch}"         # Per-circuit icon ID
KEY_CHANNEL_DAY_WATTH_FMT = "{table}.watthDaytoDate_{ch}"     # Per-circuit daily Wh

# ── Channel control state (settable via switch) ─────────────────────────────
# ctrlMode = 0 (manual)/1 (auto), ctrlSta = 0 (off)/1 (on)/2 (forced on)
KEY_CTRL_MODE_FMT_MAINS   = "loadCmdChCtrlInfos.ctrlMode_{ch}"     # Mains channel mode (0/1)
KEY_CTRL_STA_FMT_MAINS    = "loadCmdChCtrlInfos.ctrlSta_{ch}"      # Mains channel state
KEY_PRIORITY_FMT_MAINS    = "loadCmdChCtrlInfos.priority_{ch}"     # Mains channel priority
KEY_POW_CH_FMT_MAINS      = "loadCmdChCtrlInfos.powCh_{ch}"        # Mains channel allowed power

KEY_CTRL_MODE_FMT_BACKUP  = "backupCmdChCtrlInfos.ctrlMode_{ch}"   # Backup channel mode (0/1)
KEY_CTRL_STA_FMT_BACKUP   = "backupCmdChCtrlInfos.ctrlSta_{ch}"    # Backup channel state
KEY_PRIORITY_FMT_BACKUP   = "backupCmdChCtrlInfos.priority_{ch}"   # Backup channel priority
KEY_POW_CH_FMT_BACKUP     = "backupCmdChCtrlInfos.powCh_{ch}"      # Backup channel allowed power

# ── EPS (Emergency Power System) mode ───────────────────────────────────────
KEY_EPS_MODE              = "epsModeInfo.eps"             # EPS enabled (0/1)

# ── Channel enable status ───────────────────────────────────────────────────
KEY_CH_ENABLE_FMT         = "chUseInfo.isEnable_{ch}"     # Channel enabled (0/1)

# ── Backup charge/discharge configuration ───────────────────────────────────
KEY_DISC_LOWER            = "backupChaDiscCfg.discLower"        # Lower discharge threshold (%)
KEY_FORCE_CHARGE_HIGH     = "backupChaDiscCfg.forceChargeHigh"  # Force-charge upper threshold (%)

# ──────────────────────────────────────────────────────────────────────────────
# JSON SET command builders
# ──────────────────────────────────────────────────────────────────────────────
#
# All SHP1 SET commands use the same envelope:
#   {
#     "moduleType": 0,
#     "operateType": "TCP",
#     "params": { ...command-specific... }
#   }
#
# Source: foxthefox ef_panel_data.js deviceCmd templates


def shp1_build_channel_ctrl(channel: int, on: bool, *, backup: bool = False) -> dict:
    """Build a JSON SET command to switch a circuit on/off.

    For mains channels (0-9), use backup=False.
    For backup channels (10-11), use backup=True.

    sta=2 + ctrlMode=1 = ON
    sta=0 + ctrlMode=0 = OFF (auto release)
    """
    return {
        "moduleType": 0,
        "operateType": "TCP",
        "params": {
            "sta": 2 if on else 0,
            "ctrlMode": 1 if on else 0,
            "ch": int(channel),
            "cmdSet": 11,
            "id": 16,
        },
    }


def shp1_build_eps_mode(enabled: bool) -> dict:
    """Toggle EPS (Emergency Power System) mode."""
    return {
        "moduleType": 0,
        "operateType": "TCP",
        "params": {
            "cmdSet": 11,
            "id": 24,
            "eps": 1 if enabled else 0,
        },
    }


def shp1_build_channel_enable(channel: int, enabled: bool) -> dict:
    """Enable/disable a circuit (chUseInfo)."""
    return {
        "moduleType": 0,
        "operateType": "TCP",
        "params": {
            "cmdSet": 11,
            "id": 26,
            "chNum": int(channel),
            "isEnable": 1 if enabled else 0,
        },
    }


def shp1_build_backup_thresholds(disc_lower: int, force_charge_high: int) -> dict:
    """Set backup discharge lower threshold and force-charge high threshold (%)."""
    return {
        "moduleType": 0,
        "operateType": "TCP",
        "params": {
            "discLower": int(disc_lower),
            "forceChargeHigh": int(force_charge_high),
            "cmdSet": 11,
            "id": 29,
        },
    }


DEVICE_MODEL = "Smart Home Panel"
