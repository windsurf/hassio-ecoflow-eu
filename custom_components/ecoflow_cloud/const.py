"""Constants for EcoFlow Cloud integration."""

DOMAIN              = "ecoflow_cloud"
INTEGRATION_VERSION = "0.4.1"

# Config entry keys
CONF_ACCESS_KEY = "access_key"
CONF_SECRET_KEY = "secret_key"
CONF_DEVICE_SN  = "device_sn"
CONF_API_HOST   = "api_host"
CONF_AUTH_MODE  = "auth_mode"
CONF_EMAIL      = "email"
CONF_PASSWORD   = "password"

# Developer API keys (optional, for hybrid mode REST SET)
CONF_DEV_ACCESS_KEY = "dev_access_key"
CONF_DEV_SECRET_KEY = "dev_secret_key"
CONF_DEV_API_HOST   = "dev_api_host"

# Auth modes
AUTH_MODE_PUBLIC  = "public"   # Open API: Access Key + Secret Key
AUTH_MODE_PRIVATE = "private"  # App login: Email + Password (works for Delta 3)
AUTH_MODE_AUTO    = "auto"     # Auto-detect based on serial number prefix

# EcoFlow Open API endpoints
API_HOST_EU      = "https://api-e.ecoflow.com"
API_HOST_US      = "https://api-a.ecoflow.com"
API_HOST_GLOBAL  = "https://api.ecoflow.com"
API_HOST_DEFAULT = API_HOST_EU

API_PATH_QUOTA       = "/iot-open/sign/device/quota/all"
API_PATH_MQTT        = "/iot-open/sign/certification"
API_PATH_DEVICE_LIST = "/iot-open/sign/device/list"

# MQTT
MQTT_KEEPALIVE          = 120
MQTT_RECONNECT_INTERVAL = 60

# Coordinator polling interval
COORDINATOR_UPDATE_INTERVAL = 30  # seconds

# Device info
MANUFACTURER = "EcoFlow"

# Serial number prefixes for which the Developer REST API SET is blocked.
# EcoFlow returns code=1006 "not allowed to be controlled" for these devices.
# MQTT JSON SET (with "from":"Android") is the correct control path instead.
# v0.4.0: D3M1 (Delta 3 Max Plus) is NOT blocked — the Developer API documents SET for it.
# D3M1 is also not in PRIVATE_API_SN_PREFIXES: Auto-detect uses the Developer API,
# the only route that reports the AC output state.
REST_SET_BLOCKED_SN_PREFIXES = (
    "D361",   # Delta 3 / Delta 3 1500 — confirmed blocked (28 March 2026)
    "P231",   # Delta 3 (v0.4.1) — assumed blocked (same series)
    "D362",   # Delta 3 Plus — assumed blocked (same series)
    "P351",   # Delta 3 Plus (v0.4.1) — assumed blocked (same series)
    "D381",   # Delta 3 Max — assumed blocked (same series)
    "D3N1",   # Delta 3 Max (v0.4.1) — assumed blocked (same series)
    "R64",    # River 3 — assumed blocked
    "R65",    # River 3 (v0.4.1, R651 and R655) — same series
    "R63",    # River 3 Plus (v0.4.1, R631) — same series
)

PRIVATE_API_SN_PREFIXES = (
    "D361",   # Delta 3 / Delta 3 1500
    "P231",   # Delta 3 (v0.4.1)
    "D362",   # Delta 3 Plus
    "P351",   # Delta 3 Plus (v0.4.1)
    "D381",   # Delta 3 Max (tentative)
    "D3N1",   # Delta 3 Max (v0.4.1)
    "R64",    # River 3
    "R65",    # River 3 (v0.4.1, R651 and R655)
    "R63",    # River 3 Plus (v0.4.1, R631)
    "HW51",   # PowerStream (600 W and 800 W)
    "Y71",    # Delta Pro Ultra (v0.4.1; DGEB is the Smart Generator)
    "DGEA",   # Delta Pro 3
    "MR5",    # Delta Pro 3 (v0.4.1)
)

# Sentinel value used by EcoFlow in cfgChgWatts to mean "keep current value".
# The device echoes this back in telemetry — do not write to HA state.
CHG_WATTS_SENTINEL = 255

# v0.4.0: number of raw MQTT messages kept in memory for the diagnostics download
MQTT_DIAG_BUFFER_SIZE = 50
