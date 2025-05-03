"""Authorization dependencies for FastAPI."""

from fastapi import HTTPException, Security, status
from fastapi.security import HTTPBearer
from starlette.requests import Request

from app.api.authorization.enums import Permission, Resources


def permission(resource: Resources, action: Permission):
    """
    Creates a FastAPI dependency to check user permissions.

    Args:
        resource: The resource being accessed.
        action: The action being performed on the resource.

    Returns:
        A dependency function that checks for the required permission.
    """

    def permission_dependency(request: Request, _=Security(HTTPBearer())):
        """
        Dependency function to check if the user has the required permission.

        Args:
            request: The incoming request.
            _: Security dependency for HTTPBearer token.

        Returns:
            The user ID if permission is granted.

        Raises:
            HTTPException: If the user does not have the required permission.
        """
        claims = getattr(request.state, "claims", {})
        permissions = claims.get("permissions", [])
        user_id = claims.get("user", None)
        required_permission = f"{action.value}-{resource.value}"
        if required_permission not in permissions:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="You don't have permission to perform this action.",
            )
        return user_id

    return permission_dependency
