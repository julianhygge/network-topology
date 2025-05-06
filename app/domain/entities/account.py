"""Domain entity for Account."""

import uuid
from dataclasses import dataclass, field
from datetime import datetime
from typing import Optional


@dataclass
class Account:
    """Represents an account in the domain."""

    active: bool
    validity_start: datetime
    validity_end: datetime
    record_id: uuid.UUID
    id: uuid.UUID = field(default_factory=uuid.uuid4)
    alias_name: Optional[str] = None
    type: Optional[str] = None
    phone_number: str = "8429020287"
    created_by: Optional[uuid.UUID] = None
    created_date: Optional[datetime] = None
    updated_by: Optional[uuid.UUID] = None
    updated_date: Optional[datetime] = None
