from datetime import datetime
from typing import Optional, List, Dict

from pydantic import BaseModel, Field, UUID4, EmailStr


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
    id: UUID4
    active: bool
    phone_number: str
    user_name: str
    name: str
    country_code: Optional[str] = Field(default=None)
    state: str
    email: EmailStr
    created_on: datetime
    groups: Optional[List[GroupModel]] = Field(default=None)


class UserLinkResponseModel(UserResponseModel):
    links: Dict[str, str] = Field(..., description="Links to user resources")


class UserListResponse(BaseModel):
    items: List[UserLinkResponseModel]
