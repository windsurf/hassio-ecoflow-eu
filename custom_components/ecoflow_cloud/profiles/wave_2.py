"""Extra entities for the Wave 2 (v0.4.0), from the EcoFlow device documentation.

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

MODEL = "Wave 2"
_OFF = {"entity_registry_enabled_default": False}
_CHG_STATE = ((0, "unused"), (1, "charging"), (2, "discharging"))

SENSORS = (
        D(key='bms.minCellTmp', name='Min Cell Temperature', native_unit_of_measurement=UnitOfTemperature.CELSIUS, device_class=SensorDeviceClass.TEMPERATURE, state_class=SensorStateClass.MEASUREMENT, entity_category=EntityCategory.DIAGNOSTIC, round_digits=None, **_OFF),
        D(key='bms.maxCellTmp', name='Max Cell Temperature', native_unit_of_measurement=UnitOfTemperature.CELSIUS, device_class=SensorDeviceClass.TEMPERATURE, state_class=SensorStateClass.MEASUREMENT, entity_category=EntityCategory.DIAGNOSTIC, round_digits=None, **_OFF),
        D(key='pd.condTemp', name='Condensation temperature', native_unit_of_measurement=UnitOfTemperature.CELSIUS, device_class=SensorDeviceClass.TEMPERATURE, state_class=SensorStateClass.MEASUREMENT, scale=0.01, entity_category=EntityCategory.DIAGNOSTIC, round_digits=3, **_OFF),
        D(key='pd.heatEnv', name='Return air temperature in condensation zone', native_unit_of_measurement=UnitOfTemperature.CELSIUS, device_class=SensorDeviceClass.TEMPERATURE, state_class=SensorStateClass.MEASUREMENT, scale=0.01, entity_category=EntityCategory.DIAGNOSTIC, round_digits=3, **_OFF),
        D(key='pd.coolEnv', name='Air outlet temperature', native_unit_of_measurement=UnitOfTemperature.CELSIUS, device_class=SensorDeviceClass.TEMPERATURE, state_class=SensorStateClass.MEASUREMENT, scale=0.01, entity_category=EntityCategory.DIAGNOSTIC, round_digits=3, **_OFF),
        D(key='pd.evapTemp', name='Evaporation temperature', native_unit_of_measurement=UnitOfTemperature.CELSIUS, device_class=SensorDeviceClass.TEMPERATURE, state_class=SensorStateClass.MEASUREMENT, scale=0.01, entity_category=EntityCategory.DIAGNOSTIC, round_digits=3, **_OFF),
        D(key='pd.motorOutTemp', name='Exhaust temperature', native_unit_of_measurement=UnitOfTemperature.CELSIUS, device_class=SensorDeviceClass.TEMPERATURE, state_class=SensorStateClass.MEASUREMENT, scale=0.01, entity_category=EntityCategory.DIAGNOSTIC, round_digits=3, **_OFF),
        D(key='pd.airInTemp', name='Evaporation zone return air temperature', native_unit_of_measurement=UnitOfTemperature.CELSIUS, device_class=SensorDeviceClass.TEMPERATURE, state_class=SensorStateClass.MEASUREMENT, scale=0.01, entity_category=EntityCategory.DIAGNOSTIC, round_digits=3, **_OFF),
        D(key='pd.coolTemp', name='Air outlet temperature (pd.coolTemp)', native_unit_of_measurement=UnitOfTemperature.CELSIUS, device_class=SensorDeviceClass.TEMPERATURE, state_class=SensorStateClass.MEASUREMENT, entity_category=EntityCategory.DIAGNOSTIC, round_digits=None, **_OFF),
        D(key='pd.psdrPower ', name='Power supply power', native_unit_of_measurement=UnitOfPower.WATT, device_class=SensorDeviceClass.POWER, state_class=SensorStateClass.MEASUREMENT, round_digits=None, **_OFF),
        D(key='pd.batPower ', name='Battery power', native_unit_of_measurement=UnitOfPower.WATT, device_class=SensorDeviceClass.POWER, state_class=SensorStateClass.MEASUREMENT, round_digits=None, **_OFF),
        D(key='power.batPwrOut', name='Battery output power', native_unit_of_measurement=UnitOfPower.WATT, device_class=SensorDeviceClass.POWER, state_class=SensorStateClass.MEASUREMENT, round_digits=None, **_OFF),
        D(key='power.acPwrI', name='AC input power', native_unit_of_measurement=UnitOfPower.WATT, device_class=SensorDeviceClass.POWER, state_class=SensorStateClass.MEASUREMENT, round_digits=None, **_OFF),
        D(key='power.mpptPwr ', name='PV input power', native_unit_of_measurement=UnitOfPower.WATT, device_class=SensorDeviceClass.POWER, state_class=SensorStateClass.MEASUREMENT, round_digits=None, **_OFF),
    )

from ..select import EcoFlowSelectDescription

SELECTS = (
    EcoFlowSelectDescription(
        key="temp_unit", name="Temperature Unit 🧪", icon="mdi:thermometer",
        state_key="pd.tempSys",
        options_map={"Celsius": 0, "Fahrenheit": 1},
        cmd_module=1, cmd_operate="tempSys", cmd_param_key="mode",
        entity_registry_enabled_default=False,
    ),
)
