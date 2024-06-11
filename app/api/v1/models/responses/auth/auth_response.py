from datetime import datetime
from typing import Optional, List, Dict
from uuid import UUID

from pydantic import BaseModel, Field


class OtpVerificationModelResponse(BaseModel):
    state_token: str = Field(..., example="74f5596d-1df2-45ff-834c-a0511674c57f")
    attempts_remaining: int = Field(..., example=2)
    modified_on: datetime = Field(..., example="2023-07-18T19:41:27.442363")
    status: str = Field(..., example="SUCCESS")
    status_desc: str = Field(..., example="successful authentication attempt")


class OtpVerificationSuccessModelResponse(OtpVerificationModelResponse):
    session_token: Optional[str] = None
    refresh_token: Optional[str] = None
    role: str
    name: str


class GroupModel(BaseModel):
    id: int = Field(..., example=1)
    name: str = Field(..., example="Admin")
    is_member: bool = Field(..., example=True)


class UserResponseModel(BaseModel):
    id: UUID = Field(..., example=UUID("74f5596d-1df2-45ff-834c-a0511674c57f"))
    meter_number: str = Field(..., example="DL123456789")
    connection_number: str = Field(..., example="DL123456789")
    name: str = Field(..., example="Username")
    session_token: str = Field(..., example="")
    refresh_token: str = Field(..., example="")
    role: str = Field(..., example="Guest")
    user_name: str = Field(..., example="User 1")
    # active: bool = Field(..., example=True)
    # groups: List[GroupModel] = Field(default=[], example=[
    #     {"id": UUID("74f5596d-1df2-45ff-834c-a0511674c57f"), "name": "Admin", "is_member": True}])


class UserLinkResponseModel(UserResponseModel):
    links: Dict[str, str] = Field(..., description="Links to user resources")


class UserListResponse(BaseModel):
    items: List[UserLinkResponseModel]
