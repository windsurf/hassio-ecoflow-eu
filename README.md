# EcoFlow Cloud – Home Assistant Integration

[![HACS Custom](https://img.shields.io/badge/HACS-Custom-orange.svg)](https://github.com/hacs/integration)
[![GitHub Release](https://img.shields.io/github/release/windsurf/hassio-ecoflow-eu-delta3.svg)](https://github.com/windsurf/hassio-ecoflow-eu-delta3/releases)
[![Validate](https://github.com/windsurf/hassio-ecoflow-eu-delta3/actions/workflows/validate.yml/badge.svg)](https://github.com/windsurf/hassio-ecoflow-eu-delta3/actions/workflows/validate.yml)

> **Disclaimer:** This software is not affiliated with or endorsed by EcoFlow in any way. It is provided "as-is" without warranty or support, for the educational use of developers and enthusiasts. Use at your own risk.

Real-time monitoring and control of EcoFlow power stations via MQTT. Supports two connection modes:

- **App Login** (email + password) — MQTT telemetry + JSON SET control for all devices including Delta 3
- **Developer API** (Access Key + Secret Key) — REST API for device list and credentials (SET commands blocked for D361 series)

> **Actively tested with:** EcoFlow Delta 3 1500 (`D361` series, App Login + MQTT JSON SET)

---

## Installation via HACS

[![Open your Home Assistant instance and open a repository inside the Home Assistant Community Store.](https://my.home-assistant.io/badges/hacs_repository.svg)](https://my.home-assistant.io/redirect/hacs_repository/?owner=windsurf&repository=hassio-ecoflow-eu-delta3&category=integration)

1. Click the button above **or** go to HACS → Integrations → ⋮ → Custom repositories
2. Add URL: `https://github.com/windsurf/hassio-ecoflow-eu-delta3` — category: **Integration**
3. Search for **EcoFlow Cloud** and click **Download**
4. Restart Home Assistant
5. Go to **Settings → Devices & Services → Add Integration → EcoFlow Cloud**

## Manual Installation

1. Download the [latest release](https://github.com/windsurf/hassio-ecoflow-eu-delta3/releases/latest)
2. Extract and copy `custom_components/ecoflow_cloud/` to your HA `config/custom_components/` directory
3. Restart Home Assistant

---

## Getting Credentials

### Option A — App Login *(recommended for Delta 3 and newer devices)*
Use your regular EcoFlow app email and password. No extra setup needed.

### Option B — Developer API
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

Confirmed via protocol analysis (v0.2.23): Delta 3 uses **MQTT JSON SET** with `"from": "Android"` in the payload.

| Function | Channel | Notes |
|----------|---------|-------|
| Real-time sensor data | MQTT push | `/app/device/property/{sn}` |
| Switch/number control | MQTT JSON SET | `"from":"Android"` required |
| REST API SET | Blocked | EcoFlow blocks D361/D362/D381/R641/R651 (code=1006) |

**SET command payload:** `{id, version:"1.0", sn, moduleType, operateType, from:"Android", params:{...}}`

---

## Supported Entities

### Sensors (186)

| Entity | Unit | Default |
|--------|------|---------|
| Battery Level | % | ✅ |
| Battery Level (precise) | % | off |
| State of Health (BMS Status) | % | ✅ |
| Charge Cycles | | ✅ |
| Time Remaining (discharge) | min | ✅ |
| Time to Full (charge) | min | ✅ |
| Battery Voltage | V | ✅ |
| Battery Current | A | ✅ |
| Battery Temperature | °C | ✅ |
| Remaining / Full / Design Capacity | mAh | ✅ / ✅ / off |
| Min / Max Cell Temperature | °C | off |
| Min / Max Cell Voltage | mV | off |
| Max Cell Voltage Difference | mV | off |
| Min / Max MOS Temperature | °C | off |
| Max / Min Charge Level (EMS) | % | ✅ |
| EMS Charge Voltage / Current | V / A | off |
| Fan Level | | off |
| AC Plug Connected | | off |
| System Charge/Discharge State | | off |
| Generator Start SOC | % | off |
| Generator Stop SOC | % | off |
| Extra Battery Power | W | off |
| Extra Batteries Connected | | off |
| **AC / Inverter** | | |
| AC Output Power | W | ✅ |
| AC Input Power | W | ✅ |
| AC Input Voltage / Current / Frequency | V / A / Hz | off |
| AC Output Voltage / Current / Frequency | V / A / Hz | off |
| AC Configured Frequency | Hz | off |
| AC Fast / Slow Charge Watts | W | off |
| Inverter Temperature | °C | off |
| Inverter DC Input Voltage / Current / Temperature | V / A / °C | off |
| **Solar / MPPT** | | |
| Solar Input Power | W | ✅ |
| Solar Input Voltage / Current | V / A | off |
| MPPT Output Power | W | off |
| MPPT Temperature | °C | off |
| DC 12V Output Power | W | ✅ |
| DC 12V Input Power | W | off |
| DC 12V Voltage / Current | V / A | off |
| DC 12V Temperature | °C | off |
| DC 12V Port State | | off |
| DC Output Temperature | °C | off |
| MPPT DC Converter Power | W | off |
| MPPT Beep State | | off |
| **USB / PD** | | |
| Total Input / Output Power | W | ✅ |
| USB-A 1 / 2 Power | W | ✅ |
| USB-A QC 1 / 2 Power | W | ✅ |
| USB-C 1 / 2 Power | W | ✅ |
| USB-C 1 / 2 Temperature | °C | off |
| Solar Charge Power | W | off |
| **Energy totals** | | |
| Cumulative AC / DC Charged | kWh | off |
| Cumulative Charged / Discharged Energy | Wh | off |
| Cumulative Charged / Discharged Capacity | mAh | off |
| **System** | | |
| Battery Protection SOC | % | off |
| WiFi Signal | dBm | off |
| **Battery lifetime** | | |
| State of Health (BMS Info) | % | off |
| Total Charge Cycles | | off |
| Round-Trip Efficiency | % | off |
| Self-Discharge Rate | %/day | off |
| Deep Discharge Count | | off |
| Internal Resistance | mΩ | off |

### Switches (12)

| Entity | Default | Notes |
|--------|---------|-------|
| AC Output | ✅ | Turn 230V output on/off |
| X-Boost | ✅ | Enable/disable X-Boost |
| USB Output | ✅ | USB-A + USB-C ports on/off |
| DC Output | ✅ | Car/Anderson port on/off |
| AC Charging | ✅ | Pause/resume mains charging — temporary, resets on replug |
| Solar Charge Priority | ✅ | Prioritise solar over AC |
| AC Auto-On | off | AC turns on automatically when mains is connected |
| AC Always-On | off | Keep AC on regardless of SOC |
| Backup Reserve | off | Enable/disable backup reserve mode |
| Output Memory | off | Remember output states after power loss |
| Bypass | off | Enable/disable bypass mode |
| Beep Sound | off | Enable/disable device beeps |

### Number Controls (9)

| Entity | Range | Default |
|--------|-------|---------|
| AC Charging Speed | 200–1500 W (step 100) | ✅ |
| Max Charge Level | 50–100% (step 5) | ✅ |
| Min Discharge Level | 0–30% (step 5) | ✅ |
| Generator Start SOC | 0–30% (step 5) | off |
| Generator Stop SOC | 50–100% (step 5) | off |
| Backup Reserve SOC | 0–100% (step 1) | off |
| Min SOC for AC Auto-On | 0–100% (step 5) | off |
| Screen Standby Time (read-only) | min | off |
| Overall Standby Time (read-only) | min | off |

> Note: Battery Protection SOC removed (was duplicate of Min Discharge Level). Device/AC/DC standby moved to Select Controls.

### Select Controls (5)

| Entity | Options | Default |
|--------|---------|---------|
| DC Charge Current | 4 A / 6 A / 8 A | ✅ |
| Screen Timeout | Never / 10s / 30s / 1min / 5min / 30min | off |
| Unit Standby Time | Never / 30min / 1hr / 2hr / 4hr / 6hr / 12hr / 24hr | off |
| AC Output Standby Time | Never / 30min / 1hr / 2hr / 4hr / 6hr / 12hr / 24hr | off |
| DC 12V Standby Time | Never / 30min / 1hr / 2hr / 4hr / 6hr / 12hr / 24hr | off |

> Entities marked **off** are disabled by default. Enable them in Settings → Devices & Services → your device → the entity.

## How It Works

```
EcoFlow Cloud (App Login mode — recommended for Delta 3)
 |
 +-- REST API (App Login — Email + Password)
 |   +-- /auth/login                    -> token + userId
 |   +-- /iot-auth/app/certification    -> MQTT credentials
 |
 +-- MQTT TLS :8883  mqtt-e.ecoflow.com
     subscribe: /app/device/property/{sn}                  (telemetry push)
     set:       /app/{userId}/{sn}/thing/property/set       (JSON SET commands)
     set_reply: /app/{userId}/{sn}/thing/property/set_reply (command ACK)

SET command payload:
  {"id":<seq>, "version":"1.0", "sn":"<SN>", "moduleType":<n>,
   "operateType":"<cmd>", "from":"Android", "params":{...}}

REST API: used only for MQTT credential retrieval. SET commands blocked for D361 series.
```

MQTT push is the primary data source. MQTT JSON SET (with `from:Android`) is the control path for Delta 3. REST SET is auto-skipped for D361/D362/D381/R641/R651.

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

## Changelog


### v0.2.23 – Realtime telemetry fix + AC Charging Speed sync + entity corrections

**Critical fix: typeCode mapping in coordinator**
- Fixed: all telemetry sensors (Total Input Power, AC Input Power, Battery Level, etc.) never updated in HA without opening the EcoFlow app
- Root cause: D361 sends telemetry pushes with short typeCode names (`pdStatus`, `mpptStatus`, `invStatus`) — coordinator was storing them as `pdStatus.*` instead of `pd.*`
- Added typeCode → module prefix mapping: `pdStatus→pd`, `mpptStatus→mppt`, `invStatus→inv`, `bmsStatus→bms_bmsStatus`, `emsStatus→bms_emsStatus`, `bmsInfo→bms_bmsInfo`

**AC Charging Speed (cfgChgWatts=255 sentinel)**
- Fixed: AC Charging Speed slider showed 255W in HA after every keepalive GET-ALL (every 20s)
- Root cause: device always echoes `cfgChgWatts=255` (sentinel meaning "keep current value") in `latestQuotas` reply
- Coordinator now filters 255 from quotaMap; real values still arrive via telemetry push
- Shadow state removed from `number.py` — direct coordinator read with 200W fallback

**AC Charging switch — chgWatts sentinel**
- Fixed: AC Charging switch sent `chgWatts=255` with every toggle, writing 255W as the actual charge speed on the device
- Now sends only `chgPauseFlag` — device keeps current charge speed when chgWatts is omitted

**Entity corrections**
- Backup Reserve switch: `state_key` corrected to `pd.watchIsConfig` (was `pd.bpPowerSoc`)
- Battery Protection SOC: removed — was duplicate of Min Discharge Level (same key + command)
- 4 standby/timeout sliders moved from number.py to select.py with human-readable options

**New entities (68 sensors + 4 selects)**
- Added 68 new sensors (all disabled by default): extended BMS, EMS, MPPT, PD, INV telemetry keys
- Added selects: Screen Timeout, Unit Standby Time, AC Output Standby Time, DC 12V Standby Time
- Added read-only numbers: Screen Standby Time, Overall Standby Time

**GET-ALL after SET**
- Added: after every switch SET command, a `latestQuotas` GET-ALL is sent (1s delay) to refresh state keys that don't update via telemetry push (chgPauseFlag, acAutoOutPause)

**Known limitations**
- AC Charging switch state not reliably reflected in HA after toggle (chgPauseFlag always 0 in quotaMap reply)
- Bypass switch state always shows 0 regardless of actual device state
- Output Memory switch has no telemetry feedback

### v0.2.22 – Major: MQTT JSON control working for Delta 3 (protocol analysis)

**Breakthrough:** Full protocol analysis of EcoFlow Android app confirmed that:
- Delta 3 uses **JSON MQTT SET** (not protobuf, not REST API)
- Payload requires `"from": "Android"` field — without it the device ignores all commands
- REST Developer API returns `code=1006` for D361 series — now auto-skipped by SN prefix

**Fixed: all switch/number command parameters corrected from protocol analysis:**
- `acOutCfg`: `out_voltage=-1`, `out_freq=255`, `xboost=255` (keep-current values)
- `acChgCfg`: `chgPauseFlag=255` (keep-current), `chgWatts=255` for switch
- `ac_auto_on`: `acAutoOnCfg` mod=3 (INV), param `enabled` (was mod=PD, wrong param)
- `bypass`: `bypassBan` + `banBypassEn` (was `acAutoOutConfig` + `acAutoOutPause`)
- `max_charge_level`: `upsConfig` + `maxChgSoc` (was `maxChargeSoc`)
- `min_discharge_level`: `dsgCfg` + `minDsgSoc` (was `minDsgSoc` direct)
- `ac_output_standby`: `standby` mod=5 (was `standbyTime`)
- `dc_charge_current` (select): param key `dcChgCfg` (was `dcChgCurrent`)
- `lcd_brightness`: `brighLevel` + `delayOff=65535` (was wrong param key)
- `ac_auto_on` state_key: `pd.acAutoOnCfg` (was `pd.watchIsConfig`)

**Added:**
- `Output Memory` switch — `outputMemory` operateType, mod=1 (PD)
- `Backup Reserve` switch — `watthConfig` operateType, mod=1 (PD)
- `Backup Reserve SOC` number — `watthConfig` with `bpPowerSoc`
- `Connection Mode` diagnostic sensor — shows `hybrid`/`mqtt_only`/`rest_only`
- `REST_SET_BLOCKED_SN_PREFIXES` — auto-skip REST for D361/D362/D381/R641/R651

**Removed:**
- `UPS Mode` switch — `openUpsFlag` is read-only (protobuf heartbeat only, no SET command)

**Updated (examples/):**
- `test_developer_api.py` / `.ps1` — updated with MQTT JSON SET test (Test 5) and corrected REST SET interpretation for D361

### v0.2.11–v0.2.20 – MQTT protocol analysis, command payload fixes, protobuf, Hybrid Mode

- Fixed: entity ID alignment (`x_boost`, `beep_sound`, `dc12v_standby_time`); log spam reduced to DEBUG (v0.2.11)
- Added: `select.py` platform; DC Charge Current; Bypass switch; Generator SOC controls; 9 new sensors; 4× state_key inv→mppt corrected (v0.2.12)
- Fixed: internal key renames for entity alignment; no entity ID changes in HA (v0.2.13)
- Fixed: `acOutCfg` silent reject (outFreq=50); added set_reply/get_reply subscriptions; periodic MQTT recertification (v0.2.14)
- Fixed: all command payloads corrected (acOutCfg, mpptCar, acChgCfg, quietMode); 5s startup delay replaced by `threading.Timer` (v0.2.15–v0.2.16)
- Fixed: moduleType ac_output→MPPT; command id overflow; client_id recertification; QoS 1; usb_output disabled by default (v0.2.17)
- Added: `proto_codec.py` pure-Python protobuf encoder for Delta 3 SET commands (v0.2.19)
- Fixed: manifest.json key order; brand/icon.png; GitHub Actions checkout@v5; enBeep dataLen=2 (v0.2.20)
- Added: Hybrid Mode — REST API SET via Developer API; HMAC signing corrected; Dutch→English cleanup (v0.2.21)


### v0.2.0–v0.2.10 – Entity overhaul, naming refactor, new entities, command fixes

- Removed 35 low-value sensors from default enabled set; push script now syncs deletions to GitHub (v0.2.0–v0.2.3)
- Fixed: coordinator crash on `bms_kitInfo.watts` array; fixed duplicate sensor IDs; fixed sensors freezing after ~1 min (v0.2.1–v0.2.4)
- Added: AC Charging Speed slider (200–1500W); example dashboard + optimal charging automation (v0.2.6–v0.2.8)
- Refactor: full entity/sensor/number rename (DC 12V, USB/DC split); AC charging speed fix; USB switch moduleType fix (v0.2.9)
- Merged v0.2.8 extras into v0.2.9 base; fixed coordinator log level regression (v0.2.10)
- Added: `select.py` platform; DC Charge Current (4/6/8A); Bypass switch; Generator SOC controls; 9 new sensors (v0.2.12)
- Fixed: 4× switch state_key inv→mppt; command params corrections; `ac_auto_on`/`ac_always_on` separated (v0.2.12)
- Added: `proto_codec.py` protobuf encoder; `threading.Timer` startup delay fix (v0.2.19)
- Added: Hybrid Mode — REST API SET via Developer API; HMAC signing corrected (v0.2.21)
- Fixed: manifest.json key order; `brand/icon.png`; GitHub Actions checkout@v5; `enBeep` dataLen=2 (v0.2.20)

### v0.0.21–v0.1.3

- Fixed: Time to Full key corrected; coordinator MQTT debug logging added (v0.0.21)
- Added 65+ sensors, 9 switches, 9 number controls; full MQTT key coverage for Delta 3 1500; multiple command payload fixes (v0.1.0)
- Fixed: "Time Remaining" / "Time to Full" unavailable after HA restart (v0.1.1)
- Fixed: 85+ entities enabled by default; added `fallback_key` support for resilient key resolution (v0.1.2)
- Fixed: MQTT keepalive 120s, reconnect max 60s, QoS 1 subscribe, log spam reduced to DEBUG (v0.1.3)

### v0.0.11–v0.0.20

- Added App Login mode as alternative to Developer API (v0.0.11)
- Fixed MQTT ClientID format to `ANDROID_{8digits}_{userId_decimal}`; removed `Host` header (v0.0.16)
- Fixed App Login password encoding: Base64 confirmed via mmiller7/ecoflow-withoutflow (v0.0.18)
- Added Auto-detect connection mode based on serial number prefix; added 12 UI translations (v0.0.20)

### v0.0.1–v0.0.10

- Initial versions: entity availability, payload parsing, quota/get, signing algorithm

## Inspiration & Acknowledgements

| Resource | Used for |
|----------|----------|
| [EcoFlow Developer Portal](https://developer-eu.ecoflow.com/us/document/introduction) | Official Open API docs |
| [mmiller7/ecoflow-withoutflow](https://github.com/mmiller7/ecoflow-withoutflow) | App Login protocol analysis, Base64 password |
| [foxthefox/ioBroker.ecoflow-mqtt](https://github.com/foxthefox/ioBroker.ecoflow-mqtt) | Device key reference, set-command payloads |
| [varakh/go-ecoflow](https://pkg.go.dev/git.myservermanager.com/varakh/go-ecoflow) | Command payload reference |
| [berezhinskiy/ecoflow_exporter](https://github.com/berezhinskiy/ecoflow_exporter) | MQTT topic structure, payload keys |
| [tolwi/hassio-ecoflow-cloud](https://github.com/tolwi/hassio-ecoflow-cloud) | HA integration architecture inspiration |
| [snell-evan-itt/hassio-ecoflow-cloud-US](https://github.com/snell-evan-itt/hassio-ecoflow-cloud-US) | Extended device support patterns |
| [STROMDAO MQTT Credentials Tool](https://energychain.github.io/site_ecoflow_mqtt_credentials/) | Credential extraction reference |

---

## Disclaimer

This software is **not affiliated with or endorsed by EcoFlow** in any way. The EcoFlow name, logo, and product names are trademarks of EcoFlow Inc.

This integration uses undocumented private APIs that EcoFlow may change at any time. Provided **"as-is"** without warranty. The authors accept no liability for any damage, loss of data, or service disruption.
