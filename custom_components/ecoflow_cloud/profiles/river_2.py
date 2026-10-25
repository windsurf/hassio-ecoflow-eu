"""Extra entities for the River 2 (v0.4.0), from the EcoFlow device documentation.

Disabled by default. See NOTICE and LICENSE in the repository root.
"""
from __future__ import annotations

from homeassistant.components.sensor import SensorDeviceClass, SensorStateClass
from homeassistant.const import (
    PERCENTAGE,
    UnitOfElectricCurrent,
    UnitOfElectricPotential,
    UnitOfEnergy,
    UnitOfFrequency,
    UnitOfPower,
    UnitOfTemperature,
    UnitOfTime,
)
from homeassistant.helpers.entity import EntityCategory

from ..sensor import EcoFlowSensorDescription as D

MODEL = "River 2"
_OFF = {"entity_registry_enabled_default": False}
_CHG_STATE = ((0, "unused"), (1, "charging"), (2, "discharging"))

SENSORS = (
        D(key='mppt.inAmp', name='Solar In Current', native_unit_of_measurement=UnitOfElectricCurrent.MILLIAMPERE, device_class=SensorDeviceClass.CURRENT, state_class=SensorStateClass.MEASUREMENT, icon='mdi:transmission-tower-import', round_digits=None, **_OFF),
        D(key='mppt.inVol', name='Solar In Voltage', native_unit_of_measurement=UnitOfElectricPotential.MILLIVOLT, device_class=SensorDeviceClass.VOLTAGE, state_class=SensorStateClass.MEASUREMENT, icon='mdi:transmission-tower-import', round_digits=None, **_OFF),
        D(key='bms_bmsStatus.soc', name='Main Battery Level', native_unit_of_measurement=PERCENTAGE, device_class=SensorDeviceClass.BATTERY, state_class=SensorStateClass.MEASUREMENT, round_digits=None, **_OFF),
    )
