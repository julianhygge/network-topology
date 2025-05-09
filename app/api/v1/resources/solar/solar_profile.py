"""API endpoints for managing Solar Profiles."""

from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException

from app.api.authorization.authorization import permission
from app.api.authorization.enums import Permission, Resources
from app.api.v1.dependencies.container_instance import (
    get_solar_profile_service,
)
from app.api.v1.models.requests.solar.solar_profile_request import (
    SolarProfileRequestModel,
    SolarProfileUpdateModel,
)
from app.api.v1.models.responses.solar.solar_profile_response import (
    SolarProfileResponse,
)
from app.domain.interfaces.solar.i_solar_profile_service import (
    ISolarProfileService,
)

solar_router = APIRouter(tags=["Solar"])


@solar_router.post("/", response_model=SolarProfileResponse)
async def create_solar_profile(
    data: SolarProfileRequestModel,
    service: ISolarProfileService = Depends(get_solar_profile_service),
    user_id: UUID = Depends(
        permission(Resources.LOAD_PROFILES, Permission.CREATE)
    ),
):
    """
    Create a new solar profile.

    Args:
        data: The request data for the solar profile.
        service: The solar profile service.
        user_id: The ID of the user creating the profile.

    Returns:
        The created solar profile.

    Raises:
        HTTPException: If an error occurs during creation.
    """
    try:
        data_dicts = data.model_dump()
        body = service.create(user_id, **data_dicts)
        return SolarProfileResponse(**body)
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e)) from e


@solar_router.get("/{house_id}")
async def get_solar_profile(
    house_id: UUID,
    service: ISolarProfileService = Depends(get_solar_profile_service),
    _: str = Depends(permission(Resources.LOAD_PROFILES, Permission.CREATE)),
):
    """
    Retrieve the solar profile for a specific house.

    Args:
        house_id: The ID of the house.
        service: The solar profile service.
        _: Dependency to check permission.

    Returns:
        The solar profile for the house, or None if not found.

    Raises:
        HTTPException: If an error occurs during retrieval.
    """
    try:
        body = service.filter(house_id=house_id)
        if body:
            return body[0]
        return None
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e)) from e


@solar_router.put("/{house-id}")
async def update_solar_profile(
    house_id: UUID,
    data: SolarProfileUpdateModel,
    service: ISolarProfileService = Depends(get_solar_profile_service),
    user_id: str = Depends(
        permission(Resources.LOAD_PROFILES, Permission.CREATE)
    ),
):
    """
    Update an existing solar profile for a specific house.

    Args:
        house_id: The ID of the house.
        data: The request data for the solar profile update.
        service: The solar profile service.
        user_id: The ID of the user updating the profile.

    Raises:
        HTTPException: If an error occurs during the update.
    """
    try:
        data = data.model_dump(exclude_unset=True)
        service.update_solar_profile(user_id, house_id, **data)
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e)) from e


@solar_router.delete("/{house_id}")
async def delete_solar_profile(
    house_id: UUID,
    service: ISolarProfileService = Depends(get_solar_profile_service),
    _: str = Depends(permission(Resources.LOAD_PROFILES, Permission.CREATE)),
):
    """
    Delete the solar profile for a specific house.

    Args:
        house_id: The ID of the house.
        service: The solar profile service.
        _: Dependency to check permission.

    Returns:
        A confirmation message.

    Raises:
        HTTPException: If an error occurs during deletion.
    """
    try:
        service.delete_solar_profile_by_house_id(house_id)
        return f"Solar Profile deleted with house_id {house_id}"
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e)) from e
