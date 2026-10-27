"""The EcoFlow Max Plus dashboard: created on request, never overwritten (v0.4.1).

Two views for the Delta 3 Max Plus:

  Overview  - battery level, power in and out, charge state, the switches and
              the three limits, the main power flows.
  History   - three charts (apexcharts-card from HACS): the last 30 minutes,
              4 hours and 24 hours of power out (above zero), power in (below
              zero) and battery level, in the style of the Zendure RestAPI view.
              Without apexcharts-card a notice takes the place of the charts.

The cards are built in this module from "slots": a slot is one entity of the
device, found in the entity registry through its unique id (`<sn>_<key>`), so
renamed devices and entity ids with a `_2` suffix do not matter. A slot whose
entity does not exist or is disabled (the USB ports, the BMS values of the App
Login route) leaves its card out.

The same builder, run with the default entity ids, produces the hand-made
copy in dashboard/ecoflow_max_plus.yaml (see README2).

Home Assistant has no public call for an integration to add a dashboard. The
dashboards collection is reached through the handler of the websocket command
the frontend itself uses to create one. If that route is not there, the user
gets a notification with the manual route and nothing else changes; setting
up the device never depends on it.
"""
from __future__ import annotations

import inspect
import logging
from typing import Any

from homeassistant.components import persistent_notification
from homeassistant.core import HomeAssistant
from homeassistant.helpers import entity_registry as er

from .const import DOMAIN

_LOGGER = logging.getLogger(__name__)

DASHBOARD_URL   = "ecoflow-max-plus"
DASHBOARD_TITLE = "EcoFlow Max Plus"
DASHBOARD_ICON  = "mdi:power-plug-battery"
NOTIFICATION_ID = "ecoflow_cloud_dashboard"
YAML_URL = (
    "https://github.com/windsurf/hassio-ecoflow-eu/blob/main/dashboard/ecoflow_max_plus.yaml"
)
DEVICE_NAME = "ecoflow_delta_3_max_plus"      # entity id prefix of the default device name

# Gauge ceilings (W). Edit the dashboard if your unit differs.
GAUGE_MAX_IN_W  = 3000
GAUGE_MAX_OUT_W = 3000

CREATED  = "created"
REPLACED = "replaced"
EXISTS   = "exists"
FAILED   = "failed"

# slot -> (domain, unique id suffix, entity name, enabled by default)
# Sensors use the data key, switches and numbers the description key.
SLOTS: dict[str, tuple[str, str, str, bool]] = {
    "soc":        ("sensor", "cmsBattSoc",         "Battery Level",          True),
    "in_w":       ("sensor", "powInSumW",          "Total Input Power",      True),
    "out_w":      ("sensor", "powOutSumW",         "Total Output Power",     True),
    "state":      ("sensor", "cmsChgDsgState",     "Charge State",           True),
    "to_full":    ("sensor", "cmsChgRemTime",      "Time To Full",           True),
    "run_time":   ("sensor", "cmsDsgRemTime",      "Remaining Run Time",     True),
    "ac_in":      ("sensor", "powGetAcIn",         "AC Input Power",         True),
    "pv1":        ("sensor", "powGetPv",           "Solar Input Power",      True),
    "pv2":        ("sensor", "powGetPv2",          "Solar 2 Input Power",    True),
    "dc12":       ("sensor", "powGet12v",          "DC 12V Output Power",    True),
    "usba1":      ("sensor", "powGetQcusb1",       "USB-A 1 Output Power",   False),
    "usba2":      ("sensor", "powGetQcusb2",       "USB-A 2 Output Power",   False),
    "usbc1":      ("sensor", "powGetTypec1",       "USB-C 1 Output Power",   False),
    "usbc2":      ("sensor", "powGetTypec2",       "USB-C 2 Output Power",   False),
    "usbc3":      ("sensor", "powGetTypec3",       "USB-C 3 Output Power",   False),
    "bms_soc":    ("sensor", "bmsBattSoc",         "BMS Battery Level",      False),
    "dcp":        ("sensor", "powGetDcp",          "DCP Input Power",        False),
    "temp_max":   ("sensor", "bmsMaxCellTemp",     "Max Cell Temperature",   False),
    "temp_min":   ("sensor", "bmsMinCellTemp",     "Min Cell Temperature",   False),
    "ac_max_chg": ("sensor", "plugInInfoAcInChgPowMax", "AC Max Charging Power", False),
    "ac_out":     ("switch", "d3mp_ac_out",        "AC Output",              True),
    "backup":     ("switch", "d3mp_energy_backup", "Energy Backup",          True),
    "ac2_out":    ("switch", "d3mp_ac2_out",       "AC Output 2",            True),
    "dc12_out":   ("switch", "d3mp_dc12v_out",     "DC 12V Output",          True),
    "beep":       ("switch", "d3mp_beep",          "Beep Sound",             False),
    "xboost":     ("switch", "d3mp_xboost",        "X-Boost",                False),
    "bypass":     ("switch", "d3mp_bypass_disable", "Bypass Output Disabled", False),
    "chg_limit":  ("number", "d3mp_max_chg_soc",   "Charge Limit",           True),
    "dsg_limit":  ("number", "d3mp_min_dsg_soc",   "Discharge Limit",        True),
    "reserve":    ("number", "d3mp_backup_reserve", "Energy Backup Reserve", True),
}

