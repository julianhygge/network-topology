"""API endpoints for managing user-group relationships."""

from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel
from starlette import status

from app.api.authorization.authorization import permission
from app.api.authorization.enums import Resources, Permission
from app.api.v1.dependencies.container_instance import get_user_service
from app.domain.interfaces.i_service import IService

group_router = APIRouter(tags=["Groups"])


class UserGroupRelation(BaseModel):
    """Request model for user-group relationship operations."""
    user_id: UUID
    group_id: int


@group_router.post(path="/user/", status_code=status.HTTP_200_OK)
async def add_user(
        relation: UserGroupRelation,
        logged_user_id: str = Depends(permission(Resources.Users, Permission.Update)),
        service: IService = Depends(get_user_service)):
    """
    Add a user to a specific group.

    Requires update permission on the Users resource.

    Args:
        relation: Request body containing user_id and group_id.
        logged_user_id: The ID of the logged-in user performing the action.
        service: Injected user service instance.

    Returns:
        Success message if the user is added.

    Raises:
        HTTPException: If adding the user fails (e.g., already in group).
    """
    result = service.add_user_to_group(
        logged_user_id, relation.user_id, relation.group_id
    )
    if result:
        return {"status": "success", "message": "User added to group successfully."}

    raise HTTPException(
        status_code=400,
        detail="Failed to add user to group. User may already be in the group "
               "or invalid IDs provided."
    )


@group_router.delete(path="/user/", status_code=status.HTTP_200_OK)
async def remove_user(
        relation: UserGroupRelation,
        _: str = Depends(permission(Resources.Users, Permission.Update)),
        service: IService = Depends(get_user_service)):
    """
    Remove a user from a specific group.

    Requires update permission on the Users resource.

    Args:
        relation: Request body containing user_id and group_id.
        _: Placeholder for dependency injection of permission check.
        service: Injected user service instance.

    Returns:
        Success message if the user is removed.

    Raises:
        HTTPException: If removal fails (e.g., user not in group).
    """
    result = service.remove_user_from_group(relation.user_id, relation.group_id)
    if result:
        return {"status": "success", "message": "User removed from group successfully."}

    raise HTTPException(
        status_code=404, detail="User or group not found or user not in group."
    )
