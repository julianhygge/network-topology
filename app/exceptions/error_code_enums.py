"""Enums for defining specific error codes."""

from enum import Enum


class ErrorCodeEnum(Enum):
    """Enum representing specific error codes."""
    INVALID_BID_ID = "E001"
    BID_ROUND_NOT_OPEN = "E002"
    USER_ALREADY_PLACED_BID = "E003"

    def __str__(self):
        """Returns the string value of the enum member."""
        return self.value
