from app.exceptions.error_code_enums import ErrorCodeEnum


class HyggeException(Exception):
    """Base exception class for the application."""

    def __init__(self, message: str, code: ErrorCodeEnum = ""):
        self.message = message
        self.code = code
        super().__init__(f"{self.code}: {self.message}")

    def to_dict(self):
        return {"message": self.message, "code": str(self.code.value)}


class DatabaseException(HyggeException):
    """Exception raised for database-related errors."""

    def __init__(self, message="Database operation failed", details: str = None):
        self.details = details
        super().__init__(message)


class ServiceException(HyggeException):
    """Base exception for service layer"""

    def __init__(self, message: str = "Service layer exception", code: ErrorCodeEnum = ""):
        self.message = message
        self.code = code
        super().__init__(message, code)


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


class UnauthorizedError(HyggeException):
    def __init__(self, message="Unauthorized"):
        self.message = message
        super().__init__(self.message)


class InvalidRole(HyggeException):
    def __init__(self, message="Invalid Roles"):
        self.message = message
        super().__init__(self.message)
