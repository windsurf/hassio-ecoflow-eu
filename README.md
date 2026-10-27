# EcoFlow Cloud – Home Assistant Integration

[![HACS Custom](https://img.shields.io/badge/HACS-Custom-orange.svg)](https://github.com/hacs/integration) [![GitHub Release](https://img.shields.io/github/release/windsurf/hassio-ecoflow-eu.svg)](https://github.com/windsurf/hassio-ecoflow-eu/releases) [![Validate](https://github.com/windsurf/hassio-ecoflow-eu/actions/workflows/validate.yml/badge.svg)](https://github.com/windsurf/hassio-ecoflow-eu/actions/workflows/validate.yml)

**Your EcoFlow power station in Home Assistant, in three steps.** Install it from HACS, add your device with its serial number, and the sensors, switches and sliders appear. For the **Delta 3 Max Plus** the integration also builds a dashboard for you.

> Not affiliated with or endorsed by EcoFlow. Provided as is, without warranty. Use at your own risk.

---

## Delta 3 Max Plus

The Delta 3 Max Plus (serial number starts with `D3M1`) has its own profile, written for use as a reserve battery for always-on equipment such as laptops:

- **See** the battery level, the power going in and out, whether it is charging or discharging, the time to full and the remaining run time, plus every power flow: AC in, solar 1 and 2, 12 V and the USB ports.
- **Control** the AC output, Energy Backup mode, the charge limit, the discharge limit and the Energy Backup reserve — from Home Assistant, an automation or the dashboard.
- **Dashboard**, created for you: an Overview with gauges, switches and sliders, and a History view with charts of the last 30 minutes, 4 hours and 24 hours (needs [ApexCharts Card](https://my.home-assistant.io/redirect/hacs_repository/?owner=RomRider&repository=apexcharts-card&category=plugin) from HACS).
- **Diagnostics download** with the last raw messages of the device, serial numbers masked, for a bug report.

Use the **Developer API** for the Delta 3 Max Plus: it is the route tested for both reading and control. The App Login route also works for reading and adds a few values (cell temperatures, BMS level); control over it is not tested.

---

## Get started

**1. Get your credentials.** Developer API: sign in at [developer-eu.ecoflow.com](https://developer-eu.ecoflow.com/), choose **Become a Developer**, wait for the approval email, then create an **Access Key** and **Secret Key** under **Security**.

**2. Install via HACS**

[![Open in HACS](https://my.home-assistant.io/badges/hacs_repository.svg)](https://my.home-assistant.io/redirect/hacs_repository/?owner=windsurf&repository=hassio-ecoflow-eu&category=integration)

Or: HACS → three-dot menu → Custom repositories → `https://github.com/windsurf/hassio-ecoflow-eu`, category **Integration**. Download **EcoFlow Cloud** and **restart** Home Assistant (a full restart, not a reload).

**3. Add your device**

[![Add integration](https://my.home-assistant.io/badges/config_flow_start.svg)](https://my.home-assistant.io/redirect/config_flow_start/?domain=ecoflow_cloud)

Settings → Devices & services → Add integration → **EcoFlow Cloud**. Enter the serial number (on the label, or in the app under Device Info), keep **Auto-detect**, then enter your Access Key and Secret Key. The device and its entities appear within a minute.

The Delta 3 Max Plus dashboard **EcoFlow Max Plus** appears in the sidebar by itself. An existing dashboard is left alone; to rebuild it, open the integration's **Configure** and tick *Replace the dashboard with a fresh one*.

A manual copy of the dashboard is in [`dashboard/ecoflow_max_plus.yaml`](dashboard/ecoflow_max_plus.yaml).

---

## Supported devices

| Device | Serial prefix | Status |
|---|---|---|
| **Delta 3 Max Plus** | `D3M1` | ✅ Tested by the author: reading and control |
| **Delta 3 1500** | `D361` | ✅ Tested by the author (earlier versions) |
| Delta 3 Plus · Delta 3 Max | `D362` · `D381` | 🧪 Profile based on the Delta 3 1500 |
| Delta Pro 3 · Delta Pro Ultra · Delta Pro · Delta Max · Delta Mini · Delta 2 · Delta 2 Max | `DGEA` · `DGEB` · `DAEB` · `DCAB` · `DAAZ` `DBEB` `DBKB` · `R331` · `R351` | 🧪 Profile available |
| River 3 · River 3 Plus · River 2 · River 2 Max · River 2 Pro · River Max · River Pro · River Mini | `R641` `R655` · `R651` `R631` · `R621` · `R611` · `R622` · `R601` · `R602` · `R501` | 🧪 Profile available |
| PowerStream · Smart Plug · Stream AC · Stream AC Pro · Stream Ultra | `HW51` `HW52` `BKW` · `SP10` · `BK` · `BK31` · `BK11` | 🧪 Profile available |
| Glacier · Glacier 55 · Wave 2 · Wave 3 | `BX11` · `BX55` · `KT21` · `KT3` | 🧪 Profile available |
| Smart Home Panel · Smart Home Panel 2 · PowerKit · PowerOcean (3 variants) | `SH10` · `SH20` · `M106` · `PO11` `PO31` `POFI` | 🔶 Partly supported, see the [technical reference](README2.md#device-support-v0310) |

**🙋 Own a device marked 🧪 or 🔶? You are exactly who this project needs.** Install it, and whether something looks off or it all just works, open a [New model report](https://github.com/windsurf/hassio-ecoflow-eu/issues/new?template=new_model.yml) with the diagnostics download attached (Settings → Devices & services → EcoFlow Cloud → your device → Download diagnostics). One report is enough to move a device from 🧪 to ✅.

---

## Good to know

- **Full restart after an update.** A reload of the integration does not clear Python's cache and may run the old code.
- **Entities marked off are disabled by default** (for instance the USB ports of the Delta 3 Max Plus). Enable them under Settings → Devices & services → your device.
- **Diagnostics and logs.** The diagnostics download masks serial numbers. Check a log excerpt for your serial number before you attach it to a public issue.

Everything else — how the connection works, every entity per device, debug logging, the changelog — is in the [technical reference](README2.md).

---

## Disclaimer

This software is **not affiliated with or endorsed by EcoFlow**. The EcoFlow name, logo and product names are trademarks of EcoFlow Inc. The App Login route uses undocumented private APIs that EcoFlow may change at any time. Provided **"as is"** without warranty; the authors accept no liability for damage, loss of data or service disruption.

Released under the [Apache License 2.0](LICENSE). See [NOTICE](NOTICE) for attribution.
