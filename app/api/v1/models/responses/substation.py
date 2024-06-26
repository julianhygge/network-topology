from datetime import datetime
from pydantic import BaseModel, UUID4
from typing import List, Optional


class Node(BaseModel):
    id: UUID4
    type: str
    is_complete: bool
    children: Optional[List['Node']] = None

    class Config:
        from_attributes = True


class SubstationTopology(BaseModel):
    substation_id: UUID4
    substation_name: str
    locality_id: UUID4
    locality_name: str
    nodes: List[Node]

    class Config:
        from_attributes = True


class SubstationResponseModel(BaseModel):
    id: UUID4
    locality: UUID4
    name: str
    active: bool
    created_on: datetime
    modified_by: Optional[UUID4] = None
    modified_on: Optional[datetime] = None


class SubstationResponseModelList(BaseModel):
    items: List[SubstationResponseModel]
