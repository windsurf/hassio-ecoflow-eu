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

Confirmed via protocol analysis protocol analysis (v0.2.22): Delta 3 uses **MQTT JSON SET** with `"from": "Android"` in the payload.

| Function | Channel | Notes |
|----------|---------|-------|
| Real-time sensor data | MQTT push | `/app/device/property/{sn}` |
| Switch/number control | MQTT JSON SET | `"from":"Android"` required |
| REST API SET | Blocked | EcoFlow blocks D361/D362/D381/R641/R651 (code=1006) |

**SET command payload:** `{id, version:"1.0", sn, moduleType, operateType, from:"Android", params:{...}}`

---

## Supported Entities

### Sensors (82)

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

### Number Controls (13)

| Entity | Range | Default |
|--------|-------|---------|
| AC Charging Speed | 200–1500 W (step 100) | ✅ |
| Max Charge Level | 50–100% (step 5) | ✅ |
| Min Discharge Level | 0–30% (step 5) | ✅ |
| Generator Start SOC | 0–30% (step 5) | off |
| Generator Stop SOC | 50–100% (step 5) | off |
| Battery Protection SOC | 0–100% (step 5) | ✅ |
| Min SOC for AC Auto-On | 0–100% (step 5) | off |
| Device Standby Time | 0–1440 min | ✅ |
| AC Output Standby Time | 0–1440 min | ✅ |
| DC 12V Standby Time | 0–720 min | off |
| LCD Brightness | 0–100% (step 25) | ✅ |
| LCD Timeout | 0–300 s | off |
| Backup Reserve SOC | 0–100% (step 1) | off |

### Select Controls (1)

| Entity | Options | Default |
|--------|---------|---------|
| DC Charge Current | 4 A / 6 A / 8 A | ✅ |

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


### v0.2.22 – Major: MQTT JSON control working for Delta 3 (protocol analysis protocol analysis)

**Breakthrough:** Full protocol analysis protocol analysis of EcoFlow Android app confirmed that:
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
- `Output Memory` switch — `outputMemory` mod=1 (protocol analysis `I()`)
- `Backup Reserve` switch — `watthConfig` mod=1 (protocol analysis `y()`)
- `Backup Reserve SOC` number — `watthConfig` with `bpPowerSoc`
- `Connection Mode` diagnostic sensor — shows `hybrid`/`mqtt_only`/`rest_only`
- `REST_SET_BLOCKED_SN_PREFIXES` — auto-skip REST for D361/D362/D381/R641/R651

**Removed:**
- `UPS Mode` switch — `openUpsFlag` is read-only (protobuf heartbeat only, no SET command)

**Updated (examples/):**
- `test_developer_api.py` / `.ps1` — updated with MQTT JSON SET test (Test 5) and corrected REST SET interpretation for D361

### v0.2.21 – Hybrid Mode: REST API SET commands + language cleanup

**Hybrid Mode (major feature):**
- Added: REST API SET commands via EcoFlow Developer API (`PUT /iot-open/sign/device/quota`) — confirmed working signing for Delta 3
- Added: `set_quota()` method in `api_client.py` — sends HMAC-signed PUT requests with flattened body-param signing
- Added: `_sign_get()` and `_sign_put()` — corrected HMAC signing per EcoFlow spec (GET: auth-only; PUT: flatten body + sort + append auth)
- Added: `_flatten()` helper for dot-notation body parameter signing (`params.enabled=0`)
- Fixed: `import hashlib` missing in `api_client.py` — caused crash when using public API HMAC signing
- Added: `attach_developer_api()` on `EcoFlowPrivateAPI` — enables hybrid mode (MQTT read + REST write)
- Changed: `switch.py` SET priority chain: REST API → protobuf MQTT → JSON MQTT
- Changed: `number.py` SET priority chain: REST API → JSON MQTT
- Changed: `select.py` SET priority chain: REST API → JSON MQTT
- Added: `config_flow.py` — optional Developer API credentials step after App Login (hybrid mode setup)
- Added: Options flow now shows Developer API fields for private mode entries
- Added: `CONF_DEV_ACCESS_KEY`, `CONF_DEV_SECRET_KEY`, `CONF_DEV_API_HOST` in `const.py`
- Added: `developer_creds` step in `strings.json` and `translations/nl.json`

