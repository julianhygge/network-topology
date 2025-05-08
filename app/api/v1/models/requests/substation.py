"""Pydantic models for substation requests."""

from enum import Enum
from typing import List, Optional

from pydantic import UUID4, BaseModel, Field, constr


class ActionEnum(str, Enum):
    """Enum defining actions for topology nodes (add, delete, update)."""

    ADD = "add"
    DELETE = "delete"
    UPDATE = "update"


class NodeType(str, Enum):
    """Enum defining the type of topology node (transformer, house)."""

    TRANSFORMER = "transformer"
    HOUSE = "house"


class NodeDetailRequestModel(BaseModel):
    """Request model for details of a single node in the topology."""

    id: Optional[UUID4] = Field(
        None, example="824960c0-974c-4c57-8803-85f5f407b304"
    )
    action: Optional[ActionEnum] = Field(ActionEnum.UPDATE, example="update")
    type: Optional[NodeType] = Field(None, example="transformer")
    name: Optional[constr(max_length=12)] = Field(None, example="John's house")
    children: Optional[List["NodeDetailRequestModel"]] = Field(
        None, example=[]
    )


class SubstationTopologyRequestModel(BaseModel):
    """Request model for updating the topology of a substation."""

    nodes: List[NodeDetailRequestModel]


class SubstationRequestModel(BaseModel):
    """Request model for creating or updating a single substation."""

    locality_id: UUID4 = Field(
        ..., example="94522a0a-c8f1-40f8-a2e5-9aed2dc55555"
    )
    name: str = Field(..., example="Substation number 1")


class SubstationsRequestModel(BaseModel):
    """Request model for creating multiple substations within a locality."""

    locality_id: UUID4 = Field(
        ..., example="94522a0a-c8f1-40f8-a2e5-9aed2dc55555"
    )
    number_of_substations: int = Field(..., example="2")