IDS = dict[str, str | None]   # slot -> entity id (None: not available)


def _slug(name: str) -> str:
    return name.lower().replace(" ", "_").replace("-", "_")


def default_ids() -> IDS:
    """The entity ids Home Assistant gives a freshly added device (for the yaml copy)."""
    return {
        slot: f"{domain}.{DEVICE_NAME}_{_slug(name)}"
        for slot, (domain, _key, name, enabled) in SLOTS.items()
        if enabled
    }


def resolve_ids(hass: HomeAssistant, sn: str) -> IDS:
    """Slot -> entity id from the entity registry; disabled entities are left out."""
    registry = er.async_get(hass)
    ids: IDS = {}
    for slot, (domain, key, _name, _enabled) in SLOTS.items():
        entity_id = registry.async_get_entity_id(domain, DOMAIN, f"{sn}_{key}")
        entry = registry.async_get(entity_id) if entity_id else None
        ids[slot] = entity_id if entry is not None and entry.disabled_by is None else None
    return ids


# ── Card builders ───────────────────────────────────────────────────────────

def _tile(ids: IDS, slot: str, icon: str | None = None, *, slider: bool = False,
          name: str | None = None, state_content: str | list[str] | None = None,
          horizontal: bool = False) -> dict | None:
    entity = ids.get(slot)
    if not entity:
        return None
    card: dict[str, Any] = {"type": "tile", "entity": entity}
    if icon:
        card["icon"] = icon
    if name:
        card["name"] = name
    if state_content:
        card["state_content"] = state_content
    if slider:
        card["features"] = [{"type": "numeric-input", "style": "slider"}]
        card["features_position"] = "bottom"
    if slider or horizontal:
        card["vertical"] = False
    return card


def _gauge(ids: IDS, slot: str, minimum: float, maximum: float, severity: dict) -> dict | None:
    entity = ids.get(slot)
    if not entity:
        return None
    return {
        "type": "gauge", "entity": entity, "min": minimum, "max": maximum,
        "needle": True, "severity": severity,
        "grid_options": {"columns": 6, "rows": "auto"},
    }


def _heading(title: str, icon: str, badges: list[dict] | None = None) -> dict:
    card: dict[str, Any] = {
        "type": "heading", "heading": title, "heading_style": "title", "icon": icon,
    }
    if badges:
        card["badges"] = badges
    return card


def _badge(ids: IDS, slot: str) -> dict | None:
    entity = ids.get(slot)
    return {"type": "entity", "entity": entity} if entity else None