**Language cleanup:**
- Fixed: all Dutch comments, log messages, docstrings and dashboard headings translated to English across `__init__.py`, `switch.py`, `proto_codec.py`, `README.md`, `dashboard_ecoflow_v1.0.yaml`

**Scripts:**
- Changed: `push_to_github.ps1` now prompts interactively for GitHub token via `Read-Host` if `$env:GITHUB_TOKEN` is not set
- Changed: all section comments in `push_to_github.ps1` translated from Dutch to English
- Added: `delete_workflow_runs.ps1` — helper script to remove failed GitHub Actions workflow runs
- Added: `examples/test_developer_api.ps1` — PowerShell credential test (signing validated)
- Added: `examples/test_developer_api.py` — Python credential test with correct signing
- Added: `examples/test_credentials.ps1` — PowerShell multi-server credential diagnostic
- Fixed: `examples/test_credentials.py` — signing corrected (removed params from GET signature)

### v0.2.20 – Fix: manifest.json key order + brand/icon.png + GitHub Actions checkout@v5 + enBeep dataLen=2

- Fixed: `manifest.json` key order corrected to HACS/Hassfest required sequence: `domain → name → codeowners → config_flow → dependencies → documentation → iot_class → issue_tracker → requirements → version`
- Fixed: `brand/icon.png` added at `custom_components/ecoflow_cloud/brand/icon.png` (second required location alongside `brands/icon.png` in repository root)
- Fixed: `validate.yml` — daily cron trigger (`0 0 * * *`) removed to prevent unnecessary failure emails; `actions/checkout@v4` updated to `@v5`
- Fixed: `release.yml` — `actions/checkout@v4` updated to `@v5` (v4 deprecated June 2026)
- Fixed: `build_beep()` in `proto_codec.py` — `enBeep` field now encoded as length-delimited (wire=2) with `dataLen=2` per foxthefox ioBroker.ecoflow-mqtt correction; plain varint encoding was silently rejected by the device

### v0.2.19 – Fix: threading.Timer init delay + Added: proto_codec.py protobuf encoder for Delta 3 SET commands

- Fixed: `time.sleep(5)` in `on_connect` replaced by `threading.Timer(5.0, ...)` — paho MQTT thread no longer blocked during startup delay; confirmed working via post-reboot log
- Added: `proto_codec.py` — pure-Python protobuf encoder for Delta 3 SET commands; no external dependencies; encodes wire format directly
- Added: `build_ac_output(enabled)` — operate_code 3, inner field 2
- Added: `build_xboost(enabled)` — operate_code 3, inner field 1
- Added: `build_dc_output(enabled)` — operate_code 3, inner field 3
- Added: `build_ac_charging(enabled)` — operate_code 3, inner field 5
- Added: `build_beep(enabled)` — operate_code 2, inner field 9
- Added: `build_ups_mode(enabled)` — operate_code 3, inner field 8
- Added: `build_charge_target(soc)` — operate_code 3, inner field 102
- Fixed: `switch.py` — `proto_builder` assigned per switch; JSON fallback retained for switches without known protobuf mapping
- Fixed: `_next_id()` consistent message ID generation used in `select.py` and `number.py`
- Fixed: `INTEGRATION_VERSION` corrected to `"0.2.19"` in `const.py`
- Diagnosis: H-A through H-F refuted, **H-G confirmed** — Delta 3 silently ignores JSON SET commands; protobuf encoding required for all SET operations

