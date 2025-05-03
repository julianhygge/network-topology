"""Pydantic models for authentication requests."""

from datetime import datetime
from typing import Any, Callable, Generator, Optional
from uuid import UUID

from fastapi import UploadFile
from pydantic import BaseModel, Field


class UploadFileSchema(BaseModel):
    """Schema to represent basic metadata of an uploaded file."""
    filename: str
    content_type: str

    class Config:
        """Pydantic configuration."""
        arbitrary_types_allowed = True

    @classmethod
    def __get_validators__(cls) -> Generator[Callable[[Any], Any], None, None]:
        """Get validators for this schema."""
        yield cls.validate

    @classmethod
    def validate(cls, v: Any) -> 'UploadFileSchema':
        """Validate that the input is an UploadFile instance."""
        if not isinstance(v, UploadFile):
            raise TypeError('Expected UploadFile')
        return cls(filename=v.filename, content_type=v.content_type)


class OtpRequestModelResponse(BaseModel):
    """Response model after requesting an OTP."""
    state_token: UUID = Field(..., example="824960c0-974c-4c57-8803-85f5f407b304")
    attempts_remaining: int = Field(..., example=3)
    modified_on: Optional[datetime] = None
    status: str = Field(..., example="OTP_REQUIRED")
    status_desc: str = Field(..., example="waiting to verify OTP")


class OtpVerificationRequest(BaseModel):
    """Request model for verifying an OTP."""
    otp: str = Field(..., example="654321")
    state_token: UUID = Field(..., example="824960c0-974c-4c57-8803-85f5f407b304")


class OtpRequest(BaseModel):
    """Request model for initiating an OTP request."""
    phone_number: str = Field(..., example="6475295635")
    country_code: str = Field(..., example="+91")


class UserRequestModel(BaseModel):
    """Request model for creating or updating user details."""
    name: str = Field(..., example="UserName")
    phone_number: str = Field(..., example="89876543233")
    state: str = Field(..., example="Karnataka")
    pin_code: str = Field(..., example="824960")
    email: str = Field(..., example="test@hygge.energy")
