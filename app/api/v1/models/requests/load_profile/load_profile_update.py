from typing import List, Optional

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


class LoadProfileBuilderItemRequest(BaseModel):
    id: Optional[int] = Field(default=None, example=1)
    electrical_device_id: int = Field(..., example=1)
    rating_watts: int = Field(..., example=60)
    quantity: int = Field(..., example=5)
    hours: int = Field(..., example=4)


class LoadProfileBuilderItemsRequest(BaseModel):
    items: List[LoadProfileBuilderItemRequest] = Field(..., example=[
        {
            "id": 1,
            "electrical_device_id": 1,
            "rating_watts": 60,
            "quantity": 5,
            "hours": 4
        },
        {
            "electrical_device_id": 2,
            "rating_watts": 75,
            "quantity": 3,
            "hours": 8
        }
    ])