def _section(span: int, *cards: dict | None) -> dict | None:
    kept = [c for c in cards if c]
    # A section with nothing but its heading is not worth showing.
    if not any(c.get("type") != "heading" for c in kept):
        return None
    return {"type": "grid", "column_span": span, "cards": kept}


# Look of the charts follows the Zendure RestAPI history view: output above the
# zero line, input (charging) below it, battery level dashed on its own axis.
COLOR_IN, COLOR_OUT, COLOR_SOC = "#E53935", "#4CAF50", "#9575CD"

# Soft bounds ("~"): the axis always shows zero and grows with the data, so a
# small load gives a small scale instead of a fixed +/-3000 W.
_POWER_AXIS = {
    "id": "power", "min": "~0", "max": "~0", "decimals": 0, "align_to": 100,
}
_SOC_AXIS = {
    "id": "soc", "opposite": True, "min": 0, "max": 100, "decimals": 0,
    "apex_config": {"tickAmount": 4, "labels": {"style": {"fontSize": "10px"}}},
}


def _series(ids: IDS, slot: str, name: str, color: str, axis: str, *, invert: bool = False,
            line: bool = False, curve: str, stats: bool, group: str | None) -> dict | None:
    entity = ids.get(slot)
    if not entity:
        return None
    s: dict[str, Any] = {
        "entity": entity, "name": name, "color": color, "yaxis_id": axis,
        "type": "line" if line else "area", "curve": curve, "float_precision": 0,
        "extend_to": "now", "show": {"in_header": False, "legend_value": False},
    }
    if line:
        s["stroke_width"] = 2
        s["stroke_dash"] = 4
    else:
        s["opacity"] = 0.3
        s["stroke_width"] = 1
    if invert:
        s["transform"] = "return x * -1;"
    if stats:
        s["statistics"] = {"type": "mean", "period": "5minute", "align": "middle"}
    elif group:
        s["group_by"] = {"func": "avg", "duration": group, "fill": "last"}
    return s


def _chart(ids: IDS, span: str, group: str | None, *, stats: bool, curve: str,
           update: str | None, tooltip: str) -> dict | None:
    kw = {"curve": curve, "stats": stats, "group": group}
    series = [
        _series(ids, "out_w", "Output", COLOR_OUT, "power", **kw),
        _series(ids, "in_w", "Input", COLOR_IN, "power", invert=True, **kw),
        _series(ids, "soc", "Battery level", COLOR_SOC, "soc", line=True, **kw),
    ]
    series = [x for x in series if x]
    if not series:
        return None
    card: dict[str, Any] = {
        "type": "custom:apexcharts-card",
        "header": {"show": False},
        "graph_span": span,
    }
    if span != "24h":
        card["now"] = {"show": True}
    if update:
        card["update_interval"] = update
    card.update({
        "yaxis": [_POWER_AXIS, _SOC_AXIS],
        "apex_config": {
            "chart": {"height": 240},
            "legend": {"show": True},
            "tooltip": {"x": {"format": tooltip}},
            "grid": {"borderColor": "rgba(127, 127, 127, 0.25)", "strokeDashArray": 0},
            "fill": {"type": "solid"},
        },
        "series": series,
        "grid_options": {"columns": "full", "rows": "auto"},
        "hours_12": False,
    })
    return card


