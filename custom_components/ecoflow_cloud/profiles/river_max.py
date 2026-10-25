"""Extra entities for the River Max (v0.4.0), from the EcoFlow device documentation.

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

MODEL = "River Max"
_OFF = {"entity_registry_enabled_default": False}
_CHG_STATE = ((0, "unused"), (1, "charging"), (2, "discharging"))

SENSORS = (
        D(key='inv.dcInAmp', name='Solar In Current', native_unit_of_measurement=UnitOfElectricCurrent.MILLIAMPERE, device_class=SensorDeviceClass.CURRENT, state_class=SensorStateClass.MEASUREMENT, icon='mdi:transmission-tower-import', round_digits=None, **_OFF),
        D(key='inv.dcInVol', name='Solar In Voltage', native_unit_of_measurement=UnitOfElectricPotential.MILLIVOLT, device_class=SensorDeviceClass.VOLTAGE, state_class=SensorStateClass.MEASUREMENT, icon='mdi:transmission-tower-import', round_digits=None, **_OFF),
        D(key='pd.carTemp', name='DC Temperature', native_unit_of_measurement=UnitOfTemperature.CELSIUS, device_class=SensorDeviceClass.TEMPERATURE, state_class=SensorStateClass.MEASUREMENT, entity_category=EntityCategory.DIAGNOSTIC, round_digits=None, **_OFF),
        D(key='pd.typecTemp', name='USB C Temperature', native_unit_of_measurement=UnitOfTemperature.CELSIUS, device_class=SensorDeviceClass.TEMPERATURE, state_class=SensorStateClass.MEASUREMENT, entity_category=EntityCategory.DIAGNOSTIC, round_digits=None, **_OFF),
        D(key='bmsMaster.amp', name='Battery Current', native_unit_of_measurement=UnitOfElectricCurrent.MILLIAMPERE, device_class=SensorDeviceClass.CURRENT, state_class=SensorStateClass.MEASUREMENT, round_digits=None, **_OFF),
        D(key='bmsSlave1.designCap', name='Slave Design Capacity', native_unit_of_measurement='mAh', state_class=SensorStateClass.MEASUREMENT, round_digits=None, **_OFF),
        D(key='bmsSlave1.fullCap', name='Slave Full Capacity', native_unit_of_measurement='mAh', state_class=SensorStateClass.MEASUREMENT, round_digits=None, **_OFF),
        D(key='bmsSlave1.remainCap', name='Slave Remain Capacity', native_unit_of_measurement='mAh', state_class=SensorStateClass.MEASUREMENT, round_digits=None, **_OFF),
        D(key='bmsSlave1.minCellTemp', name='Slave Min Cell Temperature', native_unit_of_measurement=UnitOfTemperature.CELSIUS, device_class=SensorDeviceClass.TEMPERATURE, state_class=SensorStateClass.MEASUREMENT, entity_category=EntityCategory.DIAGNOSTIC, round_digits=None, **_OFF),
        D(key='bmsSlave1.maxCellTemp', name='Slave Max Cell Temperature', native_unit_of_measurement=UnitOfTemperature.CELSIUS, device_class=SensorDeviceClass.TEMPERATURE, state_class=SensorStateClass.MEASUREMENT, entity_category=EntityCategory.DIAGNOSTIC, round_digits=None, **_OFF),
        D(key='bmsSlave1.amp', name='Slave Battery Current', native_unit_of_measurement=UnitOfElectricCurrent.MILLIAMPERE, device_class=SensorDeviceClass.CURRENT, state_class=SensorStateClass.MEASUREMENT, round_digits=None, **_OFF),
    )
