from enum import Enum
from typing import List, Optional
from pydantic import BaseModel, UUID4, Field


class ActionEnum(str, Enum):
    add = "add"
    delete = "delete"
    update = "update"


class NodeType(str, Enum):
    transformer = "transformer"
    house = "house"


class NodeDetailRequestModel(BaseModel):
    id: Optional[UUID4] = Field(None, example="824960c0-974c-4c57-8803-85f5f407b304")
    action: Optional[ActionEnum] = Field('update', example="update")
    type: Optional[NodeType] = Field(None, example="transformer")
    children: Optional[List['NodeDetailRequestModel']] = Field(None, example=[])


class SubstationTopologyRequestModel(BaseModel):
    nodes: List[NodeDetailRequestModel]


class SubstationRequestModel(BaseModel):
    locality_id: UUID4 = Field(..., example="94522a0a-c8f1-40f8-a2e5-9aed2dc55555")
    name: str = Field(..., example="Substation number 1")


class SubstationsRequestModel(BaseModel):
    locality_id: UUID4 = Field(..., example="94522a0a-c8f1-40f8-a2e5-9aed2dc55555")
    number_of_substations: int = Field(..., example="2")
