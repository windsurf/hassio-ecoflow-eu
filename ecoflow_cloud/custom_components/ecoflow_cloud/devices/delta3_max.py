"""Device definition for EcoFlow Delta 3 Max (SN prefix D381).

The Delta 3 Max extends Delta 3 Plus with additional internal-state
diagnostics (DCDC converter, LLC resonant converter, 12V aux output,
and PV voltage reference monitoring).

Source mapping strategy: identical to Delta 3 Plus — Max uses the
same command set as Delta 3 1500 and Plus. Only the additional
diagnostic telemetry keys differ.

Extra fields vs Delta 3 Plus (from foxthefox ef_delta3maxplus_data.js):
  - dcdcChgReqCur, llcBatCur, llcBatVol, llcBusVol
  - llcFsmstate, llcMonitorFlag, llcRecvCmsChgReqVol
  - invMainFsmstate, invMonitorFlag
  - plugInInfoDcp2Amp, plugInInfoDcp2Vol, plugInInfoPfcOutVol
  - plugInInfo_12vAmp, plugInInfo_12vVol
  - pv2VinRef, pvVinRef

All diagnostic fields are disabled by default in sensor.py — they
are useful for troubleshooting but generate noise in normal dashboards.

Source: foxthefox/ioBroker.ecoflow-mqtt (ef_delta3maxplus_data.js)
"""
from __future__ import annotations

# Re-export all Delta 3 Plus keys (which already re-exports Delta 3 1500).
# Max adds internal converter diagnostics on top.
from .delta3_plus import *  # noqa: F401, F403

# ══════════════════════════════════════════════════════════════════════════════
# Delta 3 Max — additional diagnostic sensor keys (DCDC / LLC / PFC)
# ══════════════════════════════════════════════════════════════════════════════

# ── DCDC converter diagnostics ──────────────────────────────────────────────
KEY_DCDC_CHG_REQ_CUR   = "inv.dcdcChgReqCur"           # DCDC charge request   (A)
KEY_DCP2_AMP           = "inv.plugInInfoDcp2Amp"       # DCP2 current          (A)
KEY_DCP2_VOL           = "inv.plugInInfoDcp2Vol"       # DCP2 voltage          (V)
KEY_PFC_OUT_VOL        = "inv.plugInInfoPfcOutVol"     # PFC output voltage    (V)

# ── LLC resonant converter diagnostics ──────────────────────────────────────
KEY_LLC_BAT_CUR        = "inv.llcBatCur"               # LLC battery current   (A)
KEY_LLC_BAT_VOL        = "inv.llcBatVol"               # LLC battery voltage   (V)
KEY_LLC_BUS_VOL        = "inv.llcBusVol"               # LLC bus voltage       (V)
KEY_LLC_FSM_STATE      = "inv.llcFsmstate"             # LLC state machine
KEY_LLC_MONITOR        = "inv.llcMonitorFlag"          # LLC monitor flag
KEY_LLC_CHG_REQ_VOL    = "inv.llcRecvCmsChgReqVol"     # LLC charge req volt   (V)

# ── Inverter state diagnostics ──────────────────────────────────────────────
KEY_INV_MAIN_FSM       = "inv.invMainFsmstate"         # Inverter main FSM
KEY_INV_MONITOR        = "inv.invMonitorFlag"          # Inverter monitor flag

# ── 12V auxiliary output ────────────────────────────────────────────────────
KEY_12V_AMP            = "inv.plugInInfo_12vAmp"       # 12V aux current       (A)
KEY_12V_VOL            = "inv.plugInInfo_12vVol"       # 12V aux voltage       (V)

# ── PV voltage references ───────────────────────────────────────────────────
KEY_PV_VIN_REF         = "mppt.pvVinRef"               # PV1 input volt ref    (V)
KEY_PV2_VIN_REF        = "mppt.pv2VinRef"              # PV2 input volt ref    (V)

DEVICE_MODEL = "Delta 3 Max"
