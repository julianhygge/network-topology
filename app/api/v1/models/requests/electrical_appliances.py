from pydantic import BaseModel, Field


class AppliancesRequest(BaseModel):
    name: str = Field(..., example='bulb')


class ApplianceUpdateRequest(BaseModel):
    name: str = Field(..., example='bulb')
    appliance_id: int = Field(..., example=1)