def build_config(ids: IDS, custom_cards: set[str] | None = None) -> dict[str, Any]:
    """The dashboard for the slots in `ids`. `custom_cards` holds the installed
    custom card types; None assumes apexcharts-card is installed (yaml copy)."""
    soc, in_w, out_w = ids.get("soc"), ids.get("in_w"), ids.get("out_w")

    header = _section(
        4,
        _heading(
            "EcoFlow Delta 3 Max Plus", "mdi:power-plug-battery",
            [b for b in (_badge(ids, "soc"), _badge(ids, "state"), _badge(ids, "ac_out")) if b],
        ),
        _tile(ids, "soc", "mdi:battery-charging"),
        _tile(ids, "state", "mdi:battery-sync"),
        _tile(ids, "in_w", "mdi:transmission-tower-import"),
        _tile(ids, "out_w", "mdi:transmission-tower-export"),
        _tile(ids, "to_full", "mdi:battery-clock"),
        _tile(ids, "run_time", "mdi:timer-sand"),
    )
    gauges = _section(
        2,
        _heading("Overview", "mdi:gauge"),
        _gauge(ids, "soc", 0, 100, {"green": 70, "yellow": 30, "red": 0}),
        _gauge(ids, "in_w", 0, GAUGE_MAX_IN_W, {"green": 0, "yellow": 1000, "red": 2000}),
        _gauge(ids, "out_w", 0, GAUGE_MAX_OUT_W, {"green": 0, "yellow": 1500, "red": 2500}),
    )
    controls = _section(
        2,
        _heading("Control", "mdi:tune"),
        _tile(ids, "ac_out", "mdi:power-socket-eu", horizontal=True),
        _tile(ids, "ac2_out", "mdi:power-socket-eu", horizontal=True),
        _tile(ids, "dc12_out", "mdi:power-socket-eu", horizontal=True),
        _tile(ids, "backup", "mdi:battery-heart"),
        _tile(ids, "chg_limit", "mdi:battery-charging-high", slider=True),
        _tile(ids, "dsg_limit", "mdi:battery-charging-low", slider=True),
        _tile(ids, "reserve", "mdi:battery-heart-outline", slider=True),
    )
    flows = _section(
        4,
        _heading("Power flow", "mdi:flash"),
        _tile(ids, "ac_in", "mdi:flash"),
        _tile(ids, "pv1", "mdi:solar-power"),
        _tile(ids, "pv2", "mdi:solar-power"),
        _tile(ids, "dc12", "mdi:car-battery"),
    )
    overview = {
        "title": "Overview", "path": "overview", "type": "sections", "max_columns": 4,
        "sections": [s for s in (header, gauges, controls, flows) if s],
    }

    charts: list[tuple[str, str, dict | None]] = [
        ("Last 30 minutes", "mdi:pulse",
         _chart(ids, "30min", "10s", stats=False, curve="straight", update="10s", tooltip="HH:mm:ss")),
        ("Last 4 hours", "mdi:clock-outline",
         _chart(ids, "4h", "10s", stats=False, curve="straight", update="1min", tooltip="HH:mm")),
        ("Last 24 hours", "mdi:history",
         _chart(ids, "24h", None, stats=True, curve="monotoneCubic", update=None, tooltip="dd-MM HH:mm")),
    ]
    have_apex = custom_cards is None or "custom:apexcharts-card" in custom_cards
    sections: list[dict] = []
    if have_apex:
        for title, icon, chart in charts:
            if chart:
                sections.append({
                    "type": "grid", "column_span": 4,
                    "cards": [_heading(title, icon), chart],
                })
    elif any(c for _t, _i, c in charts):
        sections.append({"type": "grid", "column_span": 4, "cards": [{
            "type": "markdown",
            "content": (
                "The charts on this tab need **ApexCharts Card** from HACS. Install it, "
                "refresh the browser, then open the integration's **Configure** and tick "
                "*Replace the dashboard with a fresh one*."
            ),
            "grid_options": {"columns": "full"},
        }]})
    history = {
        "title": "History", "path": "history", "type": "sections", "max_columns": 4,
        "sections": sections,
    }
    views = [overview] + ([history] if history["sections"] and (soc or in_w or out_w) else [])
    return {"title": DASHBOARD_TITLE, "views": views}


# ── Creating the dashboard in Home Assistant ───────────────────────────────

CUSTOM_CARDS = {"apexcharts-card": "custom:apexcharts-card"}


