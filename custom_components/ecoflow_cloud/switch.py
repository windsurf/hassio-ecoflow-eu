"""Switch platform for EcoFlow Cloud."""
from __future__ import annotations

import json
import logging
from dataclasses import dataclass, field
from typing import Any, Callable, Optional

from homeassistant.components.switch import SwitchEntity, SwitchEntityDescription
from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity import DeviceInfo
from homeassistant.helpers.entity_platform import AddEntitiesCallback
from homeassistant.helpers.update_coordinator import CoordinatorEntity

from .const import DOMAIN, MANUFACTURER
from .coordinator import EcoflowCoordinator
from . import _next_id
from .devices.delta3_1500 import (
    DEVICE_MODEL,
    KEY_AC_ENABLED,
    KEY_AC_XBOOST,
    KEY_USB_OUT_STATE,
    KEY_AC_CHG_PAUSE,
    KEY_BEEP_MODE,
    KEY_PV_CHG_PRIO,
    KEY_AC_AUTO_ON,
    KEY_AC_AUTO_OUT,
    KEY_EMS_UPS_FLAG,
    KEY_DC_OUT_STATE,
    KEY_AC_BYPASS_PAUSE,
    KEY_OUTPUT_MEMORY,
    KEY_BP_POWER_SOC,
)
from .proto_codec import (
    build_ac_output,
    build_xboost,
    build_dc_output,
    build_ac_charging,
    build_beep,
    build_ups_mode,
)

_LOGGER = logging.getLogger(__name__)

# Module type constants (EcoFlow MQTT protocol — JSON fallback only)
MODULE_PD   = 1
MODULE_BMS  = 2
MODULE_INV  = 3
MODULE_MPPT = 5


@dataclass(frozen=True, kw_only=True)
class EcoFlowSwitchDescription(SwitchEntityDescription):
    """Switch description with MQTT command definition."""
    state_key:    str
    cmd_module:   int                        = 0
    cmd_operate:  str                        = ""
    cmd_params:   Any                        = None
    inverted:     bool                       = False
    # v0.2.18: optional protobuf builder — if set, used instead of JSON command
    proto_builder: Optional[Callable[[bool], bytes]] = None
    entity_registry_enabled_default: bool = True


