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

Start with **App Login**: your normal EcoFlow app email and password, nothing else to set up. It reads everything and adds a few values (cell temperatures, BMS level). Two limits: the AC output switch cannot show its real state, and control over this route is not tested. If you miss either, switch to the **Developer API** (see *When App Login is not enough* below): that is the route tested for both reading and control.

---

## Get started

**1. Credentials.** Use the email and password of your EcoFlow app (App Login). Nothing else is needed to start.

**2. Install via HACS**

[![Open in HACS](https://my.home-assistant.io/badges/hacs_repository.svg)](https://my.home-assistant.io/redirect/hacs_repository/?owner=windsurf&repository=hassio-ecoflow-eu&category=integration)

Or: HACS → three-dot menu → Custom repositories → `https://github.com/windsurf/hassio-ecoflow-eu`, category **Integration**. Download **EcoFlow Cloud** and **restart** Home Assistant (a full restart, not a reload).

**3. Add your device**

[![Add integration](https://my.home-assistant.io/badges/config_flow_start.svg)](https://my.home-assistant.io/redirect/config_flow_start/?domain=ecoflow_cloud)

Settings → Devices & services → Add integration → **EcoFlow Cloud**. Enter the serial number (on the label, or in the app under Device Info) and choose **App Login**, then enter your email and password. The device and its entities appear within a minute. (Auto-detect would pick the Developer API for the Delta 3 Max Plus, so choose App Login yourself for that device. For other devices, Auto-detect picks the right route.)

The Delta 3 Max Plus dashboard **EcoFlow Max Plus** appears in the sidebar by itself. An existing dashboard is left alone; to rebuild it, open the integration's **Configure** and tick *Replace the dashboard with a fresh one*.

A manual copy of the dashboard is in [`dashboard/ecoflow_max_plus.yaml`](dashboard/ecoflow_max_plus.yaml).

### When App Login is not enough

Switch to the **Developer API** if the AC output switch must show its real state, or if control over App Login does not work for your device. It is free but takes a few minutes: sign in at [developer-eu.ecoflow.com](https://developer-eu.ecoflow.com/), choose **Become a Developer**, wait for the approval email, then create an **Access Key** and **Secret Key** under **Security**. Then open the integration's **Configure** and switch the API mode (or add the keys next to App Login; this combination is not tested for the Delta 3 Max Plus).

---

## Supported devices

| Device | Serial prefix | Status |
|---|---|---|
| **Delta 3 Max Plus** | `D3M1` | ✅ Tested by the author: reading and control |
| **Delta 3 1500** | `D361` `P231` | ✅ Tested by the author (earlier versions) |
| Delta 3 Plus · Delta 3 Max | `D362` `P351` · `D381` `D3N1` | 🧪 Profile based on the Delta 3 1500 |
| Delta Pro 3 · Delta Pro Ultra · Delta Pro · Delta Max · Delta Mini · Delta 2 · Delta 2 Max | `DGEA` `MR5` · `Y71` · `DCAB` `DCEB` · `DAAB` `DAEB` · `DAAZ` `DBEB` `DBKB` `DBAB` · `R33` · `R35` | 🧪 Profile available |
| River 3 · River 3 Plus · River 2 · River 2 Max · River 2 Pro · River Max · River Pro · River Mini | `R64` `R65` · `R63` · `R60` · `R61` · `R62` · `R601` · `R602` · `R501` | 🧪 Profile available |
| PowerStream · Smart Plug · Stream AC · Stream AC Pro · Stream Ultra | `HW51` · `HW52` · `BK51` · `BK31` `BK41` · `BK11` `BK12` `BK61` | 🧪 Profile available |
| Glacier · Glacier 55 · Wave 2 · Wave 3 | `BX1` · `RF45` · `KT2` · `AC71` | 🧪 Profile available |
| Smart Home Panel · Smart Home Panel 2 · PowerKit · PowerOcean (3 variants) | `SH10` `SP10` · `SH20` `HD3` · `M10` · `HJ3` `J32` `R37` `HC31` | 🔶 Partly supported, see the [technical reference](README2.md#device-support-v0310) |

A serial prefix tells the integration which device profile to use. The prefixes come from owner reports and from several community projects, listed in [Serial prefix sources](README2.md#serial-prefix-sources); a prefix that is wrong for your device is easy to correct, so please report it. `DGEB` (Smart Generator), `BK01` (Stream Microinverter) and `BK21` (Smart Meter) are recognised by name only and get no entities yet.

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
