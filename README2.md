# EcoFlow Cloud – Technical reference

The simple introduction is in the [README](README.md). This page holds the details: credentials, how control works, every entity per device, the Delta 3 Max Plus profile, debug logging and the changelog.

---

## Delta 3 Max Plus (serial prefix D3M1)

The Max Plus does **not** use the dotted keys of the Delta 3 1500 (`pd.soc`, `inv.outputWatts`, …). It uses the flat key set and the command envelope of the newer generation (the same family as Delta Pro 3).

| Route | Telemetry | Control | Tested |
|---|---|---|---|
| **Developer API** (Auto-detect picks it for `D3M1`) | MQTT JSON `/open/<account>/<sn>/quota` (partial updates, about every 2 s under load) plus REST every 30 s; 27 flat keys | MQTT `/open/<account>/<sn>/set`, reply on `/set_reply` | ✅ reading and control |
| App Login | MQTT protobuf `/app/...`; the same flat keys plus BMS level, cell temperatures, DCP power and AC max charge power (42 keys); no AC output status | not tested | reading only |

**Command envelope** (as for Delta Pro 3): `{sn, id, version, cmdId: 17, cmdFunc: 254, dest: 2, dirDest: 1, dirSrc: 1, needAck: true, params: {cfgXxx: value}}`.

**Entities** (default enabled unless marked off):

| Platform | Entities |
|---|---|
| Sensors | Battery Level, Total Input Power, Total Output Power, AC Input Power, Solar Input Power, Solar 2 Input Power, DC 12V Output Power, Charge State (idle / discharging / charging), Time To Full, Remaining Run Time; off: USB-A 1/2, USB-C 1/2/3 output power; App Login only, off: BMS Battery Level, DCP Input Power, Max/Min Cell Temperature, AC Max Charging Power |
| Switches | AC Output, Energy Backup; off: AC Output 2, DC 12V Output, Beep Sound, X-Boost, Bypass Output Disabled |
| Numbers | Charge Limit (50–100 %), Discharge Limit (0–30 %), Energy Backup Reserve (0–50 %) |

**Value conventions** (EcoFlow Developer Platform, confirmed on a device): `flowInfoAcOut`, `flowInfoAc2Out` and `flowInfo12v` read **4 = off, otherwise on** (14 observed when on). `cmsChgRemTime` and `cmsDsgRemTime` are minutes; 12927 means "no value" and the sensor shows unknown.

**Dashboard.** At first setup the integration creates the dashboard `ecoflow-max-plus` (Overview and History) through the entity registry, so renamed devices and entity ids with a `_2` suffix are handled. Entities that are disabled or missing leave their card out. The flag `dashboard_done` in the entry keeps a deleted dashboard from coming back; **Configure → Replace the dashboard with a fresh one** builds it again. If Home Assistant refuses the automatic route, a notification explains the manual route with [`dashboard/ecoflow_max_plus.yaml`](dashboard/ecoflow_max_plus.yaml). The power gauges run to 3000 W (`GAUGE_MAX_IN_W`, `GAUGE_MAX_OUT_W` in `dashboard.py`).

**Diagnostics.** Settings → Devices & services → EcoFlow Cloud → device → Download diagnostics. The file holds the detected model, connection mode, MQTT topics and counters, the full coordinator state (mapped and unmapped keys) and the last 50 raw MQTT messages (JSON as text, binary as hex plus a protobuf field dump). Credentials are removed. Serial numbers are replaced by placeholders in text and JSON, and masked with `*` bytes of equal length in binary payloads, where the device and its battery pack serials appear as plain ASCII.

**Command replies.** The `set_reply` payloads of the Developer API route are logged at INFO level (`EcoFlow: set_reply payload=…`); set `custom_components.ecoflow_cloud: info` under `logger:` to see them.

---

## Getting Credentials

### Option A — App Login *(start here)*
Use your regular EcoFlow app email and password. No extra setup needed. For the Delta 3 Max Plus it reads everything plus a few BMS values; the AC output switch cannot show its real state and control over this route is not tested. If that is not enough, use Option B.

