"""Extra entities for the PowerStream (v0.4.0), from the EcoFlow device documentation.

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

MODEL = "PowerStream"
_OFF = {"entity_registry_enabled_default": False}
_CHG_STATE = ((0, "unused"), (1, "charging"), (2, "discharging"))

SENSORS = (
        D(key='20_1.pv1RelayStatus', name='Solar 1 Relay Status', entity_category=EntityCategory.DIAGNOSTIC, round_digits=None, **_OFF),
        D(key='20_1.pv1ErrCode', name='Solar 1 Error Code', entity_category=EntityCategory.DIAGNOSTIC, round_digits=None, **_OFF),
        D(key='20_1.pv1WarnCode', name='Solar 1 Warning Code', entity_category=EntityCategory.DIAGNOSTIC, round_digits=None, **_OFF),
        D(key='20_1.pv1Statue', name='Solar 1 Status', entity_category=EntityCategory.DIAGNOSTIC, round_digits=None, **_OFF),
        D(key='20_1.pv2RelayStatus', name='Solar 2 Relay Status', entity_category=EntityCategory.DIAGNOSTIC, round_digits=None, **_OFF),
        D(key='20_1.pv2ErrCode', name='Solar 2 Error Code', entity_category=EntityCategory.DIAGNOSTIC, round_digits=None, **_OFF),
        D(key='20_1.pv2WarningCode', name='Solar 2 Warning Code', entity_category=EntityCategory.DIAGNOSTIC, round_digits=None, **_OFF),
        D(key='20_1.pv2Statue', name='Solar 2 Status', entity_category=EntityCategory.DIAGNOSTIC, round_digits=None, **_OFF),
        D(key='20_1.bpType', name='Battery Type', entity_category=EntityCategory.DIAGNOSTIC, round_digits=None, **_OFF),
        D(key='20_1.batInputVolt', name='Battery Input Potential', native_unit_of_measurement=UnitOfElectricPotential.VOLT, device_class=SensorDeviceClass.VOLTAGE, state_class=SensorStateClass.MEASUREMENT, scale=0.1, round_digits=3, **_OFF),
        D(key='20_1.batOpVolt', name='Battery Op Potential', native_unit_of_measurement=UnitOfElectricPotential.VOLT, device_class=SensorDeviceClass.VOLTAGE, state_class=SensorStateClass.MEASUREMENT, scale=0.1, round_digits=3, **_OFF),
        D(key='20_1.batInputCur', name='Battery Input Current', native_unit_of_measurement=UnitOfElectricCurrent.MILLIAMPERE, device_class=SensorDeviceClass.CURRENT, state_class=SensorStateClass.MEASUREMENT, round_digits=None, **_OFF),
        D(key='20_1.batErrCode', name='Battery Error Code', entity_category=EntityCategory.DIAGNOSTIC, round_digits=None, **_OFF),
        D(key='20_1.batWarningCode', name='Battery Warning Code', entity_category=EntityCategory.DIAGNOSTIC, round_digits=None, **_OFF),
        D(key='20_1.batStatue', name='Battery Status', entity_category=EntityCategory.DIAGNOSTIC, round_digits=None, **_OFF),
        D(key='20_1.llcInputVolt', name='LLC Input Potential', native_unit_of_measurement=UnitOfElectricPotential.VOLT, device_class=SensorDeviceClass.VOLTAGE, state_class=SensorStateClass.MEASUREMENT, scale=0.1, round_digits=3, **_OFF),
        D(key='20_1.llcOpVolt', name='LLC Op Potential', native_unit_of_measurement=UnitOfElectricPotential.VOLT, device_class=SensorDeviceClass.VOLTAGE, state_class=SensorStateClass.MEASUREMENT, scale=0.1, round_digits=3, **_OFF),
        D(key='20_1.llcTemp', name='LLC Temperature', native_unit_of_measurement=UnitOfTemperature.CELSIUS, device_class=SensorDeviceClass.TEMPERATURE, state_class=SensorStateClass.MEASUREMENT, scale=0.1, entity_category=EntityCategory.DIAGNOSTIC, round_digits=3, **_OFF),
        D(key='20_1.llcErrCode', name='LLC Error Code', entity_category=EntityCategory.DIAGNOSTIC, round_digits=None, **_OFF),
        D(key='20_1.llcWarningCode', name='LLC Warning Code', entity_category=EntityCategory.DIAGNOSTIC, round_digits=None, **_OFF),
        D(key='20_1.llcStatue', name='LLC Status', entity_category=EntityCategory.DIAGNOSTIC, round_digits=None, **_OFF),
        D(key='20_1.invOnOff', name='Inverter On/Off Status', entity_category=EntityCategory.DIAGNOSTIC, round_digits=None, **_OFF),
        D(key='20_1.invInputVolt', name='Inverter Output Potential', native_unit_of_measurement=UnitOfElectricPotential.VOLT, device_class=SensorDeviceClass.VOLTAGE, state_class=SensorStateClass.MEASUREMENT, scale=0.1, round_digits=3, **_OFF),
        D(key='20_1.invOpVolt', name='Inverter Op Potential', native_unit_of_measurement=UnitOfElectricPotential.VOLT, device_class=SensorDeviceClass.VOLTAGE, state_class=SensorStateClass.MEASUREMENT, scale=0.1, round_digits=3, **_OFF),
        D(key='20_1.invOutputCur', name='Inverter Output Current', native_unit_of_measurement=UnitOfElectricCurrent.MILLIAMPERE, device_class=SensorDeviceClass.CURRENT, state_class=SensorStateClass.MEASUREMENT, round_digits=None, **_OFF),
        D(key='20_1.invRelayStatus', name='Inverter Relay Status', entity_category=EntityCategory.DIAGNOSTIC, round_digits=None, **_OFF),
        D(key='20_1.invErrCode', name='Inverter Error Code', entity_category=EntityCategory.DIAGNOSTIC, round_digits=None, **_OFF),
        D(key='20_1.invWarnCode', name='Inverter Warning Code', entity_category=EntityCategory.DIAGNOSTIC, round_digits=None, **_OFF),
        D(key='20_1.invStatue', name='Inverter Status', entity_category=EntityCategory.DIAGNOSTIC, round_digits=None, **_OFF),
        D(key='20_1.permanentWatts', name='Custom Load Power', native_unit_of_measurement=UnitOfPower.WATT, device_class=SensorDeviceClass.POWER, state_class=SensorStateClass.MEASUREMENT, scale=0.1, round_digits=3, **_OFF),
        D(key='20_1.wirelessErrCode', name='Wireless Error Code', entity_category=EntityCategory.DIAGNOSTIC, round_digits=None, **_OFF),
        D(key='20_1.wirelessWarnCode', name='Wireless Warning Code', entity_category=EntityCategory.DIAGNOSTIC, round_digits=None, **_OFF),
        D(key='20_1.heartbeatFrequency', name='Heartbeat Frequency', entity_category=EntityCategory.DIAGNOSTIC, round_digits=None, **_OFF),
        D(key='254_32.watthPv1', name='PV1 Today Energy Total', native_unit_of_measurement=UnitOfEnergy.WATT_HOUR, device_class=SensorDeviceClass.ENERGY, state_class=SensorStateClass.TOTAL_INCREASING, icon='mdi:solar-power', round_digits=None, **_OFF),
        D(key='254_32.watthPv2', name='PV2 Today Energy Total', native_unit_of_measurement=UnitOfEnergy.WATT_HOUR, device_class=SensorDeviceClass.ENERGY, state_class=SensorStateClass.TOTAL_INCREASING, icon='mdi:solar-power', round_digits=None, **_OFF),
        D(key='254_32.watthToSmartPlugs', name='To Smart Plugs Today Energy Total', native_unit_of_measurement=UnitOfEnergy.WATT_HOUR, device_class=SensorDeviceClass.ENERGY, state_class=SensorStateClass.TOTAL_INCREASING, icon='mdi:transmission-tower-export', round_digits=None, **_OFF),
        D(key='254_32.watthFromBattery', name='From Battery Today Energy Total', native_unit_of_measurement=UnitOfEnergy.WATT_HOUR, device_class=SensorDeviceClass.ENERGY, state_class=SensorStateClass.TOTAL_INCREASING, icon='mdi:transmission-tower-import', round_digits=None, **_OFF),
        D(key='254_32.watthToBattery', name='To Battery Today Energy Total', native_unit_of_measurement=UnitOfEnergy.WATT_HOUR, device_class=SensorDeviceClass.ENERGY, state_class=SensorStateClass.TOTAL_INCREASING, icon='mdi:transmission-tower-export', round_digits=None, **_OFF),
    )
