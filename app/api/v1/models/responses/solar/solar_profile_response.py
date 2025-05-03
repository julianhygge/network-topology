"""Pydantic models for solar profile responses."""

from decimal import Decimal
from typing import List, Optional

from pydantic import UUID4, BaseModel

from app.api.v1.models.requests.solar.solar_profile_request import TiltType


class SolarProfileResponse(BaseModel):
    """Response model for a single solar profile."""

    solar_available: bool
    house_id: UUID4
    installed_capacity_kw: Optional[Decimal]
    tilt_type: TiltType
    years_since_installation: Optional[Decimal]
    available_space_sqft: Optional[Decimal]
    simulated_available_space_sqft: Optional[Decimal]
    simulate_using_different_capacity: bool
    capacity_for_simulation_kw: Optional[Decimal]


class SolarProfileListResponse(BaseModel):
    """Response model for a list of solar profiles."""

    items: List[SolarProfileResponse]
