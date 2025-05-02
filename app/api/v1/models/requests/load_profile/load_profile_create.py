"""Pydantic models for creating load profiles."""

from typing import List, Optional

from pydantic import BaseModel, Field


class PersonProfile(BaseModel):
    """Represents the profile of a person within a household."""
    works_at_home: bool = Field(
        ..., example=True, description="Indicates if the person works at home."
    )
    work_schedule: str = Field(
        ..., example="Day",
        description="The time of day the person works, can be 'Day', 'Night', "
                    "or 'Variable'."
    )


class HouseholdInformation(BaseModel):
    """Represents information about the household."""
    number_of_people: int = Field(
        ..., example=1, ge=1,
        description="The number of people living in the house."
    )
    people_profiles: List[PersonProfile] = Field(
        ..., description="List of profiles for each person in the household."
    )


class ApplianceUsage(BaseModel):
    """Represents the usage details for a specific appliance."""
    appliance_id: int = Field(
        ..., example=9, description="The unique identifier of the appliance."
    )
    units: int = Field(
        ..., ge=1, example=2, description="Number of units of the appliance."
    )
    hours_per_day: float = Field(
        ..., ge=0.5, le=24, example=3,
        description="Average hours per day the appliance is used."
    )


class LoadProfileCreateRequest(BaseModel):
    """Request model for creating a new load profile."""
    load_profile_id: Optional[int] = Field(None, example="1")
    profile_name: str = Field(
        ..., example="Type 3 Residential Profile 15kw",
        description="A name for the load profile."
    )
    appliances_usage: List[ApplianceUsage] = Field(
        ..., description="List of appliances and their usage."
    )
    household_information: Optional[HouseholdInformation] = Field(
        default=None,
        description="Information about the household and its occupants. Optional."
    )
    public: bool = Field(
        example=True,
        description="Indicates whether the load profile is public or not."
    )