**Under investigation (carry-over to v0.2.20):**

- Protobuf SET device response: AC output command dispatched via `proto_codec.py`, broker ACK confirmed (QoS 1), but `set_reply` not yet received — to be verified in next session
- `build_xboost` inner field number (1) to be confirmed via live log toggle
- Remaining switches without `proto_builder`: `solar_charge_priority`, `ac_auto_on`, `ac_always_on`, `bypass` — operate_code unknown, foxthefox schema to be consulted

### v0.2.17 – Fix: moduleType acOutCfg + id overflow + qos + usb_output disabled + client_id recertification

- Fixed: `ac_output` and `x_boost` — `cmd_module` corrected from `MODULE_PD` (1) to `MODULE_MPPT` (5); confirmed via wildcard MQTT trace of APP commands
- Fixed: `KEY_AC_ENABLED` state key corrected from `mppt.cfgAcEnabled` to `pd.acEnabled` (live state, not config register)
- Fixed: `KEY_DC_OUT_STATE` corrected from `pd.carState` to `mppt.dc24vState` — confirmed via latestQuotas dump and incremental MPPT update after toggle
- Fixed: command `id` field changed from epoch milliseconds (41-bit, overflow) to epoch seconds (31-bit, fits 32-bit uint)
- Fixed: `usb_output` switch disabled by default (`entity_registry_enabled_default=False`); `dcOutCfg` returns `ack=0` regardless of state — risk of unintended DC shutdown
- Fixed: MQTT `client_id` on recertification — `_build_client()` factory creates new `mqtt.Client` object; paho does not allow `client_id` mutation after `__init__()`
- Fixed: `set_reply` parser — payload has flat structure; `operateType`/`code` on root level, not nested under `data`
- Fixed: `on_subscribe` logging — `_subscribe_mid` tracked as `dict[int, str]` per call; eliminates race condition on mid matching
- Improved: `acOutCfg` always sends live `xboost` value from coordinator to prevent inconsistent state
- Improved: command publish changed to `qos=1`; broker guarantees delivery acknowledgement
- Improved: `number.py` command `id` also corrected from epoch ms to epoch seconds

### v0.2.16 – Fix: version 1.0 + pvChangePrio + KEY_AC_ENABLED + set_reply diagnostics

- Fixed: `version` field in all set commands changed from `"1.1"` to `"1.0"` (matches device protocol for set operations)
- Fixed: `solar_charge_priority` — `operateType` corrected from `pvChangeSet` to `pvChangePrio`; `cmd_module` corrected from `MODULE_MPPT` (5) to `MODULE_PD` (1)
- Fixed: `KEY_AC_ENABLED` state key corrected from `pd.acEnabled` to `mppt.cfgAcEnabled` (present in ~30s MPPT cycle vs. infrequent INV dump)
- Improved: `set_reply` handler now parses JSON before topic check; logs `operateType` and return `code` at INFO level for direct command diagnosis
- Fixed: `set_reply` crash on malformed payload — wrapped in try/except, raw payload logged on parse error

**Still under investigation:**

- `dcOutCfg` / `usb_output`: broker ACK received but no device reply (ack: 0). Correct params still unknown. To be resolved in v0.2.17 via wildcard MQTT trace.

### v0.2.15 – Fix: payload corrections (acOutCfg/mpptCar/acChgCfg/quietMode) + startup delay

**MQTT payload corrections based on tolwi reference implementation and live log verification:**

- Fixed: `ac_output` and `x_boost` — `cmd_module` changed from `MODULE_PD` (1) to `MODULE_MPPT` (5);
  params `outFreq`/`outVol` replaced with `out_freq: 255` / `out_voltage: -1` (tolwi-compatible)
- Fixed: `dc_output` — `operateType` changed from `dc24vCfg` to `mpptCar`; `cmd_module` changed
  from `MODULE_PD` (1) to `MODULE_MPPT` (5); confirmed working (inv.outputWatts → 0 on AC off)
