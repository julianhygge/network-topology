"""API endpoints for managing flags associated with houses."""

from typing import List
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, status
from pydantic import UUID4

from app.api.authorization.authorization import permission
from app.api.authorization.enums import Permission, Resources
from app.api.v1.dependencies.container_instance import get_flag_service
from app.api.v1.models.requests.topology.flag_request import (
    FlagCreateRequest,
    FlagUpdateRequest,
)
from app.api.v1.models.responses.topology.flag_response import FlagResponse
from app.domain.interfaces.i_service import IService
from app.exceptions.hygge_exceptions import (
    AlreadyExistsException,
    NotFoundException,
)
from app.utils.logger import logger

FlagServiceType = IService[UUID, int]

flag_router = APIRouter(tags=["Flags"])

HousesCreatePermissionDep = Depends(
    permission(Resources.HOUSES, Permission.CREATE)
)
GetFlagServiceDep = Depends(get_flag_service)
HousesRetrievePermissionDep = Depends(
    permission(Resources.HOUSES, Permission.RETRIEVE)
)
HousesUpdatePermissionDep = Depends(
    permission(Resources.HOUSES, Permission.UPDATE)
)
HousesDeletePermissionDep = Depends(
    permission(Resources.HOUSES, Permission.DELETE)
)


@flag_router.post(
    "/{house_id}/flags",
    response_model=FlagResponse,
    status_code=status.HTTP_201_CREATED,
)
async def create_flag(
    house_id: UUID4,
    flag_data: FlagCreateRequest,
    user_id: UUID = HousesCreatePermissionDep,
    service: FlagServiceType = GetFlagServiceDep,
) -> FlagResponse:
    """
    Create a new flag for a specific house.

    Requires create permission on the Houses resource.
    """
    try:
        created_item_dict = service.create(
            user_id=user_id, **flag_data.model_dump(), house_id=house_id
        )
        return FlagResponse(**created_item_dict)
    except AlreadyExistsException as e:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT, detail=str(e)
        ) from e
    except NotFoundException as e:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail=str(e)
        ) from e
    except Exception as e:
        logger.exception(
            "Unexpected error in create_flag for house_id %s: %s", house_id, e
        )
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="An unexpected error occurred while creating the flag.",
        ) from e


@flag_router.get("/{house_id}/flags", response_model=List[FlagResponse])
async def get_flags_by_house(
    house_id: UUID4,
    _: UUID = HousesRetrievePermissionDep,
    service: IService = GetFlagServiceDep,
) -> List[FlagResponse]:
    """Retrieve all flags for a specific house.

    Args:
        house_id (UUID4): The ID of the house for which to retrieve flags.
        _ (UUID): The ID of the user performing the action
                        (injected by dependency).
        service (FlagServiceType): The service instance for flag operations
                                   (injected by dependency).

    Returns:
        List[FlagResponse]: A list of flag data transfer objects.

    Raises:
        HTTPException: If the house is not found (status 404) or if an
                       unexpected error occurs during flag retrieval
                       (status 500).

    Requires retrieve permission on the Houses resource.
    """
    try:
        data_list = service.filter(house_id=house_id)
        return [FlagResponse(**item) for item in data_list]
    except NotFoundException as e:  # If the house itself is not found
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail=str(e)
        ) from e
    except Exception as e:
        logger.exception(
            "Unexpected error in get_flags_by_house for house_id %s: %s",
            house_id,
            e,
        )
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="An unexpected error occurred while retrieving flags.",
        ) from e


@flag_router.put("/{house_id}/flags/{flag_id}", response_model=FlagResponse)
async def update_flag(
    house_id: UUID4,
    flag_id: int,
    flag_data: FlagUpdateRequest,
    user_id: UUID = HousesUpdatePermissionDep,
    service: FlagServiceType = GetFlagServiceDep,
) -> FlagResponse:
    """
    Update an existing flag.

    Requires update permission on the Houses resource.
    """
    try:
        updated_item_dict = service.update(
            user_id=user_id,
            item_id=flag_id,
            **flag_data.model_dump(exclude_unset=True),
            house_id=house_id,
        )
        if not updated_item_dict:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Flag with ID {flag_id} not found for update.",
            )
        return FlagResponse(**updated_item_dict)
    except NotFoundException as e:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail=str(e)
        ) from e
    except Exception as e:
        logger.exception(
            "Unexpected error in update_flag for house_id %s, flag_id %s: %s",
            house_id,
            flag_id,
            e,
        )
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="An unexpected error occurred while updating the flag.",
        ) from e


@flag_router.delete(
    "/{house_id}/flags/{flag_id}", status_code=status.HTTP_204_NO_CONTENT
)
async def delete_flag(
    flag_id: int,
    _: UUID = HousesDeletePermissionDep,
    service: FlagServiceType = GetFlagServiceDep,
) -> None:
    """
    Delete a flag.

    Requires delete permission on the Houses resource.
    """
    try:
        deleted_count = service.delete(item_id=flag_id)
        if deleted_count == 0:
            detail_msg = f"Flag {flag_id} not found for deletion."
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND, detail=detail_msg
            )
        return None
    except NotFoundException as e:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail=str(e)
        ) from e
