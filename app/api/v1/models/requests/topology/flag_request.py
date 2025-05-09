"""Pydantic models for Flag requests."""

from typing import Optional

from pydantic import BaseModel, Field


class FlagBase(BaseModel):
    """Base model for flag attributes."""

    flag_type: str = Field(..., description="The type of the flag.")
    flag_value: str = Field(..., description="The value of the flag.")
    active: Optional[bool] = Field(
        True, description="Indicates if the flag is active."
    )

    class Config:
        """Pydantic model configuration."""

        from_attributes = True
        json_schema_extra = {
            "example": {
                "flag_type": "Maintenance",
                "flag_value": "Scheduled",
                "active": True,
            }
        }


class FlagCreateRequest(FlagBase):
    """Request model for creating a new flag."""


class FlagUpdateRequest(FlagBase):
    """Request model for updating an existing flag."""

    # All fields are optional for update
    flag_type: Optional[str] = Field(None, description="The type of the flag.")
    flag_value: Optional[str] = Field(
        None, description="The value of the flag."
    )

    class Config:
        """Pydantic model configuration."""

        from_attributes = True