async def _custom_cards(hass: HomeAssistant) -> set[str]:
    """The custom cards from CUSTOM_CARDS that are installed as resources."""
    resources = getattr(hass.data.get("lovelace"), "resources", None)
    if resources is None:
        return set()
    try:
        await resources.async_get_info()
        urls = [str(item.get("url", "")) for item in resources.async_items()]
    except Exception:  # noqa: BLE001 - no resources means no custom cards
        return set()
    return {card for name, card in CUSTOM_CARDS.items() if any(name in url for url in urls)}


def _collection(hass: HomeAssistant) -> Any:
    """The live dashboards collection, through the frontend's create command."""
    handlers = hass.data.get("websocket_api") or {}
    entry = handlers.get("lovelace/dashboards/create")
    if not entry:
        return None
    handler = inspect.unwrap(entry[0])
    owner = getattr(handler, "__self__", None)
    return getattr(owner, "storage_collection", None)


def _dashboards(hass: HomeAssistant) -> dict[str, Any] | None:
    data = hass.data.get("lovelace")
    dashboards = getattr(data, "dashboards", None)
    if dashboards is None and isinstance(data, dict):
        dashboards = data.get("dashboards")
    return dashboards


async def async_create_dashboard(hass: HomeAssistant, sn: str, *, replace: bool = False) -> str:
    """Create the dashboard unless one exists at its address.

    With `replace`, an existing one gets a fresh configuration instead: the user
    asked for it in the options, which say that their edits are lost.
    """
    try:
        dashboards = _dashboards(hass)
        if dashboards is None:
            return FAILED
        existing = dashboards.get(DASHBOARD_URL)
        if existing is not None and not replace:
            return EXISTS
        collection = None if existing is not None else _collection(hass)
        if existing is None and collection is None:
            return FAILED
        config = build_config(resolve_ids(hass, sn), await _custom_cards(hass))
        if not config["views"] or not config["views"][0]["sections"]:
            return FAILED
        if existing is not None:
            await existing.async_save(config)
            return REPLACED
        await collection.async_create_item(
            {
                "url_path": DASHBOARD_URL,
                "title": DASHBOARD_TITLE,
                "icon": DASHBOARD_ICON,
                "show_in_sidebar": True,
                "require_admin": False,
                "mode": "storage",
            }
        )
        store = dashboards.get(DASHBOARD_URL)
        if store is None:
            return FAILED
        await store.async_save(config)
    except Exception:  # noqa: BLE001 - never let the dashboard break the setup
        _LOGGER.warning("Could not create the EcoFlow Max Plus dashboard", exc_info=True)
        return FAILED
    return CREATED


def notify(hass: HomeAssistant, result: str) -> None:
    """Tell the user what happened, in one notification."""
    if result == CREATED:
        message = (
            f"The dashboard **{DASHBOARD_TITLE}** is in the sidebar. It is an ordinary "
            "dashboard: edit it as you like; the integration will not touch it again. "
            "The charts on the History tab need ApexCharts Card from HACS."
        )
    elif result == REPLACED:
        message = (
            f"The dashboard **{DASHBOARD_TITLE}** was replaced by a fresh one. "
            "Refresh the browser to see it."
        )
    elif result == EXISTS:
        message = (
            f"A dashboard at `/{DASHBOARD_URL}` already exists and was left as it is. "
            "To rebuild it, tick *Replace the dashboard with a fresh one* in the "
            "integration's Configure."
        )
    else:
        message = (
            "The dashboard could not be created automatically. Add it by hand: create a "
            f"dashboard, paste [dashboard/ecoflow_max_plus.yaml]({YAML_URL}) into its raw "
            "configuration editor and replace `ecoflow_delta_3_max_plus_` in the entity ids "
            "with the prefix of your device (Developer tools → States)."
        )
    persistent_notification.async_create(
        hass, message, title=DASHBOARD_TITLE, notification_id=NOTIFICATION_ID
    )
