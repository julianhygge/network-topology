"""Domain entity for Node."""

from __future__ import annotations  # Ensure all type hints are strings

import uuid
from dataclasses import dataclass, field
from datetime import datetime
from typing import TYPE_CHECKING, List, Optional

# TYPE_CHECKING block is still good practice for clarity and for other tools
if TYPE_CHECKING:
    from app.domain.entities.house import House
    from app.domain.entities.substation import Substation
    from app.domain.entities.transformer import Transformer


@dataclass
class Node:
    """Represents a node in the topology."""

    active: bool
    name: str
    node_type: str  # 'substation', 'transformer', or 'house'
    id: uuid.UUID = field(default_factory=uuid.uuid4)
    parent_id: Optional[uuid.UUID] = None
    nomenclature: Optional[str] = None
    substation_id: Optional[uuid.UUID] = None
    created_by: Optional[uuid.UUID] = None
    created_date: Optional[datetime] = None
    updated_by: Optional[uuid.UUID] = None
    updated_date: Optional[datetime] = None
    parent: Optional["Node"] = None
    children: List["Node"] = field(default_factory=list)

    substation: Optional["Substation"] = None
    transformers: List["Transformer"] = field(default_factory=list)
    houses: List["House"] = field(default_factory=list)
