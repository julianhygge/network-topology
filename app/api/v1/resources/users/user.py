"""API endpoints for managing users."""

from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, Request, status

from app.api.authorization.authorization import permission
from app.api.authorization.enums import Permission, Resources
from app.api.v1.dependencies.container_instance import get_user_service
from app.api.v1.models.requests.auth.auth_request import UserRequestModel
from app.api.v1.models.responses.auth.auth_response import (
    UserLinkResponseModel,
    UserListResponse,
    UserResponseModel,
)
from app.domain.interfaces.i_service import IService
from app.exceptions.hygge_exceptions import NotFoundException
from app.utils.logger import logger

user_router = APIRouter(tags=["Users"])


@user_router.post(path="/", response_model=UserResponseModel)
async def create_user(
    user_data: UserRequestModel,
    user_id: str = Depends(permission(Resources.USERS, Permission.CREATE)),
    service: IService = Depends(get_user_service),
) -> UserResponseModel:
    """
    Create a new user.

    Requires create permission on the Users resource.

    Args:
        user_data: Request body containing user details.
        user_id: ID of the user performing the action (from permission check).
        service: Injected user service instance.

    Returns:
        The created user details.
    """
    body = service.create(user_id, **user_data.model_dump())
    return UserResponseModel(**body)


@user_router.get(path="/", response_model=UserListResponse)
async def get_users(
    request: Request,
    service: IService = Depends(get_user_service),
    _: str = Depends(permission(Resources.USERS, Permission.RETRIEVE)),
) -> UserListResponse:
    """
    Retrieve a list of all users.

    Requires retrieve permission on the Users resource.

    Args:
        request: The incoming request object (used for HATEOAS links).
        service: Injected user service instance.
        _: Placeholder for dependency injection of permission check.

    Returns:
        A list of users with HATEOAS links.

    Raises:
        HTTPException: If an error occurs during user retrieval.
    """
    try:
        data_list = service.list_all()
        response = UserListResponse(
            items=[
                UserLinkResponseModel(
                    **item,
                    links={"self": f"{request.url.path}{str(item['id'])}"},
                )
                for item in data_list
            ]
        )
        return response
    except Exception as e:
        logger.exception("Error retrieving users: %s", e)
        raise HTTPException(status_code=400, detail=str(e)) from e


@user_router.put(path="/{user_id}", response_model=UserResponseModel)
async def update(
    request: Request,
    user_data: UserRequestModel,
    user_id: UUID,
    logged_user_id: str = Depends(
        permission(Resources.USERS, Permission.UPDATE)
    ),
    service: IService = Depends(get_user_service),
) -> UserResponseModel:
    """
    Update an existing user.

    Requires update permission on the Users resource.

    Args:
        request: The incoming request object (used for HATEOAS links).
        user_data: Request body containing updated user details.
        user_id: The ID of the user to update.
        logged_user_id: ID of the user performing the action (from permission).
        service: Injected user service instance.

    Returns:
        The updated user details.

    Raises:
        NotFoundException: If the user to update is not found.
        HTTPException: If another error occurs during update.
    """
    try:
        updated_data = service.update(
            logged_user_id, user_id, **user_data.model_dump(exclude_unset=True)
        )
        if updated_data is None:
            raise NotFoundException(f"User with ID {user_id} not found.")
        # Assuming update returns the full updated object including 'id'
        updated_data["links"] = {"self": f"{request.url.path}"}
        return UserResponseModel(**updated_data)
    except NotFoundException as e:
        # Re-raise NotFoundException to be handled by its specific handler
        raise e
    except Exception as e:
        logger.exception("Error updating user %s: %s", user_id, e)
        raise HTTPException(status_code=400, detail=str(e)) from e


@user_router.delete(path="/{user_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete(
    user_id: UUID,
    _: str = Depends(permission(Resources.USERS, Permission.DELETE)),
    service: IService = Depends(get_user_service),
) -> None:
    """
    Delete a user.

    Requires delete permission on the Users resource.

    Args:
        user_id: The ID of the user to delete.
        _: Placeholder for dependency injection of permission check.
        service: Injected user service instance.

    Raises:
        NotFoundException: If the user to delete is not found.
    """
    delete_result = service.delete(user_id)
    if not delete_result:
        raise NotFoundException(
            f"User with ID {user_id} not found for deletion."
        )
    return None  # Return None for 204 No Content
