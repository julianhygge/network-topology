"""Pydantic models for creating load profiles."""

from typing import List, Optional

from pydantic import BaseModel, Field

from app.domain.entities.people_profile import PersonProfileItem


class PersonProfile(BaseModel):
    """Represents the profile of a person within a household."""

    works_at_home: bool = Field(
        ...,
        description="Indicates if the person works at home.",
        json_schema_extra={"example": True},
    )
    work_schedule: str = Field(
        ...,
        description="The time of day the person works, can be 'Day', 'Night', "
        "or 'Variable'.",
        json_schema_extra={"example": "Day"},
    )


class HouseholdInformation(BaseModel):
    """Represents information about the household."""

    number_of_people: int = Field(
        ...,
        ge=1,
        description="The number of people living in the house.",
        json_schema_extra={"example": 1},
    )
    people_profiles: List[PersonProfile] = Field(
        ..., description="List of profiles for each person in the household."
    )


class ApplianceUsage(BaseModel):
    """Represents the usage details for a specific appliance."""

    appliance_id: int = Field(
        ...,
        description="The unique identifier of the appliance.",
        json_schema_extra={"example": 9},
    )
    units: int = Field(
        ...,
        ge=1,
        description="Number of units of the appliance.",
        json_schema_extra={"example": 2},
    )
    hours_per_day: float = Field(
        ...,
        ge=0.5,
        le=24,
        description="Average hours per day the appliance is used.",
        json_schema_extra={"example": 3},
    )


class LoadProfileCreateRequest(BaseModel):
    """Request model for creating a new load profile."""

    load_profile_id: Optional[int] = Field(
        None,
        description="The unique identifier of the load profile. Optional.",
        json_schema_extra={"example": 1},
    )
    profile_name: str = Field(
        ...,
        description="A name for the load profile.",
        json_schema_extra={"example": "Type 3 Residential Profile 15kw"},
    )
    appliances_usage: List[ApplianceUsage] = Field(
        ..., description="List of appliances and their usage."
    )
    household_information: Optional[HouseholdInformation] = Field(
        default=None,
        description="Optional information about the household",
    )
    public: bool = Field(
        description="Indicates whether the load profile is public or not.",
        json_schema_extra={"example": True},
    )


class GenerateProfileFromTemplateRequest(BaseModel):
    """Request model for generating a load profile
    from a predefined template."""

    template_id: int = Field(
        ..., description="The ID of the predefined template to use."
    )
    people_profiles: List[PersonProfileItem] = Field(
        ...,
        description="List of people profiles in the household.",
        min_length=1,  # Using min_length for Pydantic v2 style
    )

    class Config:
        """Pydantic model configuration."""

        use_enum_values = True
        json_schema_extra = {
            "example": {
                "house_id": "a0eebc99-9c0b-4ef8-bb6d-6bb9bd380a11",
                "template_id": 1,
                "people_profiles": [
                    {"profile_type": "works_at_home", "count": 1},
                    {"profile_type": "day_worker_outside", "count": 1},
                ],
            }
        }
