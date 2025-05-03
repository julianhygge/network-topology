"""Pydantic models for solar profile requests."""

from decimal import Decimal
from enum import Enum
from typing import Any, Dict, Optional

from pydantic import UUID4, BaseModel, Field, model_validator


class TiltType(str, Enum):
    """Enum defining the type of solar panel tilt."""
    FIXED = 'fixed'
    TRACKING = 'tracking'


class SolarProfileRequestModel(BaseModel):
    """Request model for creating a new solar profile."""
    solar_available: bool = Field(..., example=False)
    house_id: UUID4 = Field(..., example="824960c0-974c-4c57-8803-85f5f407b304")
    installed_capacity_kw: Optional[Decimal] = Field(None, example="65.0", ge=0)
    tilt_type: TiltType = Field(..., example='fixed')
    years_since_installation: Optional[Decimal] = Field(None, example="10", ge=0)
    available_space_sqft: Optional[Decimal] = Field(None, example="10", ge=0)
    simulated_available_space_sqft: Optional[Decimal] = Field(
        None, example="10", ge=0
    )
    simulate_using_different_capacity: bool
    capacity_for_simulation_kw: Optional[Decimal] = Field(
        None, example="65.0", ge=0
    )

    @model_validator(mode="before")
    @classmethod
    def validate_solar_profile(cls, values: Dict[str, Any]) -> Dict[str, Any]:
        """Validate solar profile data consistency."""
        # Convert string representations of Decimals if necessary
        decimal_fields = [
            'installed_capacity_kw', 'years_since_installation',
            'capacity_for_simulation_kw', 'available_space_sqft',
            'simulated_available_space_sqft'
        ]
        for field in decimal_fields:
            if field in values and isinstance(values[field], str):
                values[field] = Decimal(values[field])

        solar_available = values.get('solar_available')
        simulate_using_different_capacity = values.get(
            'simulate_using_different_capacity'
        )

        if values.get('tilt_type') not in [t.value for t in TiltType]:
            raise ValueError("tilt_type must be either 'fixed' or 'tracking'")

        if solar_available:
            if values.get('installed_capacity_kw') is None:
                raise ValueError(
                    "installed_capacity_kw must not be null when "
                    "solar_available is True"
                )
            if (values.get('years_since_installation') is None or
                    values.get('years_since_installation', 0) < 0):
                raise ValueError(
                    "years_since_installation must be a positive number when "
                    "solar_available is True"
                )
        else:
            if values.get('available_space_sqft') is None:
                raise ValueError(
                    "available_space_sqft must not be null when "
                    "solar_available is False"
                )

        if simulate_using_different_capacity:
            if values.get('capacity_for_simulation_kw') is None:
                raise ValueError(
                    "capacity_for_simulation_kw must not be null when "
                    "simulate_using_different_capacity is True"
                )

        return values


class SolarProfileUpdateModel(BaseModel):
    """Request model for updating an existing solar profile."""
    solar_available: Optional[bool] = None
    installed_capacity_kw: Optional[Decimal] = Field(None, example="65.0", ge=0)
    tilt_type: Optional[TiltType] = Field(None, example='fixed')
    years_since_installation: Optional[Decimal] = Field(None, example="10", ge=0)
    available_space_sqft: Optional[Decimal] = Field(None, example="10", ge=0)
    simulate_using_different_capacity: Optional[bool] = None
    capacity_for_simulation_kw: Optional[Decimal] = Field(
        None, example="65.0", ge=0
    )

    @model_validator(mode='before')
    @classmethod
    def validate_update_solar_profile(cls, values: Dict[str, Any]) -> Dict[str, Any]:
        """Validate solar profile update data consistency."""
        solar_available = values.get('solar_available')
        if solar_available:
            if values.get('installed_capacity_kw') is None:
                raise ValueError(
                    "installed_capacity_kw must not be null when "
                    "solar_available is True"
                )
            if (values.get('years_since_installation') is None or
                    values.get('years_since_installation', 0) < 0):
                raise ValueError(
                    "years_since_installation must be a positive number when "
                    "solar_available is True"
                )