### Option B — Developer API *(when App Login is not enough)*
1. Go to [developer-eu.ecoflow.com](https://developer-eu.ecoflow.com/) and sign in
2. Click **Become a Developer** and wait for the approval email
3. Go to **Security** and create an Access Key + Secret Key

---

## Setup

**Step 1:** Enter your device serial number and choose a connection method.
Select **Auto-detect** (recommended) — Delta 3, newer PowerStream and other recent devices will use App Login automatically; older devices use the Developer API.

**Step 2:** Enter credentials for the chosen method.

**Step 3 (App Login only):** Optionally enter Developer API keys. For Delta 3 (D361) devices this has no effect on control — REST SET is blocked by EcoFlow for this series. Leave empty to skip.

**Step 4:** Automatic connection test — confirms login and shows which devices are on your account.

After setup, use the **gear icon** on the integration card to change credentials, add Developer API keys, or switch API mode.

### How Control Works (Delta 3)

Confirmed via live protocol analysis (v0.2.22–v0.2.24): Delta 3 uses **MQTT JSON SET** with `"from": "Android"` in the payload.

| Function | Channel | Notes |
|----------|---------|-------|
| Real-time sensor data | MQTT push | `/app/device/property/{sn}` — pushed every ~3s (pd) or ~3-5 min (mppt) |
| Switch/number control | MQTT JSON SET | `"from":"Android"` required |
| REST API SET | Blocked | EcoFlow blocks D361/D362/D381/R641/R651 (code=1006) |

**SET command payload:** `{id, version:"1.0", sn, moduleType, operateType, from:"Android", params:{...}}`

### D361-Specific Behaviour (confirmed via live tests)

| Feature | Behaviour |
|---------|-----------|
| AC Charging pause (`chgPauseFlag`) | Not supported — command received (beep) but has no effect. `mppt.chgPauseFlag` never in telemetry. |
| LCD Brightness | Not controllable via MQTT — `lcdCfg brighLevel` received (beep) but no visible effect |
| Screen Timeout (`lcdCfg delayOff`) | Works — do not send `brighLevel=255` alongside it; D361 writes 65535 literally |
| AC Standby (`standbyTime` mod5) | Works — operateType must be `standbyTime`, not `standby` |
| MPPT keys update frequency | Every 3–5 minutes (not real-time), periodic full upload |
| `mppt.chgPauseFlag` in telemetry | Never pushed — not a supported state key on D361 |
| `bms_emsStatus.sysChgDsgState` | Charge state indicator: 0=idle, 1=discharging, 2=charging |
| `pd.lcdOffSec = 65535` | Sentinel value for "Never" (not 0) |
| `pd.acAutoOutPause` | Always 0 on D361 -- never pushed via telemetry. Bypass state unavailable. SET command works (relay confirmed). |
| `mppt.cfgAcEnabled` | Updates 2s before `pd.acEnabled` and `inv.cfgAcEnabled` on AC Output toggle |

---

## Supported Entities

### Switches (13)

| Entity | Default | Notes |
|--------|---------|-------|
| AC Output | ✅ | Turn 230V output on/off |
| X-Boost | ✅ | Enable/disable X-Boost |
| USB Output | ✅ | USB-A + USB-C ports on/off |
| DC Output | ✅ | Car/Anderson port on/off |
| AC Charging | off | **Read-only** — D361 does not support chgPauseFlag via MQTT. State key `mppt.chgPauseFlag` never pushed. Disabled by default. |
| Solar Charge Priority | ✅ | Prioritise solar over AC |
| AC Auto-On | off | AC turns on automatically when mains connected |
| AC Always-On | off | Keep AC on regardless of SOC |
| UPS Mode | off | UPS mode — effect unconfirmed on D361, disabled by default |
| Backup Reserve | off | Enable/disable backup reserve mode |
| Output Memory | off | Remember output states after power loss — ACK only, no state feedback on D361 |
| Bypass | off | Enable/disable bypass mode — ACK only, no state feedback on D361 |
| Beep Sound | off | Enable/disable device beeps |

### Number Controls (9)

| Entity | Range | Default |
|--------|-------|---------|
| AC Charging Speed | 200–1500 W (step 100) | ✅ |
| Max Charge Level | 50–100% (step 5) | ✅ |
| Min Discharge Level | 0–30% (step 5) | ✅ |
| Generator Start SOC | 0–30% (step 5) | off |
| Generator Stop SOC | 50–100% (step 5) | off |
| Backup Reserve SOC | 5–100% (step 5) | off |
| Min SOC for AC Auto-On | 0–100% (step 5) | off |
| Screen Standby Time (read-only) | min | off |
| Overall Standby Time (read-only) | min | off |

> Note: Battery Protection SOC removed in v0.2.23 (duplicate of Min Discharge Level).

### Select Controls (5)

| Entity | Options | Default | operateType (confirmed) |
|--------|---------|---------|------------------------|
| DC Charge Current | 4 A / 6 A / 8 A | ✅ | `dcChgCfg` mod5 |
| Screen Timeout | Never / 10s / 30s / 1min / 5min / 30min | off | `lcdCfg` mod1 — `delayOff` only |
| Unit Standby Time | Never / 30min–24hr | off | `standbyTime` mod1 — `standbyMin` |
| AC Output Standby Time | Never / 30min–24hr | off | `standbyTime` mod5 — `standbyMins` |
| DC 12V Standby Time | Never / 30min–24hr | off | `carStandby` mod5 — `standbyMins` |

> Entities marked **off** are disabled by default. Enable them in Settings → Devices & Services → your device → the entity.

### Delta 3 1500 — Sensors (185)

**Battery (17):** Battery Level, Battery Level (precise), State of Health, Charge Cycles, Remaining Capacity, Full Capacity, Design Capacity, Battery Voltage, Battery Current, Battery Temperature, Min/Max Cell Temperature, Min/Max MOS Temperature, Min/Max Cell Voltage, Max Cell Voltage Difference

**EMS (9):** Time Remaining, Time to Full, Max Charge Level, Min Discharge Level, EMS Charge Voltage, EMS Charge Current, Fan Level, AC Plug Connected, System Charge/Discharge State

**AC / Inverter (15):** AC Output Power, AC Input Power, AC Input Voltage/Current/Frequency, AC Output Voltage/Current/Frequency, AC Configured Frequency, AC Fast/Slow Charge Watts, Inverter Temperature, Inverter DC Input Voltage/Current/Temperature

**Solar / MPPT (11):** Solar Input Power/Voltage/Current, MPPT Output Power, MPPT Temperature, DC 12V Output/Input Power, DC 12V Temperature, DC 12V Port State, DC Output Temperature, MPPT DC Converter Power

**USB / PD (10):** Total Input/Output Power, USB-A 1/2 Power, USB-A QC 1/2 Power, USB-C 1/2 Power, USB-C 1/2 Temperature

**Energy totals (3):** Cumulative AC Charged, Cumulative DC Charged, Solar Charge Power

**System (2):** Battery Protection SOC, WiFi Signal

**Extra battery kit (2):** Extra Battery Power, Extra Batteries Connected

**Slave battery (33):** Mirrors main battery sensors for attached slave battery — Level, Voltage, Current, Temperature, Capacity, SoH, Input/Output Power, Cell Voltages, MOS Temps, Lifetime stats, Error Code (20 disabled by default as diagnostics)

**Battery lifetime (10):** SoH (Info), Total Cycles, Cumulative Charged/Discharged Capacity, Cumulative Charged/Discharged Energy, Round-Trip Efficiency, Self-Discharge Rate, Deep Discharge Count, Internal Resistance

**BMS extended diagnostics (22):** Actual SOC, BMS SOC, Charge/System/MOS/Fault States, Error Codes, Cell Balancing, Charged/Discharged Capacity, Input/Output Power, Real/Calculated/Cycle SoH, SOC Difference, Target SOC, Target Charge Current, Remaining Time, BQ Status Register

**BmsInfo lifetime (5):** High/Low Temp Charge Time, High/Low Temp Total Time, Power Capability

**EMS extended (12):** Discharge Remaining Time, Charge State/Command, Discharge Command/Condition, Charge Condition, Warning State, Normal Flag, Display SOC (float/LCD), Parallel Voltage Max/Min

**INV extended (5):** AC Work Mode, Charger Type, Discharge Type, Error Code, AC DIP Switch

**MPPT extended (10):** Charge State/Type, Configured Charge Type, Discharge Type, Fault Code, Output Current/Voltage, DC 24V Port State, Screen/Overall Standby Time

**PD extended (17):** DC 12V Temperature, DC 12V/DC Input Use Time, Charger Type, Error Code, RJ45/3.8V/4.8V Port Status, Hysteresis SOC, Inverter/MPPT/USB-C/USB-A/USB QC Use Time, Relay Switch Count, WiFi Auto Recovery, MPPT Beep

**Generator thresholds (2):** Generator Start SOC, Generator Stop SOC

> Most extended/diagnostic sensors are disabled by default. Enable in Settings → Devices & Services → your device → the entity.

### Delta 2 — Sensors (46)

**Battery (14):** Battery Level, SoH, Combined Level, Charging State, Remaining/Full/Design Capacity, Cycles, Temperature, Min/Max Cell Temp, Voltage, Min/Max Cell Voltage

**Power (8):** Total Input/Output, AC Input/Output Power, AC Input/Output Voltage, Solar Input, DC Output

**USB / Type-C (6):** Type-C 1/2, USB 1/2, USB QC 1/2

**Time (3):** Charge/Discharge Remaining, Remaining Time

**Inverter (1):** Inverter Output Temperature

**Slave battery (14):** Mirrors main battery sensors for optional extra battery pack

### Delta 2 Max — Sensors (68)

**Battery (14):** Battery Level, SoH, Combined Level, Remaining/Full/Design Capacity, Cycles, Temperature, Min/Max Cell Temp, Voltage, Min/Max Cell Voltage, Battery Level SOC

**Accumulative energy (2):** Cumulative Charge/Discharge Energy

**Power (6):** Total Input/Output, AC Input/Output Power, AC Input/Output Voltage

**Solar — dual MPPT (7):** Solar 1/2 Input Power/Voltage/Current, DC Output Power

**USB / Type-C (6):** Type-C 1/2, USB 1/2, USB QC 1/2

**Time (2):** Charge/Discharge Remaining

**Inverter (1):** Inverter Output Temperature

**Slave 1 battery (15):** Full mirror including SoH and Battery Level SOC

**Slave 2 battery (15):** Full mirror including SoH and Battery Level SOC

### Gen 1 shared sensors (Delta Pro, Delta Max, Delta Mini)

**Base (34):** Battery Level, Level (precise), SoH, Combined Level, Remaining/Full/Design Capacity, Cycles, Temperature, Min/Max Cell Temp, Current, Voltage, Min/Max Cell Voltage, Total Input/Output, AC Input/Output Power/Voltage, Solar Input Power/Voltage/Current, DC Output Power/Voltage, Type-C 1/2, USB 1/2, USB QC 1/2, Charge/Discharge Remaining

**Energy (5):** Solar Input Energy, AC Charge/Discharge Energy, DC Charge/Discharge Energy

**Slave battery (16 per unit):** Level, Level (precise), SoH, Temp, Voltage, Current, Min/Max Cell Temp/Voltage, Remaining/Full/Design Capacity, Cycles, Input/Output Power

| Device | Base | Extra | Energy | Slaves | Total |
|--------|------|-------|--------|--------|-------|
| Delta Pro | DCAB, DCEB | +2 (DC Car, Anderson) | 5 | 2×16 | **57** |
| Delta Max | DAAB, DAEB | +1 (DC Car) | 5 | 2×16 | **56** |
| Delta Mini | DAAZ, DBEB, DBKB, DBAB | +2 (DC Car, Anderson) | 5 | none | **41** |

### River 2 / River 2 Max — Sensors (31)

**Battery (29):** Battery Level, SoH, Combined Level, Charging State, Remaining/Full/Design Capacity, Cycles, Temperature, Min/Max Cell Temp, Voltage, Min/Max Cell Voltage, Total Input/Output, AC Input/Output Power/Voltage, Solar Input Power, DC Output, Type-C, USB 1/2/3, Charge/Discharge Remaining, Inverter Inside/Outside Temp

**DC Solar (2):** DC Solar Input Voltage, DC Solar Input Current

### River 2 Pro — Sensors (29)

Same as River 2 base sensors (29) — no DC solar sensors.

### River Max — Sensors (97), River Pro — Sensors (65), River Mini — Sensors (33)

Detailed sensor lists for Gen 1 River devices. These use the same categories as Gen 1 Delta (battery, power, USB, time) with model-specific variations. River Max includes slave battery support.

### PowerStream — Sensors (21)

**Solar 1 (5):** Watts, Input Voltage, Op Voltage, Current, Temperature

**Solar 2 (5):** Watts, Input Voltage, Op Voltage, Current, Temperature

**Battery (5):** Charge Level, Input Watts, Temperature, Charge/Discharge Time

**Inverter (3):** Output Watts, Frequency, Temperature

**System (3):** ESP Temperature, Other Loads, Rated Power

### Glacier — Sensors (21)

**Battery (14):** Level, Combined Level, Remaining/Full/Design Capacity, Charging State, Input/Output Power, Motor Power, Charge/Discharge Remaining, Cycles, Temperature, Voltage

**Fridge temperatures (5):** Ambient, Exhaust, Water, Left Zone, Right Zone

**Ice maker (2):** Time Remaining, Ice Percentage

### Wave 2 — Sensors (13)

**Battery (5):** Level, Temperature, Remaining Capacity, Charge/Discharge Remaining

**Power (6):** PV Input, Battery Output, PV Charging, AC Input, System Power, Motor Power

**Climate (2):** Set Temperature, Ambient Temperature

---

## How It Works

```
EcoFlow Cloud (App Login mode — recommended for Delta 3)
 |
 +-- REST API (App Login — Email + Password)
 |   +-- /auth/login                    -> token + userId
 |   +-- /iot-auth/app/certification    -> MQTT credentials (renewed every 10 min)
 |
 +-- MQTT TLS :8883  mqtt-e.ecoflow.com
     subscribe: /app/device/property/{sn}                  (telemetry push)
     set:       /app/{userId}/{sn}/thing/property/set       (JSON SET commands)
     set_reply: /app/{userId}/{sn}/thing/property/set_reply (command ACK)
     get:       /app/{userId}/{sn}/thing/property/get       (GET-ALL keepalive every 20s)

SET command payload:
  {"id":<seq>, "version":"1.0", "sn":"<SN>", "moduleType":<n>,
   "operateType":"<cmd>", "from":"Android", "params":{...}}

REST API: used only for MQTT credential retrieval. SET commands blocked for D361 series.
```

MQTT push is the primary data source. Telemetry frequency varies by module:
- `pd.*` keys: every ~3 seconds
- `mppt.*` keys: every ~3-5 minutes (full upload), ~2 minutes (incremental)
- `bms_emsStatus.*` / `bms_bmsStatus.*`: every ~3 seconds

MQTT credentials are renewed every 10 minutes (periodic recertification) — this is normal behaviour and does not interrupt telemetry.

---

## Diagnostic Tools

Test scripts in the `examples/` directory:

| Script | Purpose |
|--------|---------|
| `test_credentials.py` / `.ps1` | Developer API credentials against EU/US/Global servers |
| `test_developer_api.py` / `.ps1` | Signing validation, device list, MQTT credentials, quota GET + SET |

```bash
# Python
pip install requests
python3 examples/test_developer_api.py

# PowerShell
PowerShell -ExecutionPolicy Bypass -File examples/test_developer_api.ps1
```

---

## Debug Logging

```yaml
# configuration.yaml
logger:
  logs:
    custom_components.ecoflow_cloud: debug
```

---

## Device Support (v0.3.10)

| Device | SN Prefix | Protocol | Sensors | Switches | Numbers | Selects | Status |
|--------|-----------|----------|---------|----------|---------|---------|--------|
| Delta 3 1500 | D361, P231 | JSON SET | ~80 | 13 | 9 | 5 | ✅ Live tested |
| Delta 3 Plus | D362, P351 | JSON SET | ~91 | 13 | 9 | 5 | ✅ Added v0.3.9 (+PV2) |
| Delta 3 Max | D381, D3N1 | JSON SET | ~107 | 13 | 9 | 5 | ✅ Added v0.3.9 (+PV2+diag) |
| **Delta 3 Max Plus** | D3M1 | Developer API: flat keys + dp3 command envelope | 20 | 7 | 3 | — | ✅ v0.4.0 live tested (read + control) |
| Delta Pro 3 | DGEA, MR5 | Gen 3 cmdFunc=254 | 14 | 9 | 13 | — | ✅ Full control |
| Delta Pro Ultra | Y71 | cmdCode YJ751 | 45 | 7 | 10 | 1 | ✅ Full control |
| Delta Pro | DAEB | Gen 1 TCP | ~40 | 4 | 4 | 3 | ✅ Full control |
| Delta 2 | R33 | Gen 2 moduleType | ~50 | 8 | 6 | 5 | ✅ Full control |
| Delta 2 Max | R35 | Gen 2 moduleType | ~50 | 7 | 6 | 4 | ✅ Full control |
| Delta Max | DCAB, DAAB | Gen 1 TCP | ~30 | 4 | 4 | — | ✅ Full control |
| Delta Mini | DAAZ, DBEB, DBKB | Gen 1 TCP | ~18 | 1 | 2 | 3 | ✅ Full control |
| River 3 | R64, R65 | Gen 3 cmdFunc=254 | 20 | 6 | 7 | — | ✅ Full control |
| River 3 Plus | R63 | Gen 3 cmdFunc=254 | 20 | 6 | 7 | — | ✅ Full control |
| River 2 | R60 | Gen 2 moduleType | ~30 | 3 | 3 | 3 | ✅ Full control |
| River 2 Max | R61 | Gen 2 moduleType | ~30 | 3 | 3 | 3 | ✅ Full control |
| River 2 Pro | R62 | Gen 2 moduleType | ~30 | 3 | 3 | 3 | ✅ Full control |
| River Max | R601 | Gen 1 TCP | ~28 | 2 | 2 | 2 | ✅ Full control |
| River Pro | R602 | Gen 1 TCP | ~32 | 2 | 2 | 2 | ✅ Full control |
| River Mini | R501 | Gen 1 TCP | ~17 | — | — | — | ✅ Sensors only |
| PowerStream | HW51 | Protobuf | ~25 | 1 | 4 | 1 | ✅ Full control |
| Smart Plug | HW52 | Protobuf | ~8 | 1 | 2 | — | ✅ Full control |
| Glacier | BX1 | Gen 2 moduleType | ~20 | 3 | 3 | — | ✅ Full control |
| Wave 2 | KT2 | Gen 2 moduleType | ~15 | — | 1 | 4 | ✅ Full control |
| Stream AC | BK51 | Protobuf cmdFunc=254 | 18 | — | 2 | — | ✅ Added v0.3.9 |
| Stream AC Pro | BK31, BK41 | Protobuf cmdFunc=254 | 27 | 2 | 5 | — | ✅ Added v0.3.9 |
| Stream Ultra | BK11, BK12, BK61 | Protobuf cmdFunc=254 | 29 | 2 | 5 | — | ✅ Added v0.3.9 |
| **Wave 3** | AC71 | **Protobuf cmdFunc=254** | **25** | **—** | **—** | **—** | **🆕 v0.3.10 read-only** |
| **Glacier 55** | RF45 | **Protobuf cmdFunc=254** | **22** | **4** | **6** | **1** | **🆕 v0.3.10 full control** |
| **Smart Home Panel** | SH10, SP10 | **JSON SET (TCP)** | **45** | **13** | **2** | **—** | **🆕 v0.3.10 full control** |
| **Smart Home Panel 2** | SH20, HD3 | **Protobuf cmdFunc=12** | **5** | **—** | **—** | **—** | **🔶 v0.3.10 sensor stubs** |
| **PowerKit** | M10 | **JSON heartbeat** | **30** | **—** | **—** | **—** | **🆕 v0.3.10 read-only** |
| **PowerOcean** | HJ3, J32 | **Protobuf cmdFunc=96** | **22** | **—** | **—** | **—** | **🔶 v0.3.10 sensor stubs** |
| **PowerOcean Plus** | R37 | **Protobuf cmdFunc=96** | **22** | **—** | **—** | **—** | **🔶 v0.3.10 sensor stubs** |
| **PowerOcean Fit** | HC31 | **Protobuf cmdFunc=96** | **22** | **—** | **—** | **—** | **🔶 v0.3.10 sensor stubs** |

**33 devices with active entity support** + 3 sensor-stub devices awaiting decoder completion.
Protocol variants: Gen 1 (TCP), Gen 2 (moduleType), Gen 3 (cmdFunc=254), Protobuf (PowerStream/Smart Plug/Stream AC/cmdFunc=96), cmdCode (YJ751), JSON SET (Delta 3, SHP1).

Serial prefixes: see [Serial prefix sources](#serial-prefix-sources). A device whose prefix names a model without a profile (Smart Generator `DGEB`, Stream Microinverter `BK01`, Smart Meter `BK21`) is recognised by name and gets no entities yet.
🔶 = entities registered but decoder routing incomplete

---

## Credits and licenses

This integration is licensed under the Apache License 2.0 (see [LICENSE](LICENSE)). Some definitions are derived from a community project that uses the same license; see [NOTICE](NOTICE) and *Inspiration & Acknowledgements* below.

## Changelog

### v0.4.1 -- Serial prefixes, dashboard, recertification

- **Serial prefix table rebuilt** from owner reports and several community projects (see *Serial prefix sources*). Reported in issues #1, #2, #3 and #4.
- Corrected: `R631` is River 3 Plus (was River 2 Max); `R651` is River 3 (was Plus); `DBEB`, `DBKB` and `DBAB` are Delta Mini; `DAAB` and `DAEB` are Delta Max; `DCAB` and `DCEB` are Delta Pro (`DCAB` was Delta Max, `DAEB` was Delta Pro); `Y71` is Delta Pro Ultra and `DGEB` the Smart Generator; `R62` is River 2 Pro (`R621` was River 2); `HW52` is the Smart Plug (was PowerStream 800W); `SP10` is Smart Home Panel (was Smart Plug).
- Added: `D3N1`, `P351`, `P231`, `MR5`, `R33`, `R35`, `R60`, `R61`, `R63`, `R64`, `R65`, `BK01` to `BK61`, `BX1`, `RF45`, `KT2`, `AC71`, `HD3`, `M10`, `HJ3`, `J32`, `R37`, `HC31`. The placeholder prefixes (`BKW`, `BX55`, `KT3`, `M106`, `PO11`, `PO31`, `POFI`) and the catch-all `BK` are replaced by these.
- Stream Pro (`BK12`), Stream Max (`BK41`) and Stream Ultra X (`BK61`) share the profile of a sibling model; the entities have not been verified on those models. Models without a profile (Smart Generator, Stream Microinverter, Smart Meter) are recognised by name and get no entities yet.
- The River 3 and River 3 Plus routes follow the River 3 series (App Login in Auto-detect; REST SET blocked); the same holds for the added Delta 3 prefixes.
- Remove the integration entry and add it again to apply a corrected model to an existing device.
- Untested on real devices: only the Delta 3 Max Plus and the Delta 3 1500 are owned by the author.
- Open API route: the periodic recertification (every 10 minutes) now runs only on the App Login route. On the Open API route it could only skip, which logged the warning `recertification returned empty client_id` twice per cycle and called EcoFlow for nothing.
- Cleanup: the duplicate brand folder in the repository root is gone; the icon lives in `custom_components/ecoflow_cloud/brand/`.
- Known gap: River 3 telemetry over App Login is not decoded yet (see Not ported yet below).
- **Dashboard:** the Overview tab follows the hand-tuned layout (header with badges, gauges, a *Control* section with the three output switches, Energy Backup and the three limit sliders, and a smaller *Power flow* section; the USB and battery sections are gone). AC Output 2 and DC 12V Output are disabled by default: enable them to get their tiles. The three History charts now have a heading each, output above and input below the zero line, a dashed battery level, a power axis that scales with the data (no fixed 3000 W) and a 5-minute mean for the last 24 hours. Press **Configure → Replace the dashboard with a fresh one** to get the new layout; `dashboard/ecoflow_max_plus.yaml` is regenerated.

### v0.4.0 -- Delta 3 Max Plus, diagnostics, dashboard, device profiles

- **Delta 3 Max Plus** (`D3M1`) with its own flat-key profile: 20 sensors, 7 switches, 3 numbers. Auto-detect selects the Developer API for it. Control uses the Delta Pro 3 command envelope; `set_reply` is subscribed and logged. Live tested (read and control).
- **Diagnostics download** (device state, unmapped keys, MQTT topics and counters, last 50 raw MQTT messages). Credentials are removed and serial numbers are masked, also inside binary messages.
- **Dashboard** *EcoFlow Max Plus*, created once for the Delta 3 Max Plus (Overview and History views), with a manual copy in `dashboard/ecoflow_max_plus.yaml`. **Configure → Replace the dashboard with a fresh one** rebuilds it.
- **Device profile update from EcoFlow documentation**: 223 extra sensors for 18 existing models and three controls (River 2 Pro backup reserve, Wave 2 temperature unit, Delta Pro 3 24 V DC output). All are disabled by default and marked as untested on real devices. They live in the new package `custom_components/ecoflow_cloud/profiles/`: one module per device model (like `devices/`), each with its SENSORS, NUMBERS, SWITCHES and SELECTS. Delta Pro 3 selects can send the Developer API command format.
- **Documentation and repository files**: short `README.md`, this technical reference, `hacs.json`, a "New model report" issue template and a validation workflow.
- **License**: Apache License 2.0 (`LICENSE`, `NOTICE`).
- Not ported yet: devices that speak protobuf only (River 3, Wave 3, Stream series, Smart Home Panel 3, Ocean Pro and others). They need a schema-driven decoder and are planned as a separate step.

### v0.3.10 -- Climate + Smart Home Panel + PowerKit + PowerOcean

**Climate devices**

- **Wave 3** (mobile AC with battery, placeholder SN: KT3): protobuf cmdFunc=254
  family, 25 sensors covering ambient temperature/humidity, supply air,
  condensate level, operating mode, battery, AC/PV/DC power. Read-only in
  this release -- foxthefox documents //cmd markers but no SET implementation.
- **Glacier 55** (dual-zone portable refrigerator, placeholder SN: BX55):
  protobuf cmdFunc=254, 22 sensors + 4 switches (child lock, simple mode,
  temp alert, beep) + 6 numbers (left/right setpoints as **floats**, max/min
  SOC, standby, battery protect) + 1 select (cooling mode Eco/Max/Sleep).
  First device using the new `_ff()` IEEE 754 float helper for SET commands.

**Smart Home Panel**

- **SHP1 / Smart Home Panel** (SH10): JSON SET protocol with `operateType: TCP`.
  45 sensors (per-circuit power/current/name + system stats + EPS + thresholds)
  + 13 switches (12 channel-controls + EPS mode) + 2 numbers (backup discharge
  thresholds). Activates the SH10 stub registered in v0.3.9.
- **SHP2 / Smart Home Panel 2** (SH20): protobuf cmdFunc=12 (ProtoPushAndSet).
  5 sensor stubs registered. Full decoder routing for cmdFunc=12 lands in
  a later version -- entities will activate automatically once decoder support is added.

**PowerKit** (modular off-grid system, placeholder SN: M106)

- Read-only by design -- foxthefox documents only GET commands. ~30 core
  sensors selected from 215+ telemetry fields across submodules: bp1
  (primary battery), bp2, bbcin/bbcout (DC-DC), iclow/ichigh (chargers),
  ldac/lddc (load AC/DC), kitscc (solar), wireless. Uses dotted prefix
  keys (`bp1.soc`, `ldac.outWatts`).

**PowerOcean / PowerOcean Plus / PowerOcean Fit** (residential energy storage)

- Tesla Powerwall / Sessy / Sonnen-class home battery + hybrid inverter.
  v0.3.10: SN-prefix detection (PO11/PO31/POFI placeholders) + 22 sensor
  stubs covering battery/EMS/PCS/grid safety. Full protobuf decoder for
  cmdFunc=96 (JTS1_EMS_HEARTBEAT) and cmdFunc=254/cmdId=32
  (EnergyTotalReport) coming in a later version.

**Decoder routing**

- `decode_proto_telemetry()` now accepts a `device_model` parameter to
  disambiguate cmdFunc=254/cmdId=21 telemetry between device families that
  share field numbers but differ in semantic meaning. Fixes a field 777
  conflict between Wave 3 (`powGetSelfConsume` in W) and Glacier 55
  (`inputVolt777` in V) -- both would have produced wrong sensor values
  on the same-numbered field.

**SN-prefix registry updates**

- KT3 (Wave 3), BX55 (Glacier 55), M106 (PowerKit)
- PO11 / PO31 / POFI (PowerOcean variants)
- Total registered models: 35 (was 30 in v0.3.9)

**Note on placeholder SN prefixes**

Several new devices (Wave 3, Glacier 55, PowerKit, PowerOcean variants)
ship with placeholder SN prefixes inferred from foxthefox naming patterns.
If your device is misdetected, please open a GitHub issue with your full
SN string -- prefixes will be corrected and a v0.3.10.x patch released.

### v0.3.9 -- Stream AC family (protobuf grid-tied inverter) + Delta 3 Plus/Max

**Stream AC / AC Pro / Ultra -- protobuf telemetry + control**

- New device family: grid-tied micro-inverter with optional 1920Wh LFP battery
- Protobuf protocol (cmdFunc=254) with IEEE 754 float decoding for wire type 5
- **Latest-quotas keepalive** (foxthefox pattern): minimal setMessage ping every 15s
  to keep DisplayPropertyUpload telemetry flowing
- **Model-specific entity sets** (v0.3.9 split):
  - Stream AC (BK?1Z): pure inverter -- 18 sensors, 0 switches, 2 numbers
  - Stream AC Pro (BK31Z): inverter + battery + PV2 -- 27 sensors, 2 switches, 5 numbers
  - Stream Ultra (BK11Z): inverter + battery + 4xPV -- 29 sensors, 2 switches, 5 numbers
- Paired SOC commands (max/min must be sent together) via coordinator lookup
- ConfigWriteAck (cmdId=18) decoder for command confirmation
- New diagnostic sensors (disabled by default): feedGridMode, stormPatternEnable,
  stormPatternOpenFlag -- community reverse-engineering aid

**Delta 3 Plus (D362) + Delta 3 Max (D381)**

- Full device support added (previously fell back to diagnostic mode)
- Command set identical to Delta 3 1500 -- all 18 commands reused
- Plus adds 11 PV2 MPPT input sensors (second solar channel)
- Max adds 16 diagnostic sensors (DCDC, LLC, PFC, 12V aux, PV voltage refs)
- All new sensors disabled by default until live telemetry confirms dotted prefix

**SN prefix registry updates**

- BK, BK31, BK11 for Stream AC family
- SH10, SH20 for Smart Home Panel 1/2 (prefix only, entities TBD in future release)

### v0.3.7 -- River 3/3 Plus + DPU showFlag + AC DSG fix

**New devices: River 3 (R641) and River 3 Plus (R651):**
- Gen 3 protocol (cmdFunc=254) — same command envelope as Delta Pro 3
- New device file: `devices/river3.py` with flat quota keys from community MQTT data
- 20 sensors: SOC, SOH, total power in/out, per-port power (AC, USB, Type-C, 12V, PV), temperatures, settings readback
- 6 switches: AC Output, DC 12V, X-Boost, Beep, Output Memory, Energy Backup
- 7 numbers: Max/Min SOC, Device/Screen/AC standby, AC charging power, Solar max current
- Source: foxthefox/ioBroker.ecoflow-mqtt river3plus.md (community-confirmed via live MQTT)

**Switch `is_on` fix for River 3 flow keys:**
- River 3 uses `0=off, 2=on` for flow status keys (not `0/1` like other devices)
- Changed `is_on` from `int(val) == 1` to `int(val) != 0` — covers both conventions safely

**DPU switches now use telemetry-confirmed state instead of optimistic updates:**
- AC Output (bit 2), DC Output (bit 5), Battery Heating (bit 1) read actual state from `showFlag` bit field
- Removed `optimistic=True` from these three switches — state updates arrive via MQTT telemetry push
- Battery Heating moved from `bmsModeSet` quota key to `showFlag` with `inverted=True` (bit 1: 0=enabled, 1=prohibited)

**New named constants in `delta_pro_ultra.py`:**
- `SHOW_FLAG_BIT_HEAT = 1`, `SHOW_FLAG_BIT_AC = 2`, `SHOW_FLAG_BIT_DC = 5`
- Replaced magic numbers in switch definitions with named constants
- Removed unused `extract_show_flag_bit()` helper function (logic is inline in `is_on` property)

**AC DSG combined command: read current values from coordinator:**
- `YJ751_PD_AC_DSG_SET` sends enable + xboost + freq in one command
- Now reads actual `acXboost` and `acOutFreq` from coordinator data instead of 255 sentinel

**Device count:** 22 devices total (20 previous + River 3 + River 3 Plus). All with full control.

### v0.3.6 -- Delta Pro Ultra full implementation (cmdCode protocol)

**New device: Delta Pro Ultra (DGEB) — fully implemented:**
- New cmdCode protocol: `YJ751_PD_*` command codes instead of moduleType/operateType
- New prefixed quota keys: `hs_yj751_pd_appshow_addr.*`, `hs_yj751_pd_app_set_info_addr.*`, `hs_yj751_pd_backend_addr.*`
- 12 SET commands implemented via REST PUT and MQTT
- ~45 sensors: SOC, total power in/out, per-port AC power (6 ports), DC/USB/Type-C, solar HV/LV, V/A per port
- 6 switches: AC Output, X-Boost, DC Output, Battery Heating, 4G, AC Always-On + Energy Management (read-only)
- 8 numbers: Max/Min SOC, AC/DC/Device standby, Screen standby, AC charging power, POWER IN/OUT charging power + AC Always-On Min SOC, Backup Reserve SOC
- Source: official EcoFlow developer docs (developer-eu.ecoflow.com/us/document/deltaProUltra)

**DPU showFlag bit field parsing:**
- AC Output reads bit 2, DC Output reads bit 5 from showFlag integer
- New `show_flag_bit` field on SwitchDescription for bit extraction in `is_on`

**Additional DPU entities:**
- Energy Management switch (read-only)
- AC Always-On Min SOC number
- Backup Reserve SOC number (read-only)
- Operating Mode select (Default/Self-powered/Scheduled/TOU)

**Fixes:**
- Delta 3 Plus and Delta 3 Max added to select.py model registry (prevented crash)
- Delta Pro 3 added to select.py model registry
- AC_DSG combined command uses 255 sentinel to preserve current xboost/freq values

**New API method: `set_quota_cmdcode()`:**
- Added to both `EcoFlowAPI` and `EcoFlowPrivateAPI` for cmdCode-based SET commands
- REST: `PUT /iot-open/sign/device/quota` with `{sn, cmdCode, params}`
- MQTT: `{id, version:"1.0", cmdCode:"YJ751_PD_*", params:{...}}`

**Platform updates for cmdCode routing:**
- `switch.py`: new `dpu_cmd_code` + `dpu_cmd_params` fields, cmdCode publish path (Priority 2.6)
- `number.py`: new `dpu_cmd_code` + `dpu_cmd_param_key` fields, cmdCode publish path (Priority 2.6)
- `button.py`: DPU registered (no buttons in DPU docs)
- `sensor.py`: ~45 DPU sensors registered across 3 namespaces

**Device count:** 20 devices total (19 previous + Delta Pro Ultra). All with full control.

### v0.3.5 -- Repository rename + device profile verification

**Repository renamed:** `hassio-ecoflow-eu-delta3` → `hassio-ecoflow-eu`
- All URLs updated: manifest.json, README badges, HACS links, push script
- GitHub redirects ensure existing installations continue to work

**Device profile verification against official EcoFlow developer docs:**
- Verified all 10 documented devices against developer-eu.ecoflow.com
- 9 of 10 devices fully functional, 1 (Delta Pro Ultra) registry-only
- All core functions (AC/DC control, charge/discharge limits, X-Boost) confirmed correct
- Protocol formats validated: Gen 1 (TCP), Gen 2 (moduleType), Gen 3 (cmdFunc=254), Protobuf

**Verification summary (SET commands coverage):**
- Delta Pro: 4/6 switches, 4/9 numbers — core complete
- Delta 2: 8/8 switches, 6/11 numbers — switches complete
- Delta 2 Max: 7/9 switches, 6/11 numbers — core complete
- Delta Pro 3: 9/9 switches, 13/16 numbers, 1 button — near-complete
- Smart Plug: 1/1 switches, 2/2 numbers — fully complete
- PowerStream: 1/2 switches, 4/4 numbers — numbers complete
- Wave 2: 4/4 selects, 1/1 numbers — fully complete
- Glacier: 3/3 switches, 3/3 numbers, 3 buttons — fully complete
- River 2 Pro: 3/3 switches, 3/3 numbers — fully complete
- Delta Pro Ultra: registry only in v0.3.5 (cmdCode protocol — implemented in v0.3.6)

19 devices total. All with full control (except Delta Pro Ultra — registry only).

### v0.3.4 -- Protobuf telemetry decoder (Smart Plug + PowerStream sensors live)

**Protobuf telemetry decoder:**
- Binary MQTT messages (protobuf) are now decoded and fed into the coordinator
- Previously these messages were logged but discarded — sensors never received data
- Generic decoder in proto_codec.py: parses EcoFlow envelope → extracts header (cmd_func, cmd_id) → maps pdata fields to coordinator keys

**Smart Plug (SP10) — now full control (was commands-only):**
- 5 sensor entities now receive live data: Power, Voltage, Current, Temperature, Frequency
- Heartbeat telemetry (WnPlugHeartbeatPack, cmdFunc=2) decoded with 11 field mappings
- Promotes Smart Plug from commands-only to full control (16 devices, all full control)

**PowerStream — protobuf sensor path enabled:**
- inverter_heartbeat (cmdFunc=20) decoded with 56 field mappings
- Covers all solar, battery, inverter, LLC, and system sensors
- Works alongside existing JSON path — protobuf data merges into coordinator

**Infrastructure:**
- `decode_proto_telemetry()` in proto_codec.py: header extraction + field mapping per cmdFunc
- `_parse_fields()`: generic protobuf wire-format parser (varint, LEN, fixed32, fixed64)
- `_extract_header()`: EcoFlow envelope parser (pdata, src, dest, cmd_func, cmd_id)
- Field mapping tables: `_PS_HEARTBEAT_FIELDS` (56 fields), `_SP_HEARTBEAT_FIELDS` (11 fields)
- Extensible: add new device decoders by adding a cmdFunc entry to `_HEARTBEAT_DECODERS`

**Output Memory (D361) — state retrieval at startup:**
- `pd.outputMemoryEn` is not included in latestQuotas or regular telemetry push
- Added `getOutputMemory` JSON GET to the MQTT init sequence (step 5)
- Switch now enabled by default with `optimistic=True` for immediate toggle feedback
- Initial state loaded from device reply at startup

16 devices total, all with full control.

**Delta Pro 3 (DGEA) — full device profile (17th device):**
- New command protocol: `{sn, cmdId:17, cmdFunc:254, dest:2, dirDest:1, dirSrc:1, needAck:true, params:{...}}`
- Flat quota keys (no pd./mppt. prefix): `enBeep`, `cmsMaxChgSoc`, `flowInfoAcHvOut`, etc.
- 14 sensors: charge limits, standby timers, power settings, generator SOC thresholds
- 9 switches: Beep, X-Boost, AC HV/LV Output, DC 12V, Energy Backup, Generator Auto-Start, GFCI, AC Energy Saving
- 13 numbers: Max/Min SOC, AC/DC/Device standby times, LCD brightness, AC charging power, solar current limits, generator SOC
- 1 button: Power Off
- DP3 command dispatch added to switch.py, number.py, button.py (Priority 2.5)
- Device profile: `devices/delta_pro_3.py` with 26 quota keys + 26 command keys + envelope constants
- Source: Official EcoFlow Developer Platform docs (developer-eu.ecoflow.com/us/document/deltaPro3)

17 devices total (16 original + Delta Pro 3). All with full control.

**Delta 3 Plus (D362) + Delta 3 Max (D381) — same protocol as D361:**
- Registered in sensor, switch, number, button registries using D361 definitions
- Same JSON MQTT SET protocol, same dotted quota keys, same commands
- Already in device registry (SN prefix detection) and REST_SET_BLOCKED list

19 devices total. All with full control.

### v0.3.3 -- D361 Beep Sound fix + Bypass optimistic + tested live

**Beep Sound fix (D361) -- confirmed working via live test:**
- Added `inverted=True` -- mppt.beepState=1 means quiet mode ON (sound OFF)
- Switch now correctly shows ON when sound is actually ON, OFF when muted
- Command confirmed: quietMode enabled=0 turns sound ON, enabled=1 turns sound OFF

**Bypass (D361) -- confirmed working via live test:**
- Added `optimistic=True` -- state updates immediately after toggle
- pd.acAutoOutPause is always 0 in D361 telemetry (confirmed: does not change even via app)
- Command works: ack=1, relaySwitchCnt increments, app confirms state change
- Enabled by default (was disabled)

**UPS Mode (D361) -- diagnostic only:**
- openUpsFlag is firmware-controlled (AC pass-through based on battery state + AC input)
- Command accepted (ack=1) but not a user-toggleable switch in the EcoFlow app
- Kept as disabled-by-default diagnostic entity

### v0.3.2 -- Glacier buttons + Smart Plug + PowerStream sensor fix

**Glacier (BX11) — 3 buttons added:**
- Make Small Ice, Make Large Ice, Detach Ice (new button platform)

**Smart Plug (SP10) — device profile + commands (16th device):**
- 5 sensors: Power, Voltage, Current, Temperature, Frequency
- 1 switch: Power on/off
- 2 numbers: LED Brightness (0-1023), Max Power (0-2500W)
- Uses protobuf binary protocol (cmdFunc=2, same envelope as PowerStream)
- NOTE: sensor telemetry requires protobuf decoder in MQTT handler (commands work, sensors pending)

**PowerStream sensor scaling fix:**
- All PowerStream sensors now correctly scaled: deciWatts→Watts, deciVolts→Volts, deciAmps→Amps, deciCelsius→Celsius, deciHz→Hz
- Output Limit number uses state_scale=0.1 so slider and sensor stay in sync

**Bug fix: bms_slave comma-decimal (v0.2.25 backlog):**
- Sensors receiving comma-decimal strings (e.g. bms_slave.diffSoc = "1,11") now parse correctly instead of falling back to string state
- Affects bms_slave.diffSoc, bms_slave.cycSoh, bms_bmsStatus.diffSoc, bms_bmsStatus.cycSoh on Delta 3 1500

**Infrastructure:**
- New button platform (button.py) with EcoFlowButtonDescription + JSON command dispatch
- Added `state_scale` to EcoFlowNumberDescription for numbers where raw MQTT value differs from display unit
- 3 Smart Plug protobuf command builders in proto_codec.py (switch, brightness, max_watts)

16 devices total. 15 with full control, 1 commands-only pending sensor decoder (Smart Plug).

### v0.3.1 -- Gen 1 full control + PowerStream, Glacier, Wave 2

**Gen 1 devices now have switches, numbers, and selects:**
- Delta Pro (DAEB) -- 6 switches, 6 numbers, 4 selects
- Delta Max (DCAB) -- 7 switches, 5 numbers
- Delta Mini (DAAZ) -- 4 switches, 3 numbers, 4 selects
- River Max (R601) -- 5 switches, 1 number, 3 selects
- River Pro (R602) -- 7 switches, 1 number, 3 selects
- River Mini (R501) -- 2 switches, 1 number

Gen 1 TCP commands (moduleType=0, operateType=TCP, params.id) work through the existing _publish() infrastructure -- no protocol changes needed.

**New device profiles:**
- PowerStream / 600W / 800W (HW51, HW52, BKW) -- 21 sensors + 1 switch + 4 numbers + 1 select (full control, protobuf binary protocol)
- Glacier (BX11) -- 21 sensors + 3 switches + 3 numbers (full control, JSON protocol)
- Wave 2 (KT21) -- 13 sensors + 1 number + 4 selects (full control, JSON protocol)

Glacier and Wave 2 use JSON protocol (moduleType=1) -- same infrastructure as Gen 1/Gen 2.
PowerStream uses protobuf binary protocol with pure-Python encoder -- no protobuf library dependency.

**Infrastructure:**
- Added `proto_builder_sn` to switch/number/select descriptions for protobuf binary commands (PowerStream)
- Added `cmd_params_coord_fn` to EcoFlowNumberDescription for commands needing sibling entity state (Glacier temp sync)
- Dispatch priority in all _publish(): REST API > Proto binary > JSON MQTT
- 6 PowerStream protobuf command builders in proto_codec.py

15 devices total. All 15 with full control.

### v0.3.0 – Multi-device architecture + 12 device profiles

**Architecture: multi-device support**
- Added device registry (`devices/registry.py`) with SN prefix to model mapping for 27+ EcoFlow devices
- Device model is now auto-detected from serial number at setup time
- Entity descriptions are dispatched per device model -- platform files (sensor.py, switch.py, number.py, select.py) load the correct description tuple based on detected device
- DeviceInfo (model name in HA UI) is now dynamic instead of hardcoded
- All entity unique_ids unchanged -- zero breaking changes for existing Delta 3 1500 users
- Integration name updated from "EcoFlow Cloud (EU Delta 3)" to "EcoFlow Cloud"

**Gen 2 devices -- full control (sensors + switches + numbers + selects):**
- Delta 3 1500 (D361) -- 185 sensors, 13 switches, 9 numbers, 5 selects
- Delta 2 (R331) -- 46 sensors, 8 switches, 6 numbers, 5 selects
- Delta 2 Max (R351) -- 68 sensors, 7 switches, 6 numbers, 3 selects (dual solar, dual slave)
- River 2 (R621) -- 32 sensors, 5 switches, 4 numbers, 5 selects
- River 2 Max (R631) -- 32 sensors, 5 switches, 4 numbers, 5 selects
- River 2 Pro (R622) -- 30 sensors, 3 switches, 3 numbers, 5 selects

**Gen 1 devices -- read-only sensors (TCP command protocol not yet supported):**
- Delta Pro (DAEB) -- ~57 sensors incl. dual slave + energy counters
- Delta Max (DCAB) -- ~56 sensors incl. dual slave + energy counters
- Delta Mini (DAAZ) -- ~40 sensors incl. energy counters
- River Max (R601) -- ~38 sensors incl. slave + energy counters
- River Pro (R602) -- ~32 sensors incl. slave + energy counters
- River Mini (R501) -- ~17 sensors incl. energy counters

**Device detection (SN prefix mapping):**
- Delta series: D361, D362, D381, DGEA, DGEB, DAEB, R331, R351, DCAB, DAAZ
- River series: R641, R651, R621, R631, R622, R601, R602, R501
- PowerStream: HW51, HW52, BKW
- Smart Plug: SP10
- Climate: BX11, KT21

### v0.0.1 – v0.2.25 -- Delta 3 1500: connection, control and telemetry (summary)

The first releases built the integration around the Delta 3 1500 (`D361`). Detailed notes of v0.0.1–v0.2.10 were not kept; v0.2.11–v0.2.25 in short:

**Connection**
- Hybrid mode: REST SET through the Developer API, with the HMAC signing corrected (v0.2.21).
- MQTT: `set_reply` and `get_reply` subscriptions, periodic recertification of the credentials, client id recertification, QoS 1, command id overflow fixed (v0.2.14–v0.2.17).
- `proto_codec.py`, a pure-Python protobuf encoder for Delta 3 SET commands (v0.2.19).

**Control (v0.2.22)**
- The breakthrough: the Delta 3 takes JSON MQTT SET with `"from": "Android"`; the REST API answers code 1006 for `D361`. REST SET is skipped for `D361`, `D362`, `D381`, `R641` and `R651` by serial prefix.
- All switch and number command parameters corrected from the protocol analysis.

**Telemetry (v0.2.23)**
- The coordinator mapped the short typeCodes (`pdStatus`, `mpptStatus`, `invStatus`, …) wrongly, so sensors only updated while the EcoFlow app was open; fixed with a typeCode → module prefix mapping.
- `cfgChgWatts = 255` (the "keep current value" sentinel) is filtered out, and the AC Charging switch no longer writes 255 W as the charge speed.

**Entities**
- A select platform (DC Charge Current, Screen Timeout, standby times), Bypass, Generator SOC, Output Memory, Backup Reserve, UPS Mode, a Connection Mode sensor.
- 68 more sensors, all disabled by default (extended BMS, EMS, MPPT, PD and INV keys), and the `bms_slave.*` sensors of an extra battery (v0.2.25).

**Corrections**
- AC Output Standby Time sends `standbyTime` (mod5) with `standbyMins`; Screen Timeout sends only `delayOff`.
- AC Charging is read-only (`chgPauseFlag` has no effect on `D361`); the Bypass switch is no longer inverted; Battery Protection SOC removed as a duplicate of Min Discharge Level; Backup Reserve reads `pd.watchIsConfig`.

**Housekeeping**
- `manifest.json` key order, `brand/icon.png`, GitHub Actions `checkout@v5`.

What the live tests showed about the `D361` is in the section *D361-Specific Behaviour* above.

---

## Serial prefix sources

EcoFlow publishes no table of serial prefixes. The table in `devices/registry.py` is compiled from the sources below; every entry there names the source it rests on. Only the prefix of a model, a fact about the hardware, was taken from these projects: no code and no text. The licences are listed for reference.

| Source | Licence | Used for |
|--------|---------|----------|
| Owner reports in the issues of this repository, and the author's own devices | -- | `D361`, `D3M1`, `DAAB`, `DBEB`, `DBKB`, `R631`, `R651`, `R655` |
| [MichelFR/ha-ecoflow-iot](https://github.com/MichelFR/ha-ecoflow-iot), `KNOWN_PREFIXES.md` | MIT | Prefix families (`R60`, `R61`, `R62`, `MR5`, `Y71`, `DCAB`, `DCEB`, `D3N1`, `HW51`, `HW52`, `BX1`, `KT2`, `M10`, `HJ3`, `J32`, `HD3`, `BK21`, `DBAB`). It cites the example serials in the EcoFlow developer documentation and the EcoFlow Android app's device-code registry; we have not read those two ourselves |
| [foxthefox/ioBroker.ecoflow-mqtt](https://github.com/foxthefox/ioBroker.ecoflow-mqtt), `lib/ecoflow_data.js` | MIT | Example serials per model (`P231`, `P351`, `R655`, `R631`, `RF45`, `AC71`, `HC31`, `R37`, `SH10`, `SH20`, `DGEB`, `DAEB`, `M106`, `BK11`, `BK31`, `BK61`, `KT21`) |
| [shuette42/ecoflow-energy-ha](https://github.com/shuette42/ecoflow-energy-ha), README and `const.py` | MIT | `R655`, `R631`, `R611`, `D3N1`, `P351`, `P231`, `BK01` to `BK61`, `J32x`, `R37x`, `AC71` |
| [zarbjustin/uk.co.zarb.ecoflow](https://github.com/zarbjustin/uk.co.zarb.ecoflow), README and tests | GPL-3.0 | Cross-check of the Stream prefixes `BK01` to `BK61` |

Where the sources disagree, the entry with the most independent sources wins; the comment in `registry.py` marks the rest. Open points: `DAEB` and `DCAB` (Delta Max, Delta Pro), `R601` and `R602` against `R60`, `R641`, `R651` and the shared profiles of Stream Pro, Stream Max and Stream Ultra X. Report your serial prefix if it is wrong for your device.

---

## Inspiration & Acknowledgements

| Resource | Used for |
|----------|---------|
| [EcoFlow Developer Portal](https://developer-eu.ecoflow.com/us/document/introduction) | Official Open API docs |
| [mmiller7/ecoflow-withoutflow](https://github.com/mmiller7/ecoflow-withoutflow) | App Login protocol analysis, Base64 password |
| [foxthefox/ioBroker.ecoflow-mqtt](https://github.com/foxthefox/ioBroker.ecoflow-mqtt) | Device key reference, set-command payloads |
| [tolwi/hassio-ecoflow-cloud](https://github.com/tolwi/hassio-ecoflow-cloud) | HA integration architecture, Delta 3 proto schema; sensor and control definitions for the v0.4.0 device profile update (Apache License 2.0, see NOTICE) |
| [EcoFlow Developer Docs — Delta 2](https://developer-eu.ecoflow.com/us/document/delta2) | MQTT command reference for D361 |
| [EcoFlow Developer Docs — Delta Pro 3](https://developer-eu.ecoflow.com/us/document/deltaPro3) | Delta 3 protocol schema reference |

---

## Disclaimer

This software is **not affiliated with or endorsed by EcoFlow** in any way. The EcoFlow name, logo, and product names are trademarks of EcoFlow Inc.

This integration uses undocumented private APIs that EcoFlow may change at any time. Provided **"as-is"** without warranty. The authors accept no liability for any damage, loss of data, or service disruption.
