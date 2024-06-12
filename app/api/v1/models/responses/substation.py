from datetime import datetime
from pydantic import BaseModel, UUID4
from typing import List, Optional


class HouseDetailResponseModel(BaseModel):
    id: UUID4
    is_complete: bool


class TransformerDetailResponseModel(BaseModel):
    id: UUID4
    is_complete: bool
    houses_details: List[HouseDetailResponseModel]


class SubstationTopologyResponseModel(BaseModel):
    substation_id: UUID4
    locality_id: UUID4
    transformers: List[TransformerDetailResponseModel]


class SubstationResponseModel(BaseModel):
    id: UUID4
    locality: UUID4
    name: str
    active: bool
    created_on: datetime
    modified_by: Optional[str] = None
    modified_on: Optional[datetime] = None
