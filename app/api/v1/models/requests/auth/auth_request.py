from datetime import datetime
from typing import Optional
from uuid import UUID
from fastapi import UploadFile
from pydantic import BaseModel
from pydantic import EmailStr, Field


class UploadFileSchema(BaseModel):
    filename: str
    content_type: str

    class Config:
        arbitrary_types_allowed = True

    @classmethod
    def __get_validators__(cls):
        yield cls.validate

    @classmethod
    def validate(cls, v):
        if not isinstance(v, UploadFile):
            raise TypeError('Expected UploadFile')
        return cls(filename=v.filename, content_type=v.content_type)


class OtpRequestModelResponse(BaseModel):
    state_token: str = Field(..., example="824960c0-974c-4c57-8803-85f5f407b304")
    attempts_remaining: int = Field(..., example=3)
    modified_on: Optional[datetime] = None
    status: str = Field(..., example="OTP_REQUIRED")
    status_desc: str = Field(..., example="waiting to verify OTP")


class UserModel(BaseModel):
    phone_number: str = Field(..., example="6475295636")
    name: str = Field(..., example="UserName")
    # email: EmailStr = Field(..., example="user@mail.com")
    # user_id: UUID = Field(..., example="824960c0-974c-4c57-8803-85f5f407b304")
    # country: Optional[str] = Field(..., example="Canada")
    # city: Optional[str] = Field(..., example="Toronto")
    # address: Optional[str] = Field(..., example="123 street")


class OtpVerificationRequest(BaseModel):
    otp: str = Field(..., example="654321")
    state_token: str = Field(..., example="824960c0-974c-4c57-8803-85f5f407b304")


class OtpRequest(BaseModel):
    phone_number: str = Field(..., example="6475295635")
    country_code: str = Field(..., example="+91")


class UserRequestModel(BaseModel):
    name: str = Field(..., example="UserName")
    phone_number: str = Field(..., example="89876543233")
    last_name: str = Field(..., example="UserName")
    state: str = Field(..., example="Karnataka")
    locality: str = Field(..., example="647 steel street ")
    meter_number: str = Field(..., example="DL123456789")
    connection_number: str = Field(..., example="DL123456789")
    utility_id: str = Field(..., example="824960c0-974c-4c57-8803-85f5f407b304")
    pin_code: str = Field(..., example="824960")
    email: str = Field(..., example="test@hygge.energy")
