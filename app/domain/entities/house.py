"""Domain entity for House."""

from __future__ import annotations  # Ensure all type hints are strings

import uuid
from dataclasses import dataclass, field
from datetime import datetime
from decimal import Decimal
from typing import TYPE_CHECKING, Optional

if TYPE_CHECKING:
    from app.domain.entities.node import Node


@dataclass
class House:
    """Represents a house in the domain."""

    active: bool
    id: uuid.UUID = field(default_factory=uuid.uuid4)
    node_id: Optional[uuid.UUID] = None
    load_profile: Optional[str] = None
    has_solar: bool = False
    solar_kw: Optional[Decimal] = None
    house_type: Optional[str] = None
    connection_kw: Optional[Decimal] = None
    has_battery: bool = False
    battery_type: Optional[str] = None
    battery_peak_charging_rate: Optional[Decimal] = None
    battery_peak_discharging_rate: Optional[Decimal] = None
    battery_total_kwh: Optional[Decimal] = None
    created_by: Optional[uuid.UUID] = None
    created_date: Optional[datetime] = None
    updated_by: Optional[uuid.UUID] = None
    updated_date: Optional[datetime] = None
    node: Optional["Node"] = None
