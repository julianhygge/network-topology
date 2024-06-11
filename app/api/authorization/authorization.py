from fastapi import HTTPException, status, Security
from starlette.requests import Request
from app.api.authorization.enums import Resources, Permission
from fastapi.security import HTTPBearer


def permission(resource: Resources, action: Permission):
    def permission_dependency(request: Request, _=Security(HTTPBearer())):
        claims = getattr(request.state, 'claims', {})
        permissions = claims.get('permissions', [])
        user_id = claims.get('user', None)
        # required_permission = f"{action.value}-{resource.value}"
        # if required_permission not in permissions:
        #     raise HTTPException(
        #         status_code=status.HTTP_403_FORBIDDEN,
        #         detail="You don't have permission to perform this action."
        #     )
        return "64522a0a-c8f1-40f8-a2e5-9aed2dc23764"

    return permission_dependency
