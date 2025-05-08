"""Pydantic models for updating load profiles and related entities."""

from datetime import datetime
from enum import Enum
from typing import Dict, List, Optional
from uuid import UUID

from pydantic import BaseModel, Field


class LoadProfileUpdateRequest(BaseModel):
    """Request model for updating an existing load profile."""

    active: Optional[bool] = Field(
        None,
        example=True,
        description="Indicates whether the load profile should be active or not.",
    )
    profile_name: Optional[str] = Field(
        None,
        min_length=1,
        max_length=50,
        example="Updated Residential Solar Profile",
        description="New profile name",
    )
    public: Optional[bool] = Field(
        None,
        example=True,
        description="Indicates whether the load profile is public or not.",
    )


class LoadProfileBuilderItemRequest(BaseModel):
    """Request model for a single item in the load profile builder update."""

    id: Optional[int] = Field(default=None, example=1)
    electrical_device_id: int = Field(..., example=1)
    rating_watts: int = Field(..., example=60)
    quantity: int = Field(..., example=5)
    hours: int = Field(..., example=4)


class LoadProfileBuilderItemsRequest(BaseModel):
    """Request model for updating items using the load profile builder."""

    items: List[LoadProfileBuilderItemRequest] = Field(
        ...,
        example=[
            {
                "id": 1,
                "electrical_device_id": 1,
                "rating_watts": 60,
                "quantity": 5,
                "hours": 4,
            },
            {
                "electrical_device_id": 2,
                "rating_watts": 75,
                "quantity": 3,
                "hours": 8,
            },
        ],
    )


class LoadGenerationType(str, Enum):
    """Enum defining the type of load generation (Monthly or Daily)."""

    MONTHLY = "Monthly"
    DAILY = "Daily"


class LoadGenerationEngineRequest(BaseModel):
    """Request model for the load generation engine."""

    type: LoadGenerationType = Field(
        ..., description="Type of load generation, either Monthly or Daily"
    )
    average_kwh: Optional[float] = Field(None, ge=0)
    average_monthly_bill: Optional[float] = Field(None, ge=0)
    max_demand_kw: Optional[float] = Field(None, ge=0)


class LoadGenerationEngineResponse(BaseModel):
    """Response model for the load generation engine."""

    user_id: UUID = Field(..., example="824960c0-974c-4c57-8803-85f5f407b304")
    profile_id: int = Field(..., example="1")
    type: LoadGenerationType
    average_kwh: Optional[float] = Field(None, ge=0)
    average_monthly_bill: Optional[float] = Field(None, ge=0)
    max_demand_kw: Optional[float] = Field(None, ge=0)
    created_on: datetime = Field(..., example="2024-05-07 12:40")
    modified_on: datetime = Field(..., example="2024-05-07 12:40")
    links: Dict[str, str] = Field(
        default={"self": "/v1/load_profiles/"},
        example={
            "self": "/v1/load_profiles/",
            "next": "/v1/load_profiles/?page=2",
        },
    )


class LoadPredefinedTemplateRequest(BaseModel):
    """Request model for applying a predefined template to a load profile."""

    template_id: int
