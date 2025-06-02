"""
Pydantic models for simulation API responses.
"""

from uuid import UUID

from pydantic import BaseModel, Field


class EnergySummaryResponse(BaseModel):
    """
    Response model for energy summary, providing total imported and exported units.
    """

    total_imported_units: float = Field(
        ...,
        description="Total energy imported from the grid in kWh.",
        example=150.75,
    )
    total_exported_units: float = Field(
        ...,
        description="Total energy exported to the grid in kWh.",
        example=50.25,
    )

    class Config:
        """Pydantic model configuration."""

        orm_mode = True
        allow_population_by_field_name = True
        arbitrary_types_allowed = True
        json_encoders = {UUID: str}
