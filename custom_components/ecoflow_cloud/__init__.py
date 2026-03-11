"""EcoFlow Cloud – Home Assistant integration entry point."""
from __future__ import annotations

import asyncio
import json
import logging
import ssl
import time
from typing import Any

import paho.mqtt.client as mqtt

from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant
from homeassistant.const import Platform

from .const import (
    DOMAIN, CONF_ACCESS_KEY, CONF_SECRET_KEY, CONF_DEVICE_SN, CONF_API_HOST,
    CONF_AUTH_MODE, CONF_EMAIL, CONF_PASSWORD,
    AUTH_MODE_PRIVATE,
    API_HOST_DEFAULT, MQTT_KEEPALIVE, MQTT_RECONNECT_INTERVAL,
)
from .api_client import EcoFlowAPI, EcoFlowPrivateAPI, EcoFlowAPIError
from .coordinator import EcoflowCoordinator

_LOGGER = logging.getLogger(__name__)
PLATFORMS = [Platform.SENSOR, Platform.SWITCH, Platform.NUMBER, Platform.SELECT]


async def async_setup_entry(hass: HomeAssistant, entry: ConfigEntry) -> bool:
    data       = entry.data
    access_key = data.get(CONF_ACCESS_KEY, "")
    secret_key = data.get(CONF_SECRET_KEY, "")
    sn         = data[CONF_DEVICE_SN]
    auth_mode  = data.get(CONF_AUTH_MODE, "public")
    api_host   = data.get(CONF_API_HOST, API_HOST_DEFAULT)

    _LOGGER.info("EcoFlow: setting up %s mode=%s host=%s", sn, auth_mode, api_host)

    if auth_mode == AUTH_MODE_PRIVATE:
        email    = data.get(CONF_EMAIL, "")
        password = data.get(CONF_PASSWORD, "")
        api      = EcoFlowPrivateAPI(email, password, sn)
    else:
        api = EcoFlowAPI(access_key, secret_key, sn, api_host)
    coordinator = EcoflowCoordinator(hass, api)

    # ── MQTT credentials ──────────────────────────────────────────────────
    try:
        mqtt_info = await hass.async_add_executor_job(api.get_mqtt_credentials)
    except EcoFlowAPIError as exc:
        _LOGGER.error("EcoFlow: cannot get MQTT credentials: %s", exc)
        return False

    if not mqtt_info:
        _LOGGER.error("EcoFlow: empty MQTT credentials response")
        return False

    _LOGGER.info("EcoFlow: MQTT credentials OK: %s", {
        k: v for k, v in mqtt_info.items() if k != "certificatePassword"
    })

    # ── REST quota snapshot (optional, non-fatal) ─────────────────────────
    try:
        initial = await hass.async_add_executor_job(api.get_all_quota)
        if initial:
            coordinator.async_set_updated_data(initial)
            _LOGGER.warning("EcoFlow: REST initial data OK: %d keys", len(initial))
        elif api.rest_quota_unavailable:
            coordinator.disable_rest_polling()
        else:
            _LOGGER.info("EcoFlow: REST initial data empty — waiting for MQTT push")
    except Exception as exc:
        _LOGGER.warning("EcoFlow: REST initial data failed (non-fatal): %s", exc)

    # ── Store objects ─────────────────────────────────────────────────────
    hass.data.setdefault(DOMAIN, {})
    hass.data[DOMAIN][entry.entry_id] = {
        "api": api, "coordinator": coordinator, "sn": sn,
    }

    # ── MQTT topics ───────────────────────────────────────────────────────
    mqtt_host = mqtt_info.get("url", "mqtt.ecoflow.com")
    mqtt_port = int(mqtt_info.get("port", 8883))

    is_private = mqtt_info.get("_private_api", False)
    user_id    = mqtt_info.get("_user_id", "")
    if is_private:
        topic_sub       = f"/app/device/property/{sn}"
        topic_get       = f"/app/{user_id}/{sn}/thing/property/get"
        topic_set       = f"/app/{user_id}/{sn}/thing/property/set"
        topic_set_reply = f"/app/{user_id}/{sn}/thing/property/set_reply"
        topic_get_reply = f"/app/{user_id}/{sn}/thing/property/get_reply"
    else:
        topic_sub       = f"/open/{mqtt_info.get('certificateAccount', '')}/{sn}/quota"
        topic_get       = f"/open/{mqtt_info.get('certificateAccount', '')}/{sn}/quota/get"
        topic_set       = f"/open/{mqtt_info.get('certificateAccount', '')}/{sn}/set"
        topic_set_reply = None
        topic_get_reply = None

    _LOGGER.info(
        "EcoFlow: MQTT host=%s port=%d topic_sub=%s",
        mqtt_host, mqtt_port, topic_sub
    )

    # ── Client factory ────────────────────────────────────────────────────
    # v0.2.18: extracted as inner function so recertification can create a
    # fresh Client with the new client_id returned by the API.
    # The EcoFlow broker routes set-commands only to the session whose
    # client_id matches the most recently issued certificate. Reusing an
    # old client_id after recertification causes silent command drops.

    # Track mid→topic per client so on_subscribe logs the correct topic.
    _subscribe_mid: dict[int, str] = {}

    def _request_full_state(c: mqtt.Client) -> None:
        """Send a get-all-properties request to the device."""
        payload = json.dumps({
            "id":      int(time.time() * 1000),
            "version": "1.1",
            "sn":      sn,
            "params":  {},
        })
        result = c.publish(topic_get, payload, qos=0)
        _LOGGER.debug(
            "EcoFlow: MQTT get-all published → %s (mid=%s rc=%s)",
            topic_get, result.mid, result.rc
        )

    def on_connect(c, userdata, flags, rc):
        if rc == 0:
            _LOGGER.info("EcoFlow: MQTT connected OK for %s", sn)
            r = c.subscribe(topic_sub, qos=1)
            _subscribe_mid[r[1]] = topic_sub
            if topic_set_reply:
                r = c.subscribe(topic_set_reply, qos=1)
                _subscribe_mid[r[1]] = topic_set_reply
            if topic_get_reply:
                r = c.subscribe(topic_get_reply, qos=1)
                _subscribe_mid[r[1]] = topic_get_reply
            # Delay 5s: device sends only timing config immediately after connect.
            # Full state dump (58+ keys) returned only after device init cycle completes.
            # Confirmed by log analysis: get-all at t=0 returns only pd.pdInfoFull;
            # get-all at t=5s returns full module dumps (PD:58, MPPT:36, INV:28 keys).
            _LOGGER.debug("EcoFlow: waiting 5s for device init before get-all request")
            time.sleep(5)
            _request_full_state(c)
        else:
            _LOGGER.error("EcoFlow: MQTT connect FAILED rc=%d for %s", rc, sn)

    def on_subscribe(c, userdata, mid, granted_qos):
        topic = _subscribe_mid.pop(mid, "unknown")
        _LOGGER.info("EcoFlow: MQTT subscribed mid=%d qos=%s topic=%s",
                        mid, granted_qos, topic)

    def on_disconnect(c, userdata, rc):
        if rc == 0:
            _LOGGER.info("EcoFlow: MQTT clean disconnect for %s", sn)
        else:
            _LOGGER.warning(
                "EcoFlow: MQTT unexpected disconnect rc=%d for %s — "
                "paho will auto-reconnect", rc, sn
            )

    def on_message(c, userdata, msg):
        raw_bytes = msg.payload
        _LOGGER.debug(
            "EcoFlow: MQTT message topic=%s len=%d",
            msg.topic, len(raw_bytes)
        )
        try:
            raw = raw_bytes.decode("utf-8")
            payload = json.loads(raw)
        except UnicodeDecodeError:
            _LOGGER.warning(
                "EcoFlow: MQTT payload is binary (protobuf?) — hex: %s",
                raw_bytes[:64].hex()
            )
            return
        except json.JSONDecodeError as exc:
            _LOGGER.warning("EcoFlow: MQTT JSON parse error: %s — raw: %s",
                            exc, raw_bytes[:200])
            return

        # Log set_reply at INFO — flat structure: operateType + code at top level,
        # data.ack is the device-level result (0=rejected, 1=accepted).
        # Confirmed by log analysis v0.2.16:
        #   {'operateType': 'dcOutCfg', 'moduleType': 1, 'code': '0', 'data': {'ack': 0}}
        if topic_set_reply and msg.topic == topic_set_reply:
            try:
                operate_type = payload.get("operateType", "unknown") if isinstance(payload, dict) else "unknown"
                http_code    = payload.get("code", "?")   if isinstance(payload, dict) else "?"
                _data        = payload.get("data")        if isinstance(payload, dict) else None
                ack          = _data.get("ack", "?")      if isinstance(_data, dict) else "?"
            except Exception:
                operate_type, http_code, ack = "parse_error", "?", "?"
            _LOGGER.info(
                "EcoFlow: set_reply operateType=%s code=%s ack=%s len=%d",
                operate_type, http_code, ack, len(raw_bytes)
            )
        elif topic_get_reply and msg.topic == topic_get_reply:
            _LOGGER.info("EcoFlow: MQTT get_reply received (full state ack) len=%d", len(raw_bytes))

        hass.loop.call_soon_threadsafe(coordinator.update_from_mqtt, payload)

    def on_publish(c, userdata, mid):
        _LOGGER.debug("EcoFlow: MQTT publish ACK mid=%d (command delivered to broker)", mid)

    def _build_client(cid: str, user: str, passwd: str) -> mqtt.Client:
        """Create, configure and return a new paho Client.

        Called at startup and on every recertification. Using a fresh Client
        object is required because paho.client_id is immutable after __init__,
        and the EcoFlow broker routes set-commands only to the session matching
        the most recently issued client_id.
        """
        c = mqtt.Client(
            client_id=cid,
            clean_session=True,
            protocol=mqtt.MQTTv311,
        )
        c.username_pw_set(user, passwd)
        c.tls_set(cert_reqs=ssl.CERT_NONE)
        c.tls_insecure_set(True)
        c.on_connect    = on_connect
        c.on_subscribe  = on_subscribe
        c.on_disconnect = on_disconnect
        c.on_message    = on_message
        c.on_publish    = on_publish
        c.reconnect_delay_set(min_delay=5, max_delay=60)
        _LOGGER.info("EcoFlow: MQTT client_id=%s", cid)
        return c

    # Initial connect
    init_cid  = mqtt_info.get("_client_id") or f"HA-{mqtt_info.get('certificateAccount','')}-{sn}"[:23]
    init_user = mqtt_info.get("certificateAccount", "")
    init_pass = mqtt_info.get("certificatePassword", "")

    # _build_client calls tls_set synchronously — run in executor to avoid
    # blocking the event loop (tls_set can do file I/O for CA bundles).
    client = await hass.async_add_executor_job(
        _build_client, init_cid, init_user, init_pass
    )
    client.connect_async(mqtt_host, mqtt_port, keepalive=MQTT_KEEPALIVE)
    client.loop_start()

    hass.data[DOMAIN][entry.entry_id].update({
        "mqtt_client":    client,
        "mqtt_topic_set": topic_set,
        "mqtt_user":      init_user,
    })

    # ── Periodic recertification ──────────────────────────────────────────
    # v0.2.18: creates a new Client object per cycle so the broker receives
    # a connection from the correct client_id that was just issued.
    # Previous approach (client.reconnect() with old client_id) caused the
    # broker to ignore all set-commands after the first recertification cycle.
    RECERT_INTERVAL = 600  # seconds

    async def _recertify_loop():
        while True:
            await asyncio.sleep(RECERT_INTERVAL)
            _LOGGER.info("EcoFlow: periodic recertification starting…")
            try:
                new_info = await hass.async_add_executor_job(api.get_mqtt_credentials)
            except Exception as exc:
                _LOGGER.warning("EcoFlow: recertification failed (will retry): %s", exc)
                continue

            new_cid  = new_info.get("_client_id", "")
            new_user = new_info.get("certificateAccount", "")
            new_pass = new_info.get("certificatePassword", "")

            if not new_pass:
                _LOGGER.warning("EcoFlow: recertification returned empty password — skipping")
                continue
            if not new_cid:
                _LOGGER.warning("EcoFlow: recertification returned empty client_id — skipping")
                continue

            _LOGGER.info(
                "EcoFlow: recertification OK — new client_id=%s, building new MQTT client",
                new_cid
            )

            try:
                new_client = await hass.async_add_executor_job(
                    _build_client, new_cid, new_user, new_pass
                )
            except Exception as exc:
                _LOGGER.warning("EcoFlow: failed to build new MQTT client: %s — keeping old", exc)
                continue

            # Stop old client before starting new one
            old_client = hass.data[DOMAIN][entry.entry_id].get("mqtt_client")
            if old_client:
                try:
                    old_client.loop_stop()
                    old_client.disconnect()
                except Exception as exc:
                    _LOGGER.debug("EcoFlow: error stopping old client (non-fatal): %s", exc)

            # Atomic update — switch.py and number.py read this reference on every publish
            new_client.connect_async(mqtt_host, mqtt_port, keepalive=MQTT_KEEPALIVE)
            new_client.loop_start()
            hass.data[DOMAIN][entry.entry_id]["mqtt_client"] = new_client
            _LOGGER.info("EcoFlow: new MQTT client active (client_id=%s)", new_cid)

    hass.loop.create_task(_recertify_loop())

    await hass.config_entries.async_forward_entry_setups(entry, PLATFORMS)
    return True


async def async_unload_entry(hass: HomeAssistant, entry: ConfigEntry) -> bool:
    ok = await hass.config_entries.async_unload_platforms(entry, PLATFORMS)
    if ok:
        d = hass.data[DOMAIN].pop(entry.entry_id, {})
        c = d.get("mqtt_client")
        if c:
            c.loop_stop()
            c.disconnect()
    return ok
