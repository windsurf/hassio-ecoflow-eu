"""Extra entities for the Delta Max (v0.4.0), from the EcoFlow device documentation.

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

MODEL = "Delta Max"
_OFF = {"entity_registry_enabled_default": False}
_CHG_STATE = ((0, "unused"), (1, "charging"), (2, "discharging"))

SENSORS = (
        D(key='ems.f32LcdShowSoc', name='Battery Level (Precise)', native_unit_of_measurement=PERCENTAGE, device_class=SensorDeviceClass.BATTERY, state_class=SensorStateClass.MEASUREMENT, round_digits=None, **_OFF),
        D(key='inv.outTemp', name='Inv Out Temperature', native_unit_of_measurement=UnitOfTemperature.CELSIUS, device_class=SensorDeviceClass.TEMPERATURE, state_class=SensorStateClass.MEASUREMENT, entity_category=EntityCategory.DIAGNOSTIC, round_digits=None, **_OFF),
        D(key='bmsSlave1.designCap', name='Slave 1 Design Capacity', native_unit_of_measurement='mAh', state_class=SensorStateClass.MEASUREMENT, round_digits=None, **_OFF),
        D(key='bmsSlave1.fullCap', name='Slave 1 Full Capacity', native_unit_of_measurement='mAh', state_class=SensorStateClass.MEASUREMENT, round_digits=None, **_OFF),
        D(key='bmsSlave1.remainCap', name='Slave 1 Remain Capacity', native_unit_of_measurement='mAh', state_class=SensorStateClass.MEASUREMENT, round_digits=None, **_OFF),
        D(key='bmsSlave2.designCap', name='Slave 2 Design Capacity', native_unit_of_measurement='mAh', state_class=SensorStateClass.MEASUREMENT, round_digits=None, **_OFF),
        D(key='bmsSlave2.fullCap', name='Slave 2 Full Capacity', native_unit_of_measurement='mAh', state_class=SensorStateClass.MEASUREMENT, round_digits=None, **_OFF),
        D(key='bmsSlave2.remainCap', name='Slave 2 Remain Capacity', native_unit_of_measurement='mAh', state_class=SensorStateClass.MEASUREMENT, round_digits=None, **_OFF),
    )
