"""Extra entities for the Stream AC (v0.4.0), from the EcoFlow device documentation.

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

MODEL = "Stream AC"
_OFF = {"entity_registry_enabled_default": False}
_CHG_STATE = ((0, "unused"), (1, "charging"), (2, "discharging"))

SENSORS = (
        D(key='accuChgCap', name='Cumulative Capacity Charge (mAh)', native_unit_of_measurement='mAh', state_class=SensorStateClass.TOTAL_INCREASING, round_digits=None, **_OFF),
        D(key='accuChgEnergy', name='Cumulative Energy Charge (Wh)', native_unit_of_measurement=UnitOfEnergy.WATT_HOUR, device_class=SensorDeviceClass.ENERGY, state_class=SensorStateClass.TOTAL_INCREASING, round_digits=None, **_OFF),
        D(key='accuDsgCap', name='Cumulative Capacity Discharge (mAh)', native_unit_of_measurement='mAh', state_class=SensorStateClass.TOTAL_INCREASING, round_digits=None, **_OFF),
        D(key='accuDsgEnergy', name='Cumulative Energy Discharge (Wh)', native_unit_of_measurement=UnitOfEnergy.WATT_HOUR, device_class=SensorDeviceClass.ENERGY, state_class=SensorStateClass.TOTAL_INCREASING, round_digits=None, **_OFF),
        D(key='bmsChgRemTime', name='Charge Remaining Time', native_unit_of_measurement=UnitOfTime.MINUTES, device_class=SensorDeviceClass.DURATION, state_class=SensorStateClass.MEASUREMENT, round_digits=None, **_OFF),
        D(key='bmsDsgRemTime', name='Discharge Remaining Time', native_unit_of_measurement=UnitOfTime.MINUTES, device_class=SensorDeviceClass.DURATION, state_class=SensorStateClass.MEASUREMENT, round_digits=None, **_OFF),
        D(key='cmsBattSoc', name='Battery Level', native_unit_of_measurement=PERCENTAGE, device_class=SensorDeviceClass.BATTERY, state_class=SensorStateClass.MEASUREMENT, round_digits=None, **_OFF),
        D(key='cmsMaxChgSoc', name='Max Charge Level', native_unit_of_measurement=PERCENTAGE, state_class=SensorStateClass.MEASUREMENT, round_digits=None, **_OFF),
        D(key='cmsMinDsgSoc', name='Min Discharge Level', native_unit_of_measurement=PERCENTAGE, state_class=SensorStateClass.MEASUREMENT, round_digits=None, **_OFF),
        D(key='cycles', name='Cycles', state_class=SensorStateClass.TOTAL_INCREASING, icon='mdi:battery-heart-variant', entity_category=EntityCategory.DIAGNOSTIC, round_digits=None, **_OFF),
        D(key='designCap', name='Design Capacity', native_unit_of_measurement='mAh', state_class=SensorStateClass.MEASUREMENT, round_digits=None, **_OFF),
        D(key='f32ShowSoc', name='Power Battery SOC', native_unit_of_measurement=PERCENTAGE, device_class=SensorDeviceClass.BATTERY, state_class=SensorStateClass.MEASUREMENT, round_digits=None, **_OFF),
        D(key='fullCap', name='Full Capacity', native_unit_of_measurement='mAh', state_class=SensorStateClass.MEASUREMENT, round_digits=None, **_OFF),
        D(key='inputWatts', name='In Power', native_unit_of_measurement=UnitOfPower.WATT, device_class=SensorDeviceClass.POWER, state_class=SensorStateClass.MEASUREMENT, icon='mdi:transmission-tower-import', round_digits=None, **_OFF),
        D(key='maxCellTemp', name='Max Cell Temperature', native_unit_of_measurement=UnitOfTemperature.CELSIUS, device_class=SensorDeviceClass.TEMPERATURE, state_class=SensorStateClass.MEASUREMENT, entity_category=EntityCategory.DIAGNOSTIC, round_digits=None, **_OFF),
        D(key='maxCellVol', name='Max Cell Volts', native_unit_of_measurement=UnitOfElectricPotential.MILLIVOLT, device_class=SensorDeviceClass.VOLTAGE, state_class=SensorStateClass.MEASUREMENT, round_digits=None, **_OFF),
        D(key='minCellTemp', name='Min Cell Temperature', native_unit_of_measurement=UnitOfTemperature.CELSIUS, device_class=SensorDeviceClass.TEMPERATURE, state_class=SensorStateClass.MEASUREMENT, entity_category=EntityCategory.DIAGNOSTIC, round_digits=None, **_OFF),
        D(key='minCellVol', name='Min Cell Volts', native_unit_of_measurement=UnitOfElectricPotential.MILLIVOLT, device_class=SensorDeviceClass.VOLTAGE, state_class=SensorStateClass.MEASUREMENT, round_digits=None, **_OFF),
        D(key='outputWatts', name='Out Power', native_unit_of_measurement=UnitOfPower.WATT, device_class=SensorDeviceClass.POWER, state_class=SensorStateClass.MEASUREMENT, icon='mdi:transmission-tower-export', round_digits=None, **_OFF),
        D(key='powGetBpCms', name='Power Battery', native_unit_of_measurement=UnitOfPower.WATT, device_class=SensorDeviceClass.POWER, state_class=SensorStateClass.MEASUREMENT, round_digits=None, **_OFF),
        D(key='powGetPv2', name='Power PV 2', native_unit_of_measurement=UnitOfPower.WATT, device_class=SensorDeviceClass.POWER, state_class=SensorStateClass.MEASUREMENT, round_digits=None, **_OFF),
        D(key='powGetPv3', name='Power PV 3', native_unit_of_measurement=UnitOfPower.WATT, device_class=SensorDeviceClass.POWER, state_class=SensorStateClass.MEASUREMENT, round_digits=None, **_OFF),
        D(key='powGetPv4', name='Power PV 4', native_unit_of_measurement=UnitOfPower.WATT, device_class=SensorDeviceClass.POWER, state_class=SensorStateClass.MEASUREMENT, round_digits=None, **_OFF),
        D(key='plugInInfoPvVol', name='Power PV1 Volts', native_unit_of_measurement=UnitOfElectricPotential.VOLT, device_class=SensorDeviceClass.VOLTAGE, state_class=SensorStateClass.MEASUREMENT, round_digits=None, **_OFF),
        D(key='plugInInfoPv2Vol', name='Power PV2 Volts', native_unit_of_measurement=UnitOfElectricPotential.VOLT, device_class=SensorDeviceClass.VOLTAGE, state_class=SensorStateClass.MEASUREMENT, round_digits=None, **_OFF),
        D(key='plugInInfoPv3Vol', name='Power PV3 Volts', native_unit_of_measurement=UnitOfElectricPotential.VOLT, device_class=SensorDeviceClass.VOLTAGE, state_class=SensorStateClass.MEASUREMENT, round_digits=None, **_OFF),
        D(key='plugInInfoPv4Vol', name='Power PV4 Volts', native_unit_of_measurement=UnitOfElectricPotential.VOLT, device_class=SensorDeviceClass.VOLTAGE, state_class=SensorStateClass.MEASUREMENT, round_digits=None, **_OFF),
        D(key='plugInInfoPvAmp', name='Power PV1 In Amps', native_unit_of_measurement=UnitOfElectricCurrent.AMPERE, device_class=SensorDeviceClass.CURRENT, state_class=SensorStateClass.MEASUREMENT, round_digits=None, **_OFF),
        D(key='plugInInfoPv2Amp', name='Power PV2 In Amps', native_unit_of_measurement=UnitOfElectricCurrent.AMPERE, device_class=SensorDeviceClass.CURRENT, state_class=SensorStateClass.MEASUREMENT, round_digits=None, **_OFF),
        D(key='plugInInfoPv3Amp', name='Power PV3 In Amps', native_unit_of_measurement=UnitOfElectricCurrent.AMPERE, device_class=SensorDeviceClass.CURRENT, state_class=SensorStateClass.MEASUREMENT, round_digits=None, **_OFF),
        D(key='plugInInfoPv4Amp', name='Power PV4 In Amps', native_unit_of_measurement=UnitOfElectricCurrent.AMPERE, device_class=SensorDeviceClass.CURRENT, state_class=SensorStateClass.MEASUREMENT, round_digits=None, **_OFF),
        D(key='realSoh', name='Real State of Health', native_unit_of_measurement=PERCENTAGE, state_class=SensorStateClass.MEASUREMENT, round_digits=None, **_OFF),
        D(key='remainCap', name='Remain Capacity', native_unit_of_measurement='mAh', state_class=SensorStateClass.MEASUREMENT, round_digits=None, **_OFF),
        D(key='remainTime', name='Remaining Time', native_unit_of_measurement=UnitOfTime.MINUTES, device_class=SensorDeviceClass.DURATION, state_class=SensorStateClass.MEASUREMENT, round_digits=None, **_OFF),
        D(key='soh', name='State of Health', native_unit_of_measurement=PERCENTAGE, state_class=SensorStateClass.MEASUREMENT, round_digits=None, **_OFF),
        D(key='sysGridConnectionPower', name='Power AC SYS', native_unit_of_measurement=UnitOfPower.WATT, device_class=SensorDeviceClass.POWER, state_class=SensorStateClass.MEASUREMENT, round_digits=None, **_OFF),
        D(key='temp', name='Battery Temperature', native_unit_of_measurement=UnitOfTemperature.CELSIUS, device_class=SensorDeviceClass.TEMPERATURE, state_class=SensorStateClass.MEASUREMENT, entity_category=EntityCategory.DIAGNOSTIC, round_digits=None, **_OFF),
        D(key='vol', name='Battery Volts', native_unit_of_measurement=UnitOfElectricPotential.MILLIVOLT, device_class=SensorDeviceClass.VOLTAGE, state_class=SensorStateClass.MEASUREMENT, round_digits=None, **_OFF),
        D(key='soc', name='Power Battery (soc)', native_unit_of_measurement=PERCENTAGE, device_class=SensorDeviceClass.BATTERY, state_class=SensorStateClass.MEASUREMENT, round_digits=None, **_OFF),
    )
