"""Pydantic models for transformer and house node requests and responses."""

from decimal import Decimal
from enum import Enum
from typing import Optional

from pydantic import BaseModel, UUID4, Field

from app.data.schemas.enums.enums import NodeStatusEnum


class BatteryEnum(str, Enum):
    """Enum defining battery types."""
    LITHIUM = "Lithium-ion"
    LEAD_ACID = "Lead-acid"
    NICKEL_METAL = "Nickel-Metal"


class HouseUpdateRequestModel(BaseModel):
    """Request model for updating house node details."""
    load_profile: Optional[str] = Field(None, example="")
    has_solar: Optional[bool] = Field(None, example="True")
    solar_kw: Optional[Decimal] = Field(None, example="2.9")
    house_type: Optional[str] = Field(None, example="")
    connection_kw: Optional[Decimal] = Field(None, example="5.9")
    battery_type: Optional[BatteryEnum] = Field(None, example="Lithium-ion")
    has_battery: Optional[bool] = Field(None, example="True")
    voluntary_storage: Optional[bool] = Field(None, example="False")
    battery_peak_charging_rate: Optional[Decimal] = Field(None, example="5.9")
    battery_peak_discharging_rate: Optional[Decimal] = Field(None, example="3.8")
    battery_total_kwh: Optional[Decimal] = Field(None, example="5.6")


class HouseResponseModel(BaseModel):
    """Response model for house node details."""
    id: UUID4 = Field(..., example="824960c0-974c-4c57-8803-85f5f407b304")
    status: NodeStatusEnum = Field(..., example="complete")
    load_profile: Optional[str] = Field(None, example="")
    has_solar: Optional[bool] = Field(None, example="True")
    solar_kw: Optional[Decimal] = Field(None, example="7.9")
    house_type: Optional[str] = Field(None, example="")
    connection_kw: Optional[Decimal] = Field(None, example="6.5")
    battery_type: Optional[BatteryEnum] = Field(None, example="Lithium-ion")
    has_battery: Optional[bool] = Field(None, example="True")
    voluntary_storage: Optional[bool] = Field(None, example="True")
    battery_peak_charging_rate: Optional[Decimal] = Field(None, example="2.0")
    battery_peak_discharging_rate: Optional[Decimal] = Field(None, example="2.0")
    battery_total_kwh: Optional[Decimal] = Field(None, example="130.5")


class TransformerUpdateRequestModel(BaseModel):
    """Request model for updating transformer node details."""
    max_capacity_kw: Optional[Decimal] = Field(None, example="28.9")
    allow_export: bool = Field(..., example="True")
    name: Optional[str] = Field(None, example="Shantipuram")
    backward_efficiency: Optional[Decimal] = Field(None, example="5.4")
    primary_ampacity: Optional[Decimal] = Field(None, example="5.3")
    secondary_ampacity: Optional[Decimal] = Field(None, example="50.7")
    years_of_service: Optional[int] = Field(None, example="5")
    forward_efficiency: Optional[Decimal] = Field(None, example="34.6")
    digital_twin_model: Optional[bool] = Field(None, example="True")


class TransformerResponseModel(BaseModel):
    """Response model for transformer node details."""
    id: UUID4 = Field(..., example="824960c0-974c-4c57-8803-85f5f407b304")
    status: NodeStatusEnum = Field(..., example="complete")
    max_capacity_kw: Optional[Decimal] = Field(None, example="45.7")
    active: bool = Field(..., example="True")
    allow_export: Optional[bool] = Field(None, example="True")
    name: Optional[str] = Field(None, example="Transformer1")
    backward_efficiency: Optional[Decimal] = Field(None, example="45.6")
    primary_ampacity: Optional[Decimal] = Field(None, example="25.6")
    secondary_ampacity: Optional[Decimal] = Field(None, example="34.6")
    years_of_service: Optional[int] = Field(None, example="6")
    forward_efficiency: Optional[Decimal] = Field(None, example="45.6")
    digital_twin_model: Optional[bool] = Field(None, example="True")
