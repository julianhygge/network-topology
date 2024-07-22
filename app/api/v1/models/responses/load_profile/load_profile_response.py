from datetime import datetime
from typing import Dict, List
from pydantic import BaseModel, Field, UUID4


class LoadProfileResponse(BaseModel):
    links: Dict[str, str] = Field(
        default={"self": "/v1/load_profiles/"},
        example={"self": "/v1/load_profiles/", "next": "/v1/load_profiles/?page=2"}
    )
    profile_id: int = Field(
        ...,
        example=1,
        description="The unique ID of the load profile."
    )
    active: bool = Field(
        ...,
        example=True,
        description="Indicates whether the load profile is active or not."
    )
    profile_name: str = Field(
        ...,
        example="Residential Solar Profile",
        description="The profile name."
    )
    user_id: UUID4 = Field(
        ...,
        example="123e4567-e89b-12d3-a456-426614174000",
        description="The ID of the user associated with this profile."
    )
    user: str = Field(
        ...,
        example="User 12",
        description="User name"
    )
    file_name: str = Field(
        ...,
        example="load_profile_user.csv",
        description="Profile user load file name"
    )
    created_on: datetime = Field(
        ...,
        example="2023-01-01T12:00:00Z",
        description="UTC timestamp when the profile was created."
    )
    modified_on: datetime = Field(
        ...,
        example="2023-01-02T12:00:00Z",
        description="UTC timestamp when the profile was last modified."
    )

    source: str = Field(
        ...,
        example="Template",
        description="Source of the load profile"
    )

    class Config:
        from_attributes = True


class LoadProfilesListResponse(BaseModel):
    items: List[LoadProfileResponse]
