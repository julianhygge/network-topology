"""Pydantic models for electrical appliance responses."""

from datetime import datetime
from typing import List

from pydantic import UUID4, BaseModel, Field


class AppliancesResponse(BaseModel):
    """Response model for a single electrical appliance."""

    id: int = Field(..., example="1")
    name: str = Field(..., example="Bulb")
    created_by: UUID4 = Field(..., example="74f5596d-1df2-45ff-834c-a0511674c57f")
    modified_by: UUID4 = Field(..., example="74f5596d-1df2-45ff-834c-a0511674c57f")
    created_on: datetime = Field(..., example="2024-05-07 12:40")
    modified_on: datetime = Field(..., example="2024-05-07 12:40")


class AppliancesListResponse(BaseModel):
    """Response model for a list of electrical appliances."""

    items: List[AppliancesResponse]
