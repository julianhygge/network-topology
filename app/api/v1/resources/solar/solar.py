"""API endpoints for managing Solar Profiles."""

from typing import Optional, Union
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException

from app.api.authorization.authorization import permission
from app.api.authorization.enums import Permission, Resources
from app.api.v1.dependencies.container_instance import (
    get_solar_installation_service,
    get_solar_profile_service,
)
from app.api.v1.models.requests.solar.solar_profile_request import (
    SolarProfileRequestModel,
    SolarProfileUpdateModel,
)
from app.api.v1.models.responses.solar.solar_response import (
    SolarInstallationListResponse,
    SolarInstallationResponse,
    SolarProfileResponse,
)
from app.domain.interfaces.solar.i_solar_service import (
    ISolarInstallationService,
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


@solar_router.get(path="/area")
async def get_solar_installation(
    filter_key: Union[str, None] = None,
    limit: int = 10,
    offset: int = 0,
    service: ISolarInstallationService = Depends(
        get_solar_installation_service
    ),
    _: str = Depends(permission(Resources.LOAD_PROFILES, Permission.RETRIEVE)),
):
    """
    Retrieve the solar installation of area

    Args:
        filter_key: filter the solar installation by country, city, zip_code
        limit: Number of rows
        offset: Number of rows offset
        service: The solar profile service.
        _: Dependency to check permission.

    Returns:
        The solar installation filter by country, city, zip_code.

    Raises:
        HTTPException: If an error occurs during retrieval.
    """
    try:
        data, total_items, total_pages, current_page = (
            service.get_solar_installation(filter_key, limit, offset)
        )
        response = SolarInstallationListResponse(
            items=[SolarInstallationResponse(**item) for item in data],
            total_page=total_pages,
            total_items=total_items,
            current_page=current_page,
        )
        return response
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e)) from e


@solar_router.get("/{house_id}", response_model=Optional[SolarProfileResponse])
async def get_solar_profile(
    house_id: UUID,
    service: ISolarProfileService = Depends(get_solar_profile_service),
    _: str = Depends(permission(Resources.LOAD_PROFILES, Permission.CREATE)),
) -> Optional[SolarProfileResponse]:
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
        solar_profile_data_list = service.filter(house_id=house_id)
        if solar_profile_data_list:
            return SolarProfileResponse(**solar_profile_data_list[0])
        return None
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e)) from e


@solar_router.put("/{house-id}")
async def update_solar_profile(
    house_id: UUID,
    data: SolarProfileUpdateModel,
    service: ISolarProfileService = Depends(get_solar_profile_service),
    user_id: UUID = Depends(
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
        update_data_dict = data.model_dump(exclude_unset=True)
        service.update_solar_profile(user_id, house_id, **update_data_dict)
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

@solar_router.get('/backfill/data')
async def backfill_missing_data(
    service: ISolarInstallationService = Depends(get_solar_installation_service),
    _: str = Depends(permission(Resources.LOAD_PROFILES, Permission.CREATE)),
):
    try:
        service.backfill_missing_data()
        return "data inserted successfully"
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e)) from e


