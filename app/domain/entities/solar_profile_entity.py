"""Solar profile entity."""

from dataclasses import dataclass
from datetime import datetime
from uuid import UUID


@dataclass
class SolarProfileEntity:
    """Represents a solar profile entity."""

    id: UUID
    active: bool
    solar_available: bool | None
    house_id: UUID
    installed_capacity_kw: float
    tilt_type: str
    years_since_installation: float | None
    simulate_using_different_capacity: bool | None
    capacity_for_simulation_kw: float
    available_space_sqft: float | None
    simulated_available_space_sqft: float | None
    created_at: datetime
    updated_at: datetime
    created_by: UUID
    updated_by: UUID
    imported_units: list[float] | None = None
    exported_units: list[float] | None = None
    net_usage: list[float] | None = None
