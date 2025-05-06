"""Domain entity for Substation."""

import uuid
from dataclasses import dataclass, field
from datetime import datetime
from typing import Optional

# Import Locality directly as it's not a circular dependency here
from app.domain.entities.locality import Locality


@dataclass
class Substation:
    """Represents a substation in the domain."""

    active: bool
    locality_id: uuid.UUID
    name: str
    id: uuid.UUID = field(default_factory=uuid.uuid4)
    created_by: Optional[uuid.UUID] = None
    created_date: Optional[datetime] = None
    updated_by: Optional[uuid.UUID] = None
    updated_date: Optional[datetime] = None
    locality: Optional[Locality] = None
