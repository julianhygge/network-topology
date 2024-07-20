from pydantic import BaseModel, Field


class LoadProfileUpdateRequest(BaseModel):
    active: bool = Field(None, example=True, description="Indicates whether the load profile should be active or not.")
    profile_name: str = Field(None, min_length=1, max_length=50, example="Updated Residential Solar Profile",
                              description="New profile name")
    public: bool = Field(
        ...,
        example=True,
        description="Indicates whether the load profile is public or not."
    )