- Fixed: `ac_charging` — `chgWatts: 255` added to `acChgCfg` params (keep current wattage);
  was missing, causing potential charge power reset
- Fixed: `beep_sound` — `operateType` changed from `beepCfg` to `quietMode`; logic inverted:
  `enabled: 0` = beep on, `enabled: 1` = beep off (quietMode semantics)
- Fixed: `ac_charging_speed` (number) — params changed from `slowChgWatts`/`fastChgWatts`/`chgPauseFlag: 0`
  to `chgWatts`/`chgPauseFlag: 255` (255 = keep current pause state unchanged)
- Fixed: startup state — added 5s delay in `on_connect` before get-all request;
  device returns only timing config immediately after connect; full state dump (PD:58, MPPT:36, INV:28 keys)
  only available after device init cycle (~5s); fixes all switches showing incorrect state after HA restart

**Still under investigation (carry-over from v0.2.14):**

- `dcOutCfg` / `usb_output`: broker ACK received but no device reply (silent reject).
  Correct params still unknown. To be resolved in v0.2.16 via app-toggle + wildcard MQTT trace.


### v0.2.14 – Fix: acOutCfg silent reject (outFreq) + MQTT improvements

**Root cause fixed: HA switch commands silently rejected by device**

- Fixed: `acOutCfg` command parameter `outFreq` changed from enum index `1` to Hz literal `50`
  — the device silently rejected `outFreq=1` without any error or reply; `outFreq=50` is required
- Fixed: command publish QoS changed from `QoS=1` to `QoS=0` (matches EcoFlow app behaviour)
- Fixed: command payload `version` changed from `"1.0"` to `"1.1"` (matches app)
- Fixed: command payload `id` changed from string to integer (matches app)
- Added: `set_reply` and `get_reply` MQTT topic subscriptions — device acknowledgements now visible in log
- Added: `latestQuotas` (Shape F) parsing in `coordinator.py` — full state dump on get_reply
- Added: periodic MQTT recertification every 10 minutes (`__init__.py`)

**State key corrections (verified via live MQTT trace, app toggle):**

- `ac_auto_on`: state key `pd.acAutoOnCfg` → `pd.watchIsConfig`
- `dc_output`: `cmd_module` `MODULE_MPPT` → `MODULE_PD`
- `beep_sound`: `cmd_module` `MODULE_PD` → `MODULE_MPPT`

**Logging improvements:**

- `api_client.py`: WARNING → INFO for setup messages; INFO/DEBUG privacy split (credentials never logged)
- `__init__.py`: `on_publish` ACK callback added; setup logs WARNING → INFO
- `switch.py`, `number.py`, `select.py`: INFO log per command (topic + full payload)

> **Note:** `acOutCfg` (AC Output switch) confirmed working after this fix.  
> `dcOutCfg` (DC Output) and `usb_output` commands still under investigation — broker ACK received but no device reply. To be resolved in v0.2.15.

### v0.2.13 – Fix: entity key alignment

- `switch` key `pv_charge_priority` → `solar_charge_priority` (matches entity ID)
- `switch` name `Bypass` key now consistent (was previously named with Dutch translation)
- `number` key `min_ac_soc` → `min_soc_for_ac_auto_on`
- `number` key `standby_time` → `device_standby_time`
- `number` key `ac_standby_time` → `ac_output_standby_time`
- `number` key `dc12v_standby_time` → `dc_12v_standby_time`

> **Note:** These are internal key renames only. Entity IDs in Home Assistant are unchanged — no cleanup required after upgrade.

### v0.2.12 – New entities + bugfixes + alignment

**New: Select platform**
- Added: `select.py` — new platform for list-based controls
- Added: `dc_charge_current` — DC charge current configurable: 4 A / 6 A / 8 A (`mppt.dcChgCurrent`)
- `__init__.py`: `PLATFORMS` extended with `Platform.SELECT`

