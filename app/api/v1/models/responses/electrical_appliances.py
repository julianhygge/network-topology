from pydantic import BaseModel, UUID4
from typing import List
from datetime import datetime


class AppliancesResponse(BaseModel):
    id: int
    name: str
    created_by: UUID4
    modified_by: UUID4
    created_on: datetime
    modified_on: datetime


class AppliancesListResponse(BaseModel):
    items: List[AppliancesResponse]
