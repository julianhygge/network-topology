"""Pydantic models for load profile responses."""

from datetime import datetime
from decimal import Decimal
from typing import Dict, List, Optional
from uuid import UUID

from pydantic import UUID4, BaseModel, Field


class LoadProfileResponse(BaseModel):
    """Response model for a single load profile."""

    links: Dict[str, str] = Field(
        default={"self": "/v1/load_profiles/"},
        example={
            "self": "/v1/load_profiles/",
            "next": "/v1/load_profiles/?page=2",
        },
    )
    house_id: UUID = Field(
        ...,
        example="123e4567-e89b-12d3-a456-426614174000",
        description="The house id requested",
    )
    profile_id: int = Field(
        ..., example=1, description="The unique ID of the load profile."
    )
    active: bool = Field(
        ...,
        example=True,
        description="Indicates whether the load profile is active or not.",
    )
    profile_name: str = Field(
        ...,
        example="Residential Solar Profile",
        description="The profile name.",
    )
    user_id: UUID4 = Field(
        ...,
        example="123e4567-e89b-12d3-a456-426614174000",
        description="The ID of the user associated with this profile.",
    )
    user: str = Field(..., example="User 12", description="User name")
    file_name: Optional[str] = Field(
        None,
        example="load_profile_user.csv",
        description="Profile user load file name",
    )
    created_on: datetime = Field(
        ...,
        example="2023-01-01T12:00:00Z",
        description="UTC timestamp when the profile was created.",
    )
    modified_on: datetime = Field(
        ...,
        example="2023-01-02T12:00:00Z",
        description="UTC timestamp when the profile was last modified.",
    )

    source: str = Field(
        ..., example="Template", description="Source of the load profile"
    )

    class Config:
        """Pydantic configuration."""

        from_attributes = True


class LoadProfilesListResponse(BaseModel):
    """Response model for a list of load profiles."""

    items: List[LoadProfileResponse]


class UserResponse(BaseModel):
    """Simplified user response containing only the ID."""

    id: UUID = Field(..., example="94522a0a-c8f1-40f8-a2e5-9aed2dc00001")


class LoadProfilesResponse(BaseModel):
    """Simplified load profile response containing only the ID."""

    id: int = Field(..., example=88)


class ElectricalAppliancesResponse(BaseModel):
    """Simplified electrical appliance response containing only the ID."""

    id: int = Field(..., example=1)


class LoadProfileBuilderItemResponse(BaseModel):
    """Response model for a single item within the load profile builder."""

    id: int = Field(..., example=2)
    created_on: datetime = Field(..., example="2024-07-31T14:51:46.964639")
    modified_on: datetime = Field(..., example="2024-07-31T14:51:46.964639")
    created_by: UUID = Field(
        ..., example="94522a0a-c8f1-40f8-a2e5-9aed2dc00001"
    )
    profile_id: int = Field(..., example=88)
    electrical_device_id: int = Field(..., example=1)
    rating_watts: int = Field(..., example=50)
    quantity: int = Field(..., example=5)
    hours: int = Field(..., example=4)


class LoadProfileBuilderItemsResponse(BaseModel):
    """Response model for a list of items from the load profile builder."""

    message: str = Field(..., example="Items saved successfully")
    links: Dict[str, str] = Field(
        default={"self": "/v1/load_profiles/"},
        example={
            "self": "/v1/load_profiles/",
            "next": "/v1/load_profiles/?page=2",
        },
    )
    profile_id: int
    items: List[LoadProfileBuilderItemResponse] = Field(
        ...,
        example=[
            {
                "id": 2,
                "created_on": "2024-07-31T14:51:46.964639",
                "modified_on": "2024-07-31T14:51:46.964639",
                "created_by": "94522a0a-c8f1-40f8-a2e5-9aed2dc00001",
                "profile_id": 88,
                "electrical_device_id": 1,
                "rating_watts": 50,
                "quantity": 5,
                "hours": 4,
            },
            {
                "id": 3,
                "created_on": "2024-07-31T14:51:46.964639",
                "modified_on": "2024-07-31T14:51:46.964639",
                "created_by": "94522a0a-c8f1-40f8-a2e5-9aed2dc00001",
                "profile_id": 88,
                "electrical_device_id": 2,
                "rating_watts": 75,
                "quantity": 3,
                "hours": 8,
            },
        ],
    )


class LoadPredefinedTemplateResponse(BaseModel):
    """Response model for a load profile created from a predefined template."""

    id: int
    profile_id: int
    template_id: int
    name: str
    power_kw: Decimal
    profile_source: str
    links: Dict[str, str] = Field(
        default={"self": "/v1/load_profiles/"},
        example={
            "self": "/v1/load_profiles/",
            "next": "/v1/load_profiles/?page=2",
        },
    )


class LoadPredefinedMasterTemplateResponse(BaseModel):
    """Response model for a master predefined template."""

    id: int
    name: str
    power_kw: int


class LoadPredefinedTemplateListResponse(BaseModel):
    """Response model for a list of master predefined templates."""

    items: List[LoadPredefinedMasterTemplateResponse]
