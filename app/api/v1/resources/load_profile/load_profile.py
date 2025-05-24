"""API endpoints for managing Load Profiles."""

from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, Request, status

from app.api.authorization.authorization import permission
from app.api.authorization.enums import Permission, Resources
from app.api.v1.dependencies.container_instance import (
    get_load_profile_service,
)
from app.api.v1.models.responses.load_profile.load_profile_response import (
    LoadProfileResponse,
    LoadProfilesListResponse,
)
from app.api.v1.resources.load_profile.load_profile_builder import (
    builder_router,
)
from app.api.v1.resources.load_profile.load_profile_engine import (
    engine_router,
)
from app.api.v1.resources.load_profile.load_profile_files import (
    files_router,
)
from app.api.v1.resources.load_profile.load_profile_templates import (
    templates_router,
)
from app.domain.interfaces.solar.i_load_profile_service import (
    ILoadProfileService,
)

load_router = APIRouter(tags=["Load Profile"])

# Include routers from split files
load_router.include_router(files_router)
load_router.include_router(builder_router)
load_router.include_router(engine_router)
load_router.include_router(templates_router)

LoadProfilesDeletePermissionDep = Depends(
    permission(Resources.LOAD_PROFILES, Permission.DELETE)
)
GetLoadProfileServiceDep = Depends(get_load_profile_service)
LoadProfilesRetrievePermissionDep = Depends(
    permission(Resources.LOAD_PROFILES, Permission.RETRIEVE)
)


@load_router.delete(
    "/{load_profile_id}/", status_code=status.HTTP_204_NO_CONTENT
)
async def delete_load_profile(
    load_profile_id: int,
    _: str = LoadProfilesDeletePermissionDep,
    load_profile_service: ILoadProfileService = GetLoadProfileServiceDep,
):
    """
    Delete a specific load profile by its ID.

    Args:
        load_profile_id: The ID of the load profile to delete.
        _: Dependency to check delete permission.
        load_profile_service: Injected load profile service instance.

    Raises:
        HTTPException: 404 if the profile is not found, 400 for other errors.
    """
    try:
        result = load_profile_service.delete_profile(load_profile_id)
        if not result:
            raise HTTPException(
                status_code=404, detail="Load profile not found"
            )
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e)) from e


@load_router.get(
    "/",
    response_model=LoadProfilesListResponse,
    status_code=status.HTTP_200_OK,
)
async def list_load_profiles(
    request: Request,
    house_id: UUID,
    user_id: str = LoadProfilesRetrievePermissionDep,
    load_profile_service: ILoadProfileService = GetLoadProfileServiceDep,
):
    """
    List all load profiles associated with a specific house for the user.

    Args:
        request: The incoming request object.
        house_id: The ID of the house to list profiles for.
        user_id: The ID of the user making the request (from permission).
        load_profile_service: Injected load profile service instance.

    Returns:
        A list of load profiles with links.

    Raises:
        HTTPException: 400 if an error occurs during retrieval.
    """
    try:
        return await _get_load_profiles(
            load_profile_service, user_id, house_id, request
        )
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e)) from e


async def _get_load_profiles(
    load_profile_service: ILoadProfileService,
    user_id: str,
    house_id: UUID,
    request: Request,
):
    profiles = load_profile_service.list_profiles(user_id, house_id)
    items = []
    for profile in profiles:
        base_url = "load/"
        download = (
            f"{base_url}download/file?profile_id={profile['profile_id']}"
        )
        delete = f"{base_url}{profile['profile_id']}/"
        profile_data = {
            **profile,
            "links": {
                "self": base_url,
                "delete": delete,
                "download": download,
            },
        }
        profile_response = LoadProfileResponse(**profile_data)
        items.append(profile_response)
    response = LoadProfilesListResponse(items=items)
    return response