**New: Bypass switch**
- Added: `switch.bypass` — enable/disable bypass mode (`pd.acAutoOutPause`, `inverted=True`)

**New: Generator SOC controls (number)**
- Added: `number.generator_start_soc` — generator start SOC 0–30% (`bms_emsStatus.minOpenOilEb`)
- Added: `number.generator_stop_soc` — generator stop SOC 50–100% (`bms_emsStatus.maxCloseOilEb`)

**New: Sensors (+9)**
- Added: `Battery Level (precise)` — float SOC (`bms_bmsStatus.f32ShowSoc`, 2 decimals, off)
- Added: `Max Cell Voltage Difference` — battery balance indicator in mV (`bms_bmsStatus.maxVolDiff`, off)
- Added: `AC Configured Frequency` — configured AC frequency in Hz (`inv.cfgAcOutFreq`, off)
- Added: `DC 12V Port State` — 12V port state sensor (`mppt.carState`, off)
- Added: `System Charge/Discharge State` — EMS charge/discharge state (`bms_emsStatus.sysChgDsgState`, off)
- Added: `Generator Start SOC` sensor (`bms_emsStatus.minOpenOilEb`, off)
- Added: `Generator Stop SOC` sensor (`bms_emsStatus.maxCloseOilEb`, off)
- Added: `MPPT Beep State` sensor (`mppt.beepState`, off)
- Added: `KEY_GEN_MIN_SOC`, `KEY_GEN_MAX_SOC`, `KEY_EMS_SYS_STATE`, `KEY_SOC_FLOAT`, `KEY_MAX_VOL_DIFF`, `KEY_DC12V_STATE`, `KEY_AC_CFG_FREQ`, `KEY_MPPT_BEEP` — new constants in `delta3_1500.py`

**Bugfix: switch state_keys (4× inv → mppt)**
- `KEY_AC_ENABLED`: `inv.cfgAcEnabled` → `mppt.cfgAcEnabled`
- `KEY_AC_XBOOST`: `inv.cfgAcXboost` → `mppt.cfgAcXboost`
- `KEY_AC_CHG_PAUSE`: `inv.chgPauseFlag` → `mppt.chgPauseFlag`
- `KEY_AC_STANDBY_TIME`: `inv.standbyMins` → `mppt.acStandbyMins`

*Reason: `inv.*` keys only appear in the infrequent full status dump (~every 5 min). The `mppt.*` equivalents are consistently present in the ~30s update cycle and provide reliable state.*

**Bugfix: switch command parameters**
- `ac_output`: `outFreq: 255, outVol: 255, xboost: 255` → `outFreq: 1, outVol: 230, xboost: 0`
- `x_boost`: `outFreq: 255, outVol: 255` → `outFreq: 1, outVol: 230`
- `ac_charging`: removed redundant `slowChgWatts: 255, fastChgWatts: 255` — only `chgPauseFlag` is sent

*Reason: value 255 is silently ignored by the device; correct EU values are outFreq=1 (50 Hz), outVol=230.*

**Bugfix: ac_auto_on / ac_always_on commands separated**
- `ac_auto_on`: `cmd_operate` was `acAutoOutConfig` → corrected to `acAutoOnCfg`
- Both switches were sending the same command; each now has its own `operateType` and payload

**Fix: delta3_1500.py alignment**
- All constants rewritten with uniform column alignment: `=` at column 20, `#` at column 55

**number.py**
- `standby_time` and `ac_standby_time` max: `720` → `1440` min (app supports 24h)
- Hardcoded `cmd_module` integers replaced by named constants `MODULE_PD`, `MODULE_BMS`, `MODULE_MPPT`

**Upgrade procedure:** HACS update → full HA restart required.

