"""Extra entities for the Glacier (v0.4.0), from the EcoFlow device documentation.

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

MODEL = "Glacier"
_OFF = {"entity_registry_enabled_default": False}
_CHG_STATE = ((0, "unused"), (1, "charging"), (2, "discharging"))

SENSORS = (
        D(key='bms_bmsStatus.minCellTmp', name='Min Cell Temperature', native_unit_of_measurement=UnitOfTemperature.CELSIUS, device_class=SensorDeviceClass.TEMPERATURE, state_class=SensorStateClass.MEASUREMENT, entity_category=EntityCategory.DIAGNOSTIC, round_digits=None, **_OFF),
        D(key='bms_bmsStatus.maxCellTmp', name='Max Cell Temperature', native_unit_of_measurement=UnitOfTemperature.CELSIUS, device_class=SensorDeviceClass.TEMPERATURE, state_class=SensorStateClass.MEASUREMENT, entity_category=EntityCategory.DIAGNOSTIC, round_digits=None, **_OFF),
        D(key='bms_bmsStatus.minCellVol', name='Min Cell Volts', native_unit_of_measurement=UnitOfElectricPotential.MILLIVOLT, device_class=SensorDeviceClass.VOLTAGE, state_class=SensorStateClass.MEASUREMENT, round_digits=None, **_OFF),
        D(key='bms_bmsStatus.maxCellVol', name='Max Cell Volts', native_unit_of_measurement=UnitOfElectricPotential.MILLIVOLT, device_class=SensorDeviceClass.VOLTAGE, state_class=SensorStateClass.MEASUREMENT, round_digits=None, **_OFF),
        D(key='pd.xt60InState', name='XT60 State', entity_category=EntityCategory.DIAGNOSTIC, round_digits=None, **_OFF),
        D(key='bms_emsStatus.fanLvl', name='Fan Level', state_class=SensorStateClass.MEASUREMENT, icon='mdi:fan', round_digits=None, **_OFF),
        D(key='pd.iceMkMode', name='Ice Make Mode', entity_category=EntityCategory.DIAGNOSTIC, round_digits=None, **_OFF),
    )
