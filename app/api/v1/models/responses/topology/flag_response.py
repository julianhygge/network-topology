"""Pydantic models for Flag responses."""

from datetime import datetime
from typing import Optional
from uuid import UUID

from pydantic import BaseModel, Field, UUID4


class FlagResponse(BaseModel):
    """Response model for a flag."""

    id: int = Field(..., description="The unique identifier of the flag.")
    created_on: datetime = Field(
        ..., description="Timestamp of when the flag was created."
    )
    modified_on: datetime = Field(
        ..., description="Timestamp of when the flag was last modified."
    )
    created_by: Optional[UUID4] = Field(
        None, description="ID of the user who created the flag."
    )
    modified_by: Optional[UUID4] = Field(
        None, description="ID of the user who last modified the flag."
    )
    active: bool = Field(..., description="Indicates if the flag is active.")
    house_id: UUID4 = Field(
        ...,
        alias="house",
        description="The ID of the house this flag belongs to.",
    )
    flag_type: str = Field(..., description="The type of the flag.")
    flag_value: str = Field(..., description="The value of the flag.")

    class Config:
        """Pydantic model configuration."""

        from_attributes = True
        populate_by_name = True
        json_encoders = {
            UUID: str,
            datetime: lambda dt: dt.isoformat(),
        }
        json_schema_extra = {
            "example": {
                "id": 5,
                "created_on": "2025-05-08T10:00:00Z",
                "modified_on": "2025-05-08T10:00:00Z",
                "created_by": "b2c3d4e5-f6a7-8901-2345-67890abcdef0",
                "modified_by": "c3d4e5f6-a7b8-9012-3456-7890abcdef01",
                "active": True,
                "house_id": "7ecae55e-92dd-427e-a2d6-4f3bed16b0d2",
                "flag_type": "Test",
                "flag_value": "Hospital",
            }
        }
