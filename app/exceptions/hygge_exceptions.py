"""Module defining custom exceptions for the Hygge Power application."""

from typing import Optional

from app.exceptions.error_code_enums import ErrorCodeEnum


class HyggeException(Exception):
    """Base exception class for the application."""

    def __init__(self, message: str, code: Optional[ErrorCodeEnum] = None):
        self.message = message
        self.code = code
        if self.code:
            display_message = f"{self.code}: {self.message}"
        else:
            display_message = self.message
        super().__init__(display_message)

    def to_dict(self):
        return {
            "message": self.message,
            "code": str(self.code.value) if self.code else None,
        }


class DatabaseException(HyggeException):
    """Exception raised for database-related errors."""

    def __init__(
        self,
        message="Database operation failed",
        details: Optional[str] = None,
    ):
        self.details = details
        super().__init__(message)


class ServiceException(HyggeException):
    """Base exception for service layer"""

    def __init__(
        self,
        message: str = "Service layer exception",
        code: Optional[ErrorCodeEnum] = None,
    ):
        self.message = message
        self.code = code
        super().__init__(message, code)


class ValidationError(HyggeException):
    def __init__(self, message="Validation error occurred"):
        self.message = message
        super().__init__(self.message)


class InvalidAttemptState(ServiceException):
    def __init__(self, message="Attempt state not as per required"):
        self.message = message
        super().__init__(self.message)


class UserDoesNotExist(ServiceException):
    def __init__(self, message="User does not Exist"):
        self.message = message
        super().__init__(self.message)


class UserAlreadyExistException(ServiceException):
    def __init__(self, message="User already exist"):
        self.message = message
        super().__init__(self.message)


class NotFoundException(ServiceException):
    def __init__(self, message="Item not found"):
        self.message = message
        super().__init__(self.message)


class AlreadyExistsException(ServiceException):
    """Exception raised when an item that should be unique already exists."""

    def __init__(self, message="Item already exists"):
        self.message = message
        super().__init__(self.message)


class InvalidDataException(ServiceException):
    def __init__(self, message="Invalid topology data"):
        self.message = message
        super().__init__(self.message)


class UnauthorizedError(HyggeException):
    def __init__(self, message="Unauthorized"):
        self.message = message
        super().__init__(self.message)


class InvalidRole(HyggeException):
    def __init__(self, message="Invalid Roles"):
        self.message = message
        super().__init__(self.message)