SWITCH_DESCRIPTIONS: tuple[EcoFlowSwitchDescription, ...] = (
    # ── Outputs ──────────────────────────────────────────────────────────
    EcoFlowSwitchDescription(
        key="ac_output",
        name="AC Output",
        icon="mdi:power-socket-eu",
        state_key=KEY_AC_ENABLED,
        cmd_module=MODULE_MPPT,
        cmd_operate="acOutCfg",
        cmd_params=lambda on: {
            "enabled":     1 if on else 0,
            "xboost":      255,   # 255 = keep current xboost state (protocol verified)
            "out_voltage": -1,    # -1 = keep current voltage (protocol verified)
            "out_freq":    255,   # 255 = keep current frequency (protocol verified)
        },
        proto_builder=build_ac_output,
    ),
    EcoFlowSwitchDescription(
        key="x_boost",
        name="X-Boost",
        icon="mdi:lightning-bolt",
        state_key=KEY_AC_XBOOST,
        cmd_module=MODULE_MPPT,
        cmd_operate="acOutCfg",
        cmd_params=lambda on: {
            "enabled":     255,           # 255 = keep current AC output state
            "xboost":      1 if on else 0,
            "out_voltage": 4294967295,    # keep current voltage (protocol verified)
            "out_freq":    255,           # keep current frequency (protocol verified)
        },
        proto_builder=build_xboost,
    ),
    EcoFlowSwitchDescription(
        key="usb_output",
        name="USB Output",
        icon="mdi:usb-port",
        entity_registry_enabled_default=False,  # dcOutCfg returns ack=0 — risk of DC-bus shutdown
        state_key=KEY_USB_OUT_STATE,
        cmd_module=MODULE_PD,
        cmd_operate="dcOutCfg",
        cmd_params=lambda on: {"enabled": 1 if on else 0},  # protocol analysis: N() mod=1
    ),
    EcoFlowSwitchDescription(
        key="dc_output",
        name="DC Output",
        icon="mdi:car-electric",
        state_key=KEY_DC_OUT_STATE,
        cmd_module=MODULE_MPPT,
        cmd_operate="mpptCar",
        cmd_params=lambda on: {"enabled": 1 if on else 0},
        proto_builder=build_dc_output,
    ),

    # ── AC Charging ───────────────────────────────────────────────────────
    EcoFlowSwitchDescription(
        key="ac_charging",
        name="AC Charging",
        icon="mdi:transmission-tower",
        state_key=KEY_AC_CHG_PAUSE,
        inverted=True,
        cmd_module=MODULE_MPPT,
        cmd_operate="acChgCfg",
        cmd_params=lambda on: {
            "chgWatts":     255,   # 255 = keep current charge watts unchanged
            "chgPauseFlag": 0 if on else 1,  # 0=charging enabled, 1=paused
        },
        proto_builder=build_ac_charging,
    ),

    # ── Charging behaviour ────────────────────────────────────────────────
    EcoFlowSwitchDescription(
        key="solar_charge_priority",
        name="Solar Charge Priority",
        icon="mdi:solar-power",
        state_key=KEY_PV_CHG_PRIO,
        cmd_module=MODULE_PD,
        cmd_operate="pvChangePrio",
        cmd_params=lambda on: {"pvChangeSet": 1 if on else 0},  # protocol analysis: J() mod=1
    ),
    EcoFlowSwitchDescription(
        key="ac_auto_on",
        name="AC Auto-On",
        icon="mdi:power-plug-outline",
        state_key=KEY_AC_AUTO_ON,
        cmd_module=MODULE_INV,   # protocol analysis: k(): mod=3 (INV)
        cmd_operate="acAutoOnCfg",
        cmd_params=lambda on: {"enabled": 1 if on else 0},  # protocol analysis: enabled, not acAutoOnCfg
    ),
    EcoFlowSwitchDescription(
        key="ac_always_on",
        name="AC Always-On",
        icon="mdi:power-plug",
        state_key=KEY_AC_AUTO_OUT,
        cmd_module=MODULE_PD,    # protocol analysis: B(): acAutoOutConfig mod=1
        cmd_operate="acAutoOutConfig",
        cmd_params=lambda on: {"acAutoOutConfig": 1 if on else 0, "minAcOutSoc": 0},
    ),
    # ups_mode: openUpsFlag is read-only (protobuf heartbeat only, no SET command in protocol analysis)
    # Removed from switch entities — state visible via sensor if needed.

    # ── System ───────────────────────────────────────────────────────────
    EcoFlowSwitchDescription(
        key="bypass",
        name="Bypass",
        icon="mdi:electric-switch",
        state_key=KEY_AC_BYPASS_PAUSE,
        inverted=True,
        cmd_module=MODULE_PD,    # protocol analysis: v(): bypassBan mod=1
        cmd_operate="bypassBan",
        cmd_params=lambda on: {"banBypassEn": 0 if on else 1},  # protocol verified
    ),
    EcoFlowSwitchDescription(
        key="beep_sound",
        name="Beep Sound",
        icon="mdi:volume-high",
        state_key=KEY_BEEP_MODE,
        cmd_module=MODULE_MPPT,
        cmd_operate="quietMode",
        cmd_params=lambda on: {"enabled": 0 if on else 1},
        proto_builder=build_beep,
    ),

    # ── Memory & Reserve ─────────────────────────────────────────────
    EcoFlowSwitchDescription(
        key="output_memory",
        name="Output Memory",
        icon="mdi:memory",
        state_key=KEY_OUTPUT_MEMORY,
        cmd_module=MODULE_PD,    # protocol analysis: I(): outputMemory mod=1
        cmd_operate="outputMemory",
        cmd_params=lambda on: {"outputMemoryEn": 1 if on else 0},
    ),

    EcoFlowSwitchDescription(
        key="backup_reserve",
        name="Backup Reserve",
        icon="mdi:battery-charging-medium",
        state_key=KEY_BP_POWER_SOC,
        cmd_module=MODULE_PD,    # protocol analysis: y(): watthConfig mod=1
        cmd_operate="watthConfig",
        cmd_params=lambda on: {
            "isConfig":  1 if on else 0,
            "bpPowerSoc": 0,   # SOC via separate number entity
            "minDsgSoc": 0,
            "minChgSoc": 0,
        },
    ),
)


