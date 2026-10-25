"""Extra entities for the Delta Pro Ultra (v0.4.0), from the EcoFlow device documentation.

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

MODEL = "Delta Pro Ultra"
_OFF = {"entity_registry_enabled_default": False}
_CHG_STATE = ((0, "unused"), (1, "charging"), (2, "discharging"))

SENSORS = (
        D(key='hs_yj751_pd_appshow_addr.fullCombo', name='Wireless 4G Data Max', entity_category=EntityCategory.DIAGNOSTIC, round_digits=None, **_OFF),
        D(key='hs_yj751_pd_appshow_addr.remainCombo', name='Wireless 4G Data Remaining', entity_category=EntityCategory.DIAGNOSTIC, round_digits=None, **_OFF),
        D(key='hs_yj751_pd_appshow_addr.wireless4gCon', name='Wireless 4G Resgistered', entity_category=EntityCategory.DIAGNOSTIC, round_digits=None, **_OFF),
        D(key='hs_yj751_pd_appshow_addr.wirlesss4gErrCode', name='Wireless 4G Error Code', entity_category=EntityCategory.DIAGNOSTIC, round_digits=None, **_OFF),
        D(key='hs_yj751_pd_appshow_addr.simIccid', name='Wireless 4G SIM ID', entity_category=EntityCategory.DIAGNOSTIC, round_digits=None, **_OFF),
        D(key='hs_yj751_pd_appshow_addr.wireless4GSta', name='Internet Connection Type', entity_category=EntityCategory.DIAGNOSTIC, round_digits=None, **_OFF),
        D(key='hs_yj751_pd_backend_addr.outAc5p8Amp', name='Power I/O Port Output Current', native_unit_of_measurement=UnitOfElectricCurrent.AMPERE, device_class=SensorDeviceClass.CURRENT, state_class=SensorStateClass.MEASUREMENT, round_digits=None, **_OFF),
        D(key='hs_yj751_pd_backend_addr.outAc5p8Vol', name='Power I/O Port Output Voltage', native_unit_of_measurement=UnitOfElectricPotential.VOLT, device_class=SensorDeviceClass.VOLTAGE, state_class=SensorStateClass.MEASUREMENT, round_digits=None, **_OFF),
        D(key='hs_yj751_pd_appshow_addr.access5p8InType', name='Power I/O Port Input Type', entity_category=EntityCategory.DIAGNOSTIC, round_digits=None, **_OFF),
        D(key='hs_yj751_pd_appshow_addr.wattsInSum', name='Total In Power', native_unit_of_measurement=UnitOfPower.WATT, device_class=SensorDeviceClass.POWER, state_class=SensorStateClass.MEASUREMENT, icon='mdi:transmission-tower-import', round_digits=None, **_OFF),
        D(key='hs_yj751_pd_appshow_addr.wattsOutSum', name='Total Out Power', native_unit_of_measurement=UnitOfPower.WATT, device_class=SensorDeviceClass.POWER, state_class=SensorStateClass.MEASUREMENT, icon='mdi:transmission-tower-export', round_digits=None, **_OFF),
    )
