#!/usr/bin/env python3
"""
EcoFlow Developer API Credential Test (Python)
------------------------------------------------
Tests your Access Key + Secret Key against the EcoFlow Developer API.

Usage:
    python3 test_developer_api.py

Fill in your credentials below before running.

Signing spec (confirmed 19 March 2026):
  GET:  HMAC-SHA256(accessKey=...&nonce=...&timestamp=..., secretKey)
  PUT:  HMAC-SHA256(flat_body_sorted&accessKey=...&nonce=...&timestamp=..., secretKey)
        where nested params are flattened with dot notation (params.enabled=0)

Requires: pip install requests
"""

import hashlib
import hmac
import json
import random
import time

import requests

# -- Fill in your credentials ---------------------------------------------
ACCESS_KEY = ""     # From https://developer-eu.ecoflow.com/us/security
SECRET_KEY = ""     # From https://developer-eu.ecoflow.com/us/security
DEVICE_SN  = ""     # Your device serial number (e.g. D361ZEH49GAR0848)

# API host - EU by default. Change to https://api.ecoflow.com for US.
API_HOST = "https://api-e.ecoflow.com"
# -- End credentials -------------------------------------------------------


def _flatten(obj, prefix=""):
    """Recursively flatten nested dict with dot notation."""
    result = {}
    for k, v in obj.items():
        full_key = f"{prefix}.{k}" if prefix else k
        if isinstance(v, dict):
            result.update(_flatten(v, full_key))
        else:
            result[full_key] = str(v)
    return result


def _make_headers(access_key, secret_key, body_params=None):
    """
    Build signed headers for EcoFlow Developer API.

    GET:  sign only accessKey + nonce + timestamp
    PUT:  flatten body params, sort by ASCII, then append auth fields
    """
    nonce = str(random.randint(100_000, 999_999))
    timestamp = str(int(time.time() * 1000))

    auth_part = f"accessKey={access_key}&nonce={nonce}&timestamp={timestamp}"

    if body_params:
        flat = _flatten(body_params)
        sorted_params = "&".join(f"{k}={v}" for k, v in sorted(flat.items()))
        sign_input = f"{sorted_params}&{auth_part}"
    else:
        sign_input = auth_part

    signature = hmac.new(
        secret_key.encode(), sign_input.encode(), hashlib.sha256
    ).hexdigest()

    return {
        "Content-Type": "application/json",
        "accessKey": access_key,
        "nonce": nonce,
        "timestamp": timestamp,
        "sign": signature,
    }, sign_input


def test_device_list():
    print("\n" + "=" * 60)
    print("TEST 1: GET /device/list")
    print("=" * 60)
    headers, _ = _make_headers(ACCESS_KEY, SECRET_KEY)
    try:
        r = requests.get(f"{API_HOST}/iot-open/sign/device/list",
                         headers=headers, timeout=15).json()
        print(f"  Code: {r.get('code')}  Message: {r.get('message')}")
        if str(r.get("code")) == "0":
            for d in (r.get("data") or []):
                print(f"  - {d.get('sn')} ({d.get('productName')}) online={d.get('online')}")
            return True
        return False
    except Exception as e:
        print(f"  ERROR: {e}")
        return False


def test_mqtt_creds():
    print("\n" + "=" * 60)
    print("TEST 2: GET /certification")
    print("=" * 60)
    headers, _ = _make_headers(ACCESS_KEY, SECRET_KEY)
    try:
        r = requests.get(f"{API_HOST}/iot-open/sign/certification",
                         headers=headers, timeout=15).json()
        print(f"  Code: {r.get('code')}  Message: {r.get('message')}")
        if str(r.get("code")) == "0":
            d = r.get("data", {})
            print(f"  host={d.get('url')} port={d.get('port')}")
            return True
        return False
    except Exception as e:
        print(f"  ERROR: {e}")
        return False


def test_quota_get():
    if not DEVICE_SN:
        return None
    print("\n" + "=" * 60)
    print(f"TEST 3: GET /device/quota/all (SN={DEVICE_SN})")
    print("=" * 60)
    headers, _ = _make_headers(ACCESS_KEY, SECRET_KEY)
    try:
        r = requests.get(f"{API_HOST}/iot-open/sign/device/quota/all",
                         headers=headers, params={"sn": DEVICE_SN}, timeout=15).json()
        code = str(r.get("code"))
        print(f"  Code: {code}  Message: {r.get('message')}")
        if code == "0":
            return True
        elif "1006" in code:
            print("  NOTE: expected for Delta 3 - use App Login for telemetry")
            return None
        return False
    except Exception as e:
        print(f"  ERROR: {e}")
        return False


def test_quota_set():
    if not DEVICE_SN:
        return None
    print("\n" + "=" * 60)
    print(f"TEST 4: PUT /device/quota (SN={DEVICE_SN})")
    print("=" * 60)
    body = {"sn": DEVICE_SN, "moduleType": 5,
            "operateType": "quietMode", "params": {"enabled": 0}}
    headers, sign_input = _make_headers(ACCESS_KEY, SECRET_KEY, body_params=body)
    print(f"  Body: {json.dumps(body)}")
    print(f"  Sign: {sign_input[:80]}...")
    try:
        r = requests.put(f"{API_HOST}/iot-open/sign/device/quota",
                         headers=headers, json=body, timeout=15).json()
        code = str(r.get("code"))
        print(f"  Code: {code}  Message: {r.get('message')}")
        if code == "0":
            print("  SUCCESS: REST SET accepted!")
            return True
        elif "1006" in code:
            print("  NOTE: device offline - re-test when powered on")
            return None
        elif "8521" in code:
            print("  FAILED: signature wrong")
            return False
        else:
            print(f"  RESULT: code={code} (not 8521 = signing correct)")
            return None
    except Exception as e:
        print(f"  ERROR: {e}")
        return False


def main():
    print("EcoFlow Developer API Credential Test (Python)")
    print(f"Host: {API_HOST}")
    if not ACCESS_KEY or not SECRET_KEY:
        print("ERROR: Fill in ACCESS_KEY and SECRET_KEY.")
        return
    r1 = test_device_list()
    r2 = test_mqtt_creds()
    r3 = test_quota_get()
    r4 = test_quota_set()
    print("\n" + "=" * 60)
    print("SUMMARY")
    print("=" * 60)
    for name, val in [("device_list", r1), ("mqtt_creds", r2),
                      ("quota_get", r3), ("quota_set", r4)]:
        s = "PASS" if val is True else ("SKIP/NOTE" if val is None else "FAIL")
        print(f"  {name:20s}: {s}")


if __name__ == "__main__":
    main()
