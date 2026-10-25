"""Extra entities for the Delta Pro 3 (v0.4.0), from the EcoFlow device documentation.

Disabled by default. See NOTICE and LICENSE in the repository root.
"""
from __future__ import annotations

from ..switch import EcoFlowSwitchDescription

MODEL = "Delta Pro 3"

SWITCHES = (
    EcoFlowSwitchDescription(
        key="dp3_dc_24v", name="DC 24V Output 🧪", icon="mdi:car-battery",
        state_key="flowInfo24v",
        dp3_cmd_key="cfgDc24vOutOpen",
        optimistic=True,
        entity_registry_enabled_default=False,
    ),
)
