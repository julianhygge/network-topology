from decimal import Decimal
from enum import Enum
from pydantic import BaseModel, UUID4, Field, model_validator
from typing import Optional


class TiltType(str, Enum):
    fixed = 'fixed'
    tracking = 'tracking'


class SolarProfileRequestModel(BaseModel):
    solar_available: bool = Field(..., example=False)
    house_id: UUID4 = Field(..., example="824960c0-974c-4c57-8803-85f5f407b304")
    installed_capacity_kw: Optional[Decimal] = Field(None, example="65.0", ge=0)
    tilt_type: Optional[TiltType] = Field(..., example='fixed')
    years_since_installation: Optional[Decimal] = Field(None, example="10", ge=0)
    available_space_sqft: Optional[Decimal] = Field(None, example="10", ge=0)
    simulate_using_different_capacity: bool
    capacity_for_simulation_kw: Optional[Decimal] = Field(None, example="65.0", ge=0)

    @model_validator(mode="before")
    def validate_solar_profile(cls, values):
        solar_available = values.get('solar_available')
        simulate_using_different_capacity = values.get('simulate_using_different_capacity')

        if values.get('tilt_type') not in TiltType:
            raise ValueError("tilt_type must be either 'fixed' or 'tracking' ")

        if solar_available:
            if values.get('installed_capacity_kw') is None:
                raise ValueError("installed_capacity_kw must not be null when solar_available is True")

            if values.get('years_since_installation') is None or values.get('years_since_installation') < 0:
                raise ValueError("years_since_installation must be a positive number when solar_available is True")
        else:
            if values.get('available_space_sqft') is None:
                raise ValueError("available_space_sqft must not be null when solar_available is False")

        if simulate_using_different_capacity:
            if values.get('capacity_for_simulation_kw') is None:
                raise ValueError(
                    "capacity_for_simulation_kw must not be null when simulate_using_different_capacity is True")

        return values


class SolarProfileUpdateModel(BaseModel):
    solar_available: Optional[bool] = None
    installed_capacity_kw: Optional[Decimal] = Field(None, example="65.0", ge=0)
    tilt_type: Optional[TiltType] = Field(None, example='fixed')
    years_since_installation: Optional[Decimal] = Field(None, example="10", ge=0)
    available_space_sqft: Optional[Decimal] = Field(None, example="10", ge=0)
    simulate_using_different_capacity: Optional[bool] = None
    capacity_for_simulation_kw: Optional[Decimal] = Field(None, example="65.0", ge=0)

    @model_validator(mode='before')
    def validate_update_solar_profile(cls, values):
        solar_available = values.get('solar_available')
        if solar_available:
            if values.get('installed_capacity_kw') is None:
                raise ValueError("installed_capacity_kw must not be null when solar_available is True")

            if values.get('years_since_installation') is None or values.get('years_since_installation') < 0:
                raise ValueError("years_since_installation must be a positive number when solar_available is True")
