"""Pydantic models for electrical appliance requests."""

from pydantic import BaseModel, Field


class AppliancesRequest(BaseModel):
    """Request model for creating a new electrical appliance."""
    name: str = Field(..., example='bulb')


class ApplianceUpdateRequest(BaseModel):
    """Request model for updating an existing electrical appliance."""
    name: str = Field(..., example='bulb')
    appliance_id: int = Field(..., example=1)
