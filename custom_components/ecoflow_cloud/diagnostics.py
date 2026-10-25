"""Diagnostics download for EcoFlow Cloud (v0.4.0).

Settings → Devices & services → EcoFlow Cloud → (device or entry) →
Download diagnostics.

Contains everything needed to build or verify a device profile:
  - detected model, auth mode, connection mode, MQTT topics
  - the full coordinator state (every key with its current value)
  - which keys are mapped to an entity and which are not
  - the last MQTT_DIAG_BUFFER_SIZE raw MQTT messages, untruncated
    (JSON as text, binary as hex plus a protobuf field dump)

Credentials are removed and the serial number, user id and MQTT account
are replaced by placeholders everywhere, including inside topics and
payloads, so the file is safe to attach to a GitHub issue.
"""
from __future__ import annotations

import re
import time
from typing import Any

from homeassistant.components.diagnostics import async_redact_data
from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant
from homeassistant.helpers.device_registry import DeviceEntry

from .const import (
    DOMAIN, INTEGRATION_VERSION,
    CONF_ACCESS_KEY, CONF_SECRET_KEY, CONF_DEVICE_SN, CONF_EMAIL, CONF_PASSWORD,
    CONF_DEV_ACCESS_KEY, CONF_DEV_SECRET_KEY,
)
from .proto_codec import dump_fields

TO_REDACT = {
    CONF_ACCESS_KEY, CONF_SECRET_KEY, CONF_DEVICE_SN, CONF_EMAIL, CONF_PASSWORD,
    CONF_DEV_ACCESS_KEY, CONF_DEV_SECRET_KEY,
    "certificatePassword", "certificateAccount", "sn", "email", "password",
}


# v0.4.0: serial numbers (device, battery pack, ...) also travel inside binary protobuf
# payloads as plain ASCII. A run of 10+ uppercase letters/digits is treated as a serial.
_SERIAL_BYTES = re.compile(rb"[A-Z0-9]{10,}")
_SERIAL_TEXT  = re.compile(r"(?<![A-Za-z0-9])[A-Z][A-Z0-9]{11,}(?![A-Za-z0-9])")


def _mask_binary_hex(hex_data: str, secrets: list[str]) -> str:
    """Mask serial numbers inside a hex-encoded binary message.

    Replaced bytes are 0x2a ('*') of identical length, so the message stays a valid
    protobuf for the field dump.
    """
    try:
        raw = bytes.fromhex(hex_data)
    except ValueError:
        return hex_data
    for s in secrets:
        sb = s.encode("utf-8", errors="ignore")
        if len(sb) >= 4:
            raw = raw.replace(sb, b"*" * len(sb))
    raw = _SERIAL_BYTES.sub(lambda m: b"*" * len(m.group()), raw)
    return raw.hex()


def _mask_json_text(text: str) -> str:
    return _SERIAL_TEXT.sub("**SN**", text)


def _scrub(obj: Any, secrets: list[tuple[str, str]]) -> Any:
    """Replace secret substrings in every string, recursively (keys and values)."""
    if isinstance(obj, str):
        for secret, placeholder in secrets:
            obj = obj.replace(secret, placeholder)
        return obj
    if isinstance(obj, dict):
        return {_scrub(k, secrets): _scrub(v, secrets) for k, v in obj.items()}
    if isinstance(obj, (list, tuple)):
        return [_scrub(v, secrets) for v in obj]
    return obj


def _mapped_keys(model: str) -> set[str]:
    """All coordinator keys the platforms use for this model."""
    keys: set[str] = set()
    try:
        from .sensor import SENSOR_DESCRIPTIONS_BY_MODEL
        keys |= {d.key for d in SENSOR_DESCRIPTIONS_BY_MODEL.get(model, ())}
        keys |= {d.fallback_key for d in SENSOR_DESCRIPTIONS_BY_MODEL.get(model, ())
                 if getattr(d, "fallback_key", None)}
    except Exception:  # pragma: no cover — diagnostics must never fail
        pass
    for module, table in (
        ("switch", "SWITCH_DESCRIPTIONS_BY_MODEL"),
        ("number", "NUMBER_DESCRIPTIONS_BY_MODEL"),
        ("select", "SELECT_DESCRIPTIONS_BY_MODEL"),
    ):
        try:
            mod = __import__(f"{__package__}.{module}", fromlist=[table])
            for d in getattr(mod, table).get(model, ()):
                for attr in ("state_key",):
                    val = getattr(d, attr, None)
                    if isinstance(val, str):
                        keys.add(val)
        except Exception:  # pragma: no cover
            pass
    return keys


