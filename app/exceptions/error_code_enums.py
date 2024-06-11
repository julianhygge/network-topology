from enum import Enum


class ErrorCodeEnum(Enum):
    INVALID_BID_ID = "E001"
    BID_ROUND_NOT_OPEN = "E002"
    USER_ALREADY_PLACED_BID = "E003"

    def __str__(self):
        return self.value
