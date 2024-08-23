from pydantic import BaseModel, UUID4, Field
from typing import List
from datetime import datetime


class AppliancesResponse(BaseModel):
    id: int = Field(..., example="1")
    name: str = Field(..., example="Bulb")
    created_by: UUID4 = Field(..., example="74f5596d-1df2-45ff-834c-a0511674c57f")
    modified_by: UUID4 = Field(..., example="74f5596d-1df2-45ff-834c-a0511674c57f")
    created_on: datetime = Field(..., example="2024-05-07 12:40")
    modified_on: datetime = Field(..., example="2024-05-07 12:40")


class AppliancesListResponse(BaseModel):
    items: List[AppliancesResponse]
