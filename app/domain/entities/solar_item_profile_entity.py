"""Solar item profile entity."""

from dataclasses import dataclass
from datetime import datetime
from uuid import UUID


@dataclass
class SolarItemProfileEntity:
    """Represents a solar item profile entity."""
    id: int
    user_id: UUID
    solar_profile_id: UUID
    production_kwh: float
    timestamp: datetime
    voltage_v: float
    current_amps: float