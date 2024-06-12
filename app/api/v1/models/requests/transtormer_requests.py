from decimal import Decimal

from pydantic import BaseModel, UUID4
from typing import Optional, List
from datetime import datetime


class HouseUpdateRequestModel(BaseModel):
    is_complete: bool


class HouseResponseModel(BaseModel):
    id: UUID4
    is_complete: bool


class TransformerUpdateRequestModel(BaseModel):
    is_complete: bool
    houses_details: Optional[List[HouseResponseModel]]  # Optional list of houses to update


class TransformerResponseModel(BaseModel):
    id: UUID4
    is_complete: bool
    max_capacity: Decimal
    active: bool
    export_efficiency: bool
    allow_export: bool