async def async_setup_entry(
    hass: HomeAssistant,
    entry: ConfigEntry,
    async_add_entities: AddEntitiesCallback,
) -> None:
    """Set up EcoFlow switches from a config entry."""
    entry_data  = hass.data[DOMAIN][entry.entry_id]
    coordinator = entry_data["coordinator"]
    sn          = entry_data["sn"]

    async_add_entities(
        EcoFlowSwitchEntity(coordinator, desc, entry_data, sn)
        for desc in SWITCH_DESCRIPTIONS
    )


class EcoFlowSwitchEntity(CoordinatorEntity[EcoflowCoordinator], SwitchEntity):
    """A togglable output on the EcoFlow device."""

    entity_description: EcoFlowSwitchDescription

    def __init__(
        self,
        coordinator: EcoflowCoordinator,
        description: EcoFlowSwitchDescription,
        entry_data: dict,
        sn: str,
    ) -> None:
        super().__init__(coordinator)
        self.entity_description  = description
        self._entry_data         = entry_data
        self._sn                 = sn
        self._attr_unique_id     = f"{sn}_{description.key}"
        self._attr_has_entity_name = True
        self._attr_device_info   = DeviceInfo(
            identifiers={(DOMAIN, sn)},
            name=f"EcoFlow {DEVICE_MODEL}",
            manufacturer=MANUFACTURER,
            model=DEVICE_MODEL,
        )

    @property
    def is_on(self) -> bool | None:
        if not self.coordinator.data:
            return None
        val = self.coordinator.data.get(self.entity_description.state_key)
        if val is None:
            return None
        active = int(val) == 1
        result = (not active) if self.entity_description.inverted else active
        return result

    @property
    def available(self) -> bool:
        return bool(self.coordinator.data)

    def _publish(self, turn_on: bool) -> None:
        desc   = self.entity_description

        # ── Priority 1: REST API SET (Developer API) ─────────────────────
        # Confirmed working for Delta 3 (H-H, 19 March 2026).
        # Reliable, documented, uses HMAC-signed HTTP PUT.
        rest_api = self._entry_data.get("rest_api")
        if rest_api is not None and desc.cmd_operate:
            params = desc.cmd_params(turn_on) if desc.cmd_params else {}
            # acOutCfg: always include live xboost value
            if desc.cmd_operate == "acOutCfg":
                xboost_val = int((self.coordinator.data or {}).get(KEY_AC_XBOOST, 0))
                params["xboost"] = xboost_val
            try:
                rest_api.set_quota(desc.cmd_module, desc.cmd_operate, params)
                _LOGGER.info(
                    "EcoFlow: REST SET %s turn_on=%s module=%d operate=%s params=%s",
                    desc.key, turn_on, desc.cmd_module, desc.cmd_operate, params,
                )
                return
            except Exception as exc:
                _LOGGER.debug(
                    "EcoFlow: REST SET %s failed (%s) — falling back to MQTT",
                    desc.key, exc,
                )

        # ── Priority 2: JSON MQTT SET ─────────────────────────────────────
        # protocol analysis: analysis (28 March 2026): EcoFlow app uses JSON on MQTT /set topic.
        # Topic: /app/{userId}/{sn}/thing/property/set
        # chgPauseFlag=255 means keep current pause state unchanged.
        # H-G (protobuf required) is REVISED — app uses JSON, not protobuf.
        client = self._entry_data.get("mqtt_client")
        topic  = self._entry_data.get("mqtt_topic_set")

        if not client or not topic:
            _LOGGER.error(
                "EcoFlow: no MQTT client and no REST API — cannot send %s command",
                desc.key,
            )
            return

        params = desc.cmd_params(turn_on) if desc.cmd_params else {}

        cmd = {
            "id":          _next_id(),
            "version":     "1.0",
            "sn":          self._sn,
            "moduleType":  desc.cmd_module,
            "operateType": desc.cmd_operate,
            "from":        "Android",
            "params":      params,
        }
        _LOGGER.info(
            "EcoFlow: JSON SET %s turn_on=%s topic=%s params=%s",
            desc.key, turn_on, topic, params,
        )
        result = client.publish(topic, json.dumps(cmd), qos=1)
        _LOGGER.debug(
            "EcoFlow: JSON publish mid=%s rc=%s", result.mid, result.rc,
        )


    async def async_turn_on(self, **kwargs: Any) -> None:
        await self.hass.async_add_executor_job(self._publish, True)

    async def async_turn_off(self, **kwargs: Any) -> None:
        await self.hass.async_add_executor_job(self._publish, False)
