from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel
from starlette import status

from app.api.authorization.authorization import permission
from app.api.authorization.enums import Resources, Permission
from app.api.v1.dependencies.container_instance import get_user_service

group_router = APIRouter(tags=["Groups"])


class UserGroupRelation(BaseModel):
    user_id: UUID
    group_id: int


@group_router.post(path="/user/", status_code=status.HTTP_200_OK)
async def add_user(
        relation: UserGroupRelation,
        logged_user_id: str = Depends(permission(Resources.Users, Permission.Update)),
        service=Depends(get_user_service)):
    result = service.add_user_to_group(logged_user_id, relation.user_id, relation.group_id)
    if result:
        return {"status": "success", "message": "User added to group successfully."}
    else:
        raise HTTPException(status_code=400,
                            detail="Failed to add user to group. User may already be in the group or invalid IDs.")


@group_router.delete(path="/user/", status_code=status.HTTP_200_OK)
async def remove_user(relation: UserGroupRelation,
                      _=Depends(permission(Resources.Users, Permission.Update)),
                      service=Depends(get_user_service)):
    result = service.remove_user_from_group(relation.user_id, relation.group_id)
    if result:
        return {"status": "success", "message": "User removed from group successfully."}
    else:
        raise HTTPException(status_code=404, detail="User or group not found or user not in group.")
