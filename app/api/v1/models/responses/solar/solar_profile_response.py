from pydantic import BaseModel, UUID4
from typing import Optional, List
from datetime import datetime
from decimal import Decimal

from app.api.v1.models.requests.solar.solar_profile_request import TiltType


class SolarProfileResponse(BaseModel):
    max_capacity_kw: Optional[Decimal] = None
    solar_available: bool
    house_id: UUID4
    installed_capacity_kw: Optional[Decimal]
    tilt_type: Optional[TiltType]
    years_since_installation: Optional[Decimal]
    available_space_sqft: Optional[Decimal]
    simulate_using_different_capacity: bool
    capacity_for_simulation_kw: Optional[Decimal]


class SolarProfileListResponse(BaseModel):
    items: List[SolarProfileResponse]
