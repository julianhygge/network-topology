"""Domain entity for Locality."""

import uuid
from dataclasses import dataclass, field
from datetime import datetime
from typing import Optional


@dataclass
class Locality:
    """Represents a locality in the domain."""

    active: bool
    name: str
    id: uuid.UUID = field(default_factory=uuid.uuid4)
    created_by: Optional[uuid.UUID] = None
    created_date: Optional[datetime] = None
    updated_by: Optional[uuid.UUID] = None
    updated_date: Optional[datetime] = None