**Stale entities — remove manually (Settings → Entities → filter ecoflow):**
- `switch.ecoflow_delta_3_1500_x_boost_2` and `switch.ecoflow_delta_3_1500_beep_sound_2` (duplicate registrations from v0.2.11 → v0.2.12 upgrade)

---

### v0.2.11 – Bugfix: entity ID alignment + code cleanup

**Entity ID fixes (switch.py):**
- Fixed: `x_boost` — was `xboost` (entity ID mismatch with HA slug)
- Fixed: `beep_sound` — was `beep` (entity ID mismatch with HA slug)

**Entity ID fix (number.py):**
- Fixed: `dc12v_standby_time` — was `car_standby_time` (removed legacy "car" prefix, consistent with v0.2.9 DC 12V naming)

**Code cleanup:**
- Removed: unused import `KEY_DC12V_STATE` from `switch.py`
- Removed: unused import `KEY_AC_SLOW_CHG_W` from `number.py`
- Fixed: `_LOGGER.warning` → `_LOGGER.debug` for switch and number MQTT commands (was causing log spam in production)

**Dashboard fix:**
- Fixed: `sensor.ecoflow_delta_3_1500_state_of_health` → `state_of_health_bms_status` in `dashboard_ecoflow_v1.0.yaml`

**README fix:**
- Fixed: sensor table entry "Solar Charge Power (PD)" → "Solar Charge Power" (name changed in v0.2.9)

**Upgrade note — manual HA cleanup required:**
After upgrading, remove these stale entity registrations in HA (Settings → Devices & Services → Entities → filter on ecoflow → delete):
- `switch.ecoflow_delta_3_1500_ac_charging_230v` (→ now `ac_charging`)
- `switch.ecoflow_delta_3_1500_ac_auto_on_on_plug_in` (→ now `ac_auto_on`)
- `switch.ecoflow_delta_3_1500_solar_charge_priority` (→ now `pv_charge_priority`)
- `number.ecoflow_delta_3_1500_min_soc_for_ac_auto_on` (→ now `min_ac_soc`)
- `number.ecoflow_delta_3_1500_car_port_standby_time` (→ now `dc12v_standby_time`)
- `sensor.ecoflow_delta_3_1500_solar_charge_power_pd` (→ now `solar_charge_power`)
- `sensor.ecoflow_delta_3_1500_battery_health` (→ now `state_of_health_bms_info`)

### v0.2.10 – Merge: v0.2.9 base + v0.2.8 extras

**Merged from v0.2.8:**
- Added: `RESTART_WARNING.md` — guidance on disabling rate-limited integrations before repeated HA restarts
- Added: `examples/ecoflow_optimal_charging_v1.3.yaml` — smart AC charging automation based on PV surplus (entity IDs updated to v0.2.9 naming)
- Added: `examples/dashboard_ecoflow_v1.0.yaml` — alternative compact dashboard (entity IDs updated to v0.2.9 naming, 33 corrections)
- Added: `examples/test_credentials.py` — EcoFlow API credential diagnostic tool

**Fixes:**
- Fixed: `coordinator.py` MQTT data log level set back to `DEBUG` (was accidentally set to `WARNING` in v0.2.9)

### v0.2.9 – Refactor: full naming overhaul + AC charging speed fix + USB switch fix

**Fixes:**
- Fixed: AC Charging Speed slider now uses `mppt.cfgChgWatts` as `state_key` — shows 200W correctly even when AC cable is unplugged
- Fixed: AC charging command now sends `slowChgWatts` + `fastChgWatts` (was: `chgWatts` — ignored by device)
- Fixed: USB Output switch now uses `MODULE_PD` (moduleType 1) — was MODULE_MPPT (5), device did not respond

**Switch renames:**
- `dc_output` → `usb_output` / "USB Output" (`pd.dcOutState`) — USB-A + USB-C ports
- `dc24v_output` → `dc_output` / "DC Output" (`mppt.dc24vState`) — 12V car port + Anderson connectors
- `AC Charging 230V` → `AC Charging`

