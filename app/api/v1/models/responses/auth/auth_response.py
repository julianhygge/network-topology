from datetime import datetime
from typing import Optional, List, Dict

from pydantic import BaseModel, Field, UUID4, EmailStr


class OtpVerificationModelResponse(BaseModel):
    state_token: UUID4 = Field(..., example="74f5596d-1df2-45ff-834c-a0511674c57f")
    attempts_remaining: int = Field(..., example=2)
    modified_on: datetime = Field(..., example="2023-07-18T19:41:27.442363")
    status: str = Field(..., example="SUCCESS")
    status_desc: str = Field(..., example="successful authentication attempt")


class OtpVerificationSuccessModelResponse(OtpVerificationModelResponse):
    session_token: Optional[str] = None
    refresh_token: Optional[str] = None
    role: str = Field(..., example="Consumer")
    name: str = Field(..., example="Username")


class GroupModel(BaseModel):
    id: int = Field(..., example=1)
    name: str = Field(..., example="Admin")
    is_member: bool = Field(..., example=True)


class UserResponseModel(BaseModel):
    id: UUID4 = Field(..., example="74f5596d-1df2-45ff-834c-a0511674c57f")
    active: bool = Field(..., example=True)
    phone_number: str = Field(..., example="9876565654")
    user_name: str = Field(..., example="Username")
    name: str = Field(..., example="Username")
    country_code: Optional[str] = Field(default=None)
    state: str = Field(..., example="Goa")
    email: EmailStr = Field(..., example="user@gmail.com")
    created_on: datetime = Field(..., example="2024-05-07 12:40")
    groups: Optional[List[GroupModel]] = Field(default=None)


class UserLinkResponseModel(UserResponseModel):
    links: Dict[str, str] = Field(..., description="Links to user resources")


class UserListResponse(BaseModel):
    items: List[UserLinkResponseModel]
