"""Domain entity for Transformer."""

from __future__ import annotations  # Ensure all type hints are strings

import uuid
from dataclasses import dataclass, field
from datetime import datetime
from decimal import Decimal
from typing import TYPE_CHECKING, Optional

if TYPE_CHECKING:
    from app.domain.entities.node import Node


@dataclass
class Transformer:
    """Represents a transformer in the domain."""

    active: bool
    max_capacity_kw: Decimal
    id: uuid.UUID = field(default_factory=uuid.uuid4)
    node_id: Optional[uuid.UUID] = None
    allow_export: bool = False
    name: Optional[str] = None
    backward_efficiency: Optional[Decimal] = None
    primary_ampacity: Optional[Decimal] = None
    secondary_ampacity: Optional[Decimal] = None
    years_of_service: Optional[int] = None
    forward_efficiency: Optional[Decimal] = None
    digital_twin_model: bool = False
    created_by: Optional[uuid.UUID] = None
    created_date: Optional[datetime] = None
    updated_by: Optional[uuid.UUID] = None
    updated_date: Optional[datetime] = None
    node: Optional["Node"] = None