**Sensor renames:**
- Car Port Output Power → DC 12V Output Power
- Car Charger Input Power → DC 12V Input Power
- Car Port Temperature → DC 12V Temperature
- DC-DC 12V Power → MPPT DC Converter Power
- DC 24V Temperature → DC Output Temperature
- AC Input Power (Mains) → AC Input Power
- AC Slow/Fast Charge Limit → AC Slow/Fast Charge Watts
- Solar Charge Power (PD) → Solar Charge Power
- DC Input Current/Voltage/Temperature → Inverter DC Input Current/Voltage/Temperature
- Battery Health (BMS) → State of Health (BMS Status)
- Battery Health → State of Health (BMS Info)
- Removed: Wireless Charging Power (not present on Delta 3 1500)

**Number renames:**
- Car Port Standby Time → DC 12V Standby Time
- Standby Time → Device Standby Time
- AC Standby Time → AC Output Standby Time

**Code refactor:**
- All `KEY_CAR_*` constants → `KEY_DC12V_*`
- `KEY_DC_OUT_STATE` → `KEY_USB_OUT_STATE` (`pd.dcOutState`)
- `KEY_DC24V_STATE` → `KEY_DC_OUT_STATE` (`mppt.dc24vState`)
- `KEY_DC24V_TEMP` → `KEY_DC_OUT_TEMP`
- Added: `KEY_MPPT_CFG_CHG_W` = `mppt.cfgChgWatts`

### v0.2.8 – Bugfix: AC Charging Speed slider NameError
- Fixed: `NameError: KEY_AC_IN_W` — import statement corrected in `number.py`

### v0.2.7 – Added: AC Charging Speed slider
- Added: `number.ecoflow_delta_3_1500_ac_charging_speed` — slider 200–1500W (step 100W) to control AC charging limit

### v0.2.6 – Added example dashboard
- Added: `examples/dashboard_delta3_1500.yaml` — complete HA dashboard covering all entities (battery, AC, solar, DC, USB, settings, BMS detail, statistics)

### v0.2.5 – Bugfix: 6 sensor names mismatched with HA entity registry
- Fixed: dashboard YAML corrected to use the descriptive entity IDs generated by the integration — `ac_input_power_mains`, `solar_input_voltage`, `solar_input_current`, `car_port_output_power`, `usb_a_qc_1_power`, `usb_a_qc_2_power`

### v0.2.4 – Bugfix: coordinator crash on bms_kitInfo.watts array
- Fixed: all sensors freezing when device sends `bms_kitInfo.watts` as a JSON array (triggered when AC charging starts) — non-scalar values (lists, dicts) are now filtered before updating coordinator state

### v0.2.3 – Bugfix: force update after HACS install
- Fixed: HA did not prompt for restart after HACS update when version number was unchanged — bumped version so HACS correctly detects the update and requests a restart

### v0.2.2 – Bugfix: duplicate sensor IDs
- Fixed: 7 sensors ignored by Home Assistant due to duplicate unique IDs — BMS/EMS keys in `delta3_1500.py` were incorrectly mapped to MPPT/INV keys already used by other sensors; all now point to correct `bms_bmsStatus.*` / `bms_emsStatus.*` keys (confirmed present in live MQTT dumps)

### v0.2.1 – Bugfix: sensors freezing after ~1 minute
- Fixed: all sensors freezing after ~1 minute — coordinator crashed when device sent `bms_kitInfo` as a JSON array; non-scalar MQTT values are now filtered before merging into coordinator data

### v0.2.0 – Entities cleaned up & push script improved
- Removed: `brands/icon.png` (HA has built-in EcoFlow icon via brands.home-assistant.io)
- Changed: 35 of 75 sensors disabled by default (never or rarely receive data)
- Changed: Push script now automatically removes files from GitHub that no longer exist locally

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

---

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
