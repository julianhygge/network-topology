"""Pydantic models for solar profile responses."""
from datetime import datetime
from decimal import Decimal
from typing import List, Optional, Union

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

class SolarInstallationResponse(BaseModel):
    site_id: int
    name: Optional[str]
    status: Optional[str]
    peak_power: Optional[float]
    type: Optional[str]
    zip_code: Optional[str]
    country: Optional[str]
    address: Optional[str]
    state: Optional[str]
    city: Optional[str]
    installation_date: Optional[str]
    last_reporting_time: Optional[str]
    location: Optional[str]
    secondary_address: Optional[str]
    uploaded_on: Optional[datetime]
    profile_updated_on: Optional[datetime]
    updated_on: Optional[datetime]
    has_csv: Optional[bool]

class SolarInstallationListResponse(BaseModel):
    items: List[SolarInstallationResponse]
    total_page: int
    total_items: int
    current_page: int