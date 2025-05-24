"""API endpoints for managing Load Profile builder operations."""

from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, Request

from app.api.authorization.authorization import permission
from app.api.authorization.enums import Permission, Resources
from app.api.v1.dependencies.container_instance import (
    get_load_profile_builder_service,
)
from app.api.v1.models.requests.load_profile.load_profile_update import (
    LoadProfileBuilderItemsRequest,
)
from app.api.v1.models.responses.load_profile.load_profile_response import (
    LoadProfileBuilderItemResponse,
    LoadProfileBuilderItemsResponse,
)
from app.domain.services.solar.load_profile_builder_service import (
    LoadProfileBuilderService,
)

builder_router = APIRouter(tags=["Load Profile"])

GetLoadProfileBuilderServiceDep = Depends(get_load_profile_builder_service)
LoadProfilesRetrievePermissionDep = Depends(
    permission(Resources.LOAD_PROFILES, Permission.RETRIEVE)
)


@builder_router.post(
    "/houses/{house_id}/load-profile-items",
    response_model=LoadProfileBuilderItemsResponse,
    description="Save load profile builder items for a specific house",
    response_description="The saved load profile builder items",
)
async def save_load_profile_builder_items(
    request: Request,
    house_id: UUID,
    items: LoadProfileBuilderItemsRequest,
    lpb_service: LoadProfileBuilderService = GetLoadProfileBuilderServiceDep,
    user_id: str = LoadProfilesRetrievePermissionDep,
):
    """
    Save load profile builder items for a specific house.

    Args:
        request: The incoming request object.
        house_id: The ID of the house.
        items: The load profile builder items to save.
        lpb_service:
        Injected load profile builder service instance.
        user_id: The ID of the user making the request (from permission).

    Returns:
        The saved load profile builder items with links.

    Raises:
        HTTPException: 400 for value errors, 500 for unexpected errors.
    """
    try:
        items_dicts = [item.model_dump() for item in items.items]
        updated_items, load_profile_id = lpb_service.save_load_profile_items(
            user_id, house_id, items_dicts
        )
        updated_items_response = [
            LoadProfileBuilderItemResponse(
                id=item.id,
                created_on=item.created_on,
                modified_on=item.modified_on,
                created_by=item.created_by.id,
                profile_id=item.profile_id.id,
                electrical_device_id=item.electrical_device_id.id,
                rating_watts=item.rating_watts,
                quantity=item.quantity,
                hours=item.hours,
            )
            for item in updated_items
        ]
        index = request.url.path.find("/load/")
        if index != -1:
            new_url_path = request.url.path[: index + len("/load/")]
        else:
            new_url_path = request.url.path
        delete = f"{new_url_path}{load_profile_id}/"
        return LoadProfileBuilderItemsResponse(
            message="Items retrieved successfully",
            links={"delete": delete},
            profile_id=load_profile_id,
            items=updated_items_response,
        )
    except ValueError as ve:
        raise HTTPException(status_code=400, detail=str(ve)) from ve
    except Exception as exc:
        raise HTTPException(
            status_code=500, detail="An unexpected error occurred"
        ) from exc


@builder_router.get(
    "/houses/{house_id}/load-profile-items",
    response_model=LoadProfileBuilderItemsResponse,
    description="Get builder items for a specific house",
    response_description="The current load profile builder items",
)
async def get_profile_builder_items(
    request: Request,
    house_id: UUID,
    lpb_service: LoadProfileBuilderService = GetLoadProfileBuilderServiceDep,
    user_id: str = LoadProfilesRetrievePermissionDep,
):
    """
    Get builder items for a specific house.

    Args:
        request: The incoming request object.
        house_id: The ID of the house.
        lpb_service: Injected load profile builder service instance.
        user_id: The ID of the user making the request (from permission).

    Returns:
        The current load profile builder items with links.

    Raises:
        HTTPException: 400 for value errors, 500 for unexpected errors.
    """
    try:
        updated_items, load_profile_id = (
            lpb_service.get_load_profile_builder_items(user_id, house_id)
        )
        updated_items_response = [
            LoadProfileBuilderItemResponse(
                id=item.id,
                created_on=item.created_on,
                modified_on=item.modified_on,
                created_by=item.created_by.id,
                profile_id=item.profile_id.id,
                electrical_device_id=item.electrical_device_id.id,
                rating_watts=item.rating_watts,
                quantity=item.quantity,
                hours=item.hours,
            )
            for item in updated_items
        ]
        index = request.url.path.find("/load/")
        if index != -1:
            new_url_path = request.url.path[: index + len("/load/")]
        else:
            new_url_path = request.url.path
        delete = f"{new_url_path}{load_profile_id}/"
        return LoadProfileBuilderItemsResponse(
            message="Items retrieved successfully",
            links={"delete": delete},
            profile_id=load_profile_id,
            items=updated_items_response,
        )
    except ValueError as ve:
        raise HTTPException(status_code=400, detail=str(ve)) from ve
    except Exception as exc:
        raise HTTPException(
            status_code=500, detail="An unexpected error occurred"
        ) from exc
