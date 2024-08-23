from datetime import datetime
from pydantic import BaseModel, UUID4, Field
from typing import List, Optional

from app.data.schemas.enums.enums import NodeStatusEnum


class Node(BaseModel):
    id: UUID4 = Field(..., example="74f5596d-1df2-45ff-834c-a0511674c57f")
    type: str = Field(..., example="House")
    status: NodeStatusEnum = Field(..., example="complete")
    name: str = Field(..., example="House1")
    nomenclature: str = Field(..., example="T.1.1")
    children: Optional[List["Node"]] = None

    class Config:
        from_attributes = True


class SubstationTopology(BaseModel):
    substation_id: UUID4 = Field(..., example="74f5596d-1df2-45ff-834c-a0511674c57f")
    substation_name: str = Field(..., example="Substation1")
    locality_id: UUID4 = Field(..., example="74f5596d-1df2-45ff-834c-a0511674c57f")
    locality_name: str = Field(..., example="Shantipuram")
    nodes: List[Node]

    class Config:
        from_attributes = True


class SubstationResponseModel(BaseModel):
    id: UUID4 = Field(..., example="74f5596d-1df2-45ff-834c-a0511674c57f")
    locality: UUID4 = Field(..., example="74f5596d-1df2-45ff-834c-a0511674c57f")
    name: str = Field(..., example="Grid2")
    active: bool = Field(..., example="True")
    created_on: datetime = Field(..., example="2024-05-07 12:40")
    modified_by: Optional[UUID4] = Field(None, example="74f5596d-1df2-45ff-834c-a0511674c57f")
    modified_on: Optional[datetime] = Field(None, example="2024-05-07 12:40")


class SubstationResponseModelList(BaseModel):
    items: List[SubstationResponseModel]
