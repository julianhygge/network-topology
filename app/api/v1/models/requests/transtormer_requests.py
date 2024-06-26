from decimal import Decimal
from enum import Enum
from pydantic import BaseModel, UUID4
from typing import Optional, List


class BatteryEnum(str, Enum):
    Lithium = "Lithium-ion"
    LeadAcid = "Lead-acid"
    NickelMetal = "Nickel-Metal"


class HouseUpdateRequestModel(BaseModel):
    load_profile: Optional[str] = None
    has_solar: Optional[bool] = None
    solar_kw: Optional[Decimal] = None
    house_type: Optional[str] = None
    connection_kw: Optional[Decimal] = None
    battery_type: Optional[BatteryEnum] = None
    has_battery: Optional[bool] = None
    voluntary_storage: Optional[bool] = None
    battery_peak_charging_rate: Optional[Decimal] = None
    battery_peak_discharging_rate: Optional[Decimal] = None
    battery_total_kwh: Optional[Decimal] = None


class HouseResponseModel(BaseModel):
    id: UUID4
    is_complete: bool
    load_profile: Optional[str] = None
    has_solar: Optional[bool] = None
    solar_kw: Optional[Decimal] = None
    house_type: Optional[str] = None
    connection_kw: Optional[Decimal] = None
    battery_type: Optional[BatteryEnum] = None
    has_battery: Optional[bool] = None
    voluntary_storage: Optional[bool] = None
    battery_peak_charging_rate: Optional[Decimal] = None
    battery_peak_discharging_rate: Optional[Decimal] = None
    battery_total_kwh: Optional[Decimal] = None


class TransformerUpdateRequestModel(BaseModel):
    max_capacity_kw: Decimal
    export_efficiency: Decimal
    allow_export: bool


class TransformerResponseModel(BaseModel):
    id: UUID4
    is_complete: bool
    max_capacity_kw: Optional[Decimal] = None
    active: bool
    export_efficiency: Optional[Decimal] = None
    allow_export: Optional[bool] = None