def _message(rec: dict, secrets: list[str]) -> dict:
    if rec["format"] == "binary":
        data = _mask_binary_hex(rec["data"], secrets)
    else:
        data = _mask_json_text(rec["data"])
    out = {
        "age_s": round(time.time() - rec["ts"], 1),
        "topic": rec["topic"],
        "len": rec["len"],
        "format": rec["format"],
        "data": data,
    }
    if rec["format"] == "binary":
        try:
            out["proto_fields"] = dump_fields(bytes.fromhex(data))
        except Exception as exc:
            out["proto_fields"] = f"dump failed: {exc}"
    return out


async def async_get_config_entry_diagnostics(
    hass: HomeAssistant, entry: ConfigEntry
) -> dict[str, Any]:
    """Return diagnostics for a config entry (one device per entry)."""
    entry_data: dict = hass.data.get(DOMAIN, {}).get(entry.entry_id, {})
    model = entry_data.get("device_model", "?")
    coordinator = entry_data.get("coordinator")
    state: dict = dict(coordinator.data or {}) if coordinator else {}

    mapped = _mapped_keys(model)
    has_mqtt = entry_data.get("mqtt_client") is not None
    has_rest = entry_data.get("rest_api") is not None
    stats = entry_data.get("mqtt_stats", {})

    msg_secrets = [s for s in entry_data.get("redact_strings", []) if s]
    sn_cfg0 = str(entry.data.get(CONF_DEVICE_SN, ""))
    if sn_cfg0:
        msg_secrets.append(sn_cfg0)

    result = {
        "integration_version": INTEGRATION_VERSION,
        "config_entry": async_redact_data(dict(entry.data), TO_REDACT),
        "device": {
            "model": model,
            "sn_prefix": str(entry.data.get(CONF_DEVICE_SN, ""))[:4],
            "auth_mode": entry_data.get("auth_mode"),
            "connection_mode": "hybrid" if has_mqtt and has_rest
                               else "mqtt_only" if has_mqtt else "rest_only",
        },
        "mqtt": {
            "host": entry_data.get("mqtt_host"),
            "topics": entry_data.get("mqtt_topics", {}),
            "stats": {
                "messages": stats.get("messages", 0),
                "json": stats.get("json", 0),
                "binary": stats.get("binary", 0),
                "by_topic": dict(stats.get("by_topic", {})),
            },
        },
        "state": {
            "key_count": len(state),
            "mapped_key_count": len(mapped & state.keys()),
            "unmapped_keys": sorted(state.keys() - mapped),
            "missing_mapped_keys": sorted(mapped - state.keys()),
            "values": {k: state[k] for k in sorted(state)},
        },
        "mqtt_messages": [_message(r, msg_secrets) for r in list(entry_data.get("mqtt_buffer", ()))],
    }

    secrets: list[tuple[str, str]] = []
    for i, s in enumerate(entry_data.get("redact_strings", [])):
        placeholder = "**SN**" if i == 0 else f"**ID{i}**"
        secrets.append((s, placeholder))
    # Also redact the configured SN in case the entry data holds it differently
    sn_cfg = str(entry.data.get(CONF_DEVICE_SN, ""))
    if sn_cfg and all(sn_cfg != s for s, _ in secrets):
        secrets.insert(0, (sn_cfg, "**SN**"))
    # Longest first so a partial match never leaves a fragment behind
    secrets.sort(key=lambda p: len(p[0]), reverse=True)
    return _scrub(result, secrets)


async def async_get_device_diagnostics(
    hass: HomeAssistant, entry: ConfigEntry, device: DeviceEntry
) -> dict[str, Any]:
    """Return diagnostics for the device (same content as the entry)."""
    return await async_get_config_entry_diagnostics(hass, entry)
