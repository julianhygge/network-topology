"""API endpoints for managing Load Profile engine configurations."""

from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, Request

from app.api.authorization.authorization import permission
from app.api.authorization.enums import Permission, Resources
from app.api.v1.dependencies.container_instance import (
    get_load_profile_engine_service,
)
from app.api.v1.models.requests.load_profile.load_profile_update import (
    LoadGenerationEngineRequest,
    LoadGenerationEngineResponse,
)
from app.domain.services.solar.load_profile_engine_service import (
    LoadProfileEngineService,
)

engine_router = APIRouter(tags=["Load Profile"])


@engine_router.post(
    "/houses/{house_id}/generation-engine",
    response_model=LoadGenerationEngineResponse,
    description="Save load generation engine data for a specific house",
    response_description="The saved load generation engine data",
)
async def save_load_generation_engine(
    request: Request,
    house_id: UUID,
    data: LoadGenerationEngineRequest,
    load_profile_engine_service: LoadProfileEngineService = Depends(
        get_load_profile_engine_service
    ),
    user_id: UUID = Depends(
        permission(Resources.LOAD_PROFILES, Permission.CREATE)
    ),
):
    """
    Save load generation engine data for a specific house.

    Args:
        request: The incoming request object.
        house_id: The ID of the house.
        data: The load generation engine data to save.
        load_profile_engine_service: Injected load profile engine service instance.
        user_id: The ID of the user making the request (from permission).

    Returns:
        The saved load generation engine data with links.

    Raises:
        HTTPException: 500 if an error occurs during saving.
    """
    try:
        engine = load_profile_engine_service.save_load_generation_engine(
            user_id, house_id, data.model_dump()
        )

        index = request.url.path.find("/load/")
        if index != -1:
            new_url_path = request.url.path[: index + len("/load/")]
        else:
            new_url_path = request.url.path
        delete = f"{new_url_path}{engine.profile_id.id}/"

        return LoadGenerationEngineResponse(
            id=engine.id,
            user_id=engine.user_id.id,
            profile_id=engine.profile_id.id,
            house_id=house_id,
            type=engine.type,
            average_kwh=engine.average_kwh,
            average_monthly_bill=engine.average_monthly_bill,
            max_demand_kw=engine.max_demand_kw,
            created_on=engine.created_on,
            modified_on=engine.modified_on,
            links={"delete": delete},
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e)) from e


@engine_router.get(
    "/houses/{house_id}/generation-engine",
    response_model=LoadGenerationEngineResponse,
    description="Get load generation engine data for a specific house",
    response_description="The load generation engine data",
)
async def get_load_generation_engine(
    request: Request,
    house_id: UUID,
    load_profile_engine_service: LoadProfileEngineService = Depends(
        get_load_profile_engine_service
    ),
    user_id: UUID = Depends(
        permission(Resources.LOAD_PROFILES, Permission.RETRIEVE)
    ),
):
    """
    Get load generation engine data for a specific house.

    Args:
        request: The incoming request object.
        house_id: The ID of the house.
        load_profile_engine_service: Injected load profile engine service instance.
        user_id: The ID of the user making the request (from permission).

    Returns:
        The load generation engine data with links.

    Raises:
        HTTPException: 404 if data is not found, 500 for unexpected errors.
    """
    try:
        engine = load_profile_engine_service.get_load_generation_engine(
            user_id, house_id
        )
        if engine is None:
            raise HTTPException(
                status_code=404, detail="Load generation engine data not found"
            )

        index = request.url.path.find("/load/")
        if index != -1:
            new_url_path = request.url.path[: index + len("/load/")]
        else:
            new_url_path = request.url.path
        delete = f"{new_url_path}{engine.profile_id.id}/"

        return LoadGenerationEngineResponse(
            id=engine.id,
            user_id=engine.user_id.id,
            profile_id=engine.profile_id.id,
            house_id=house_id,
            type=engine.type,
            average_kwh=engine.average_kwh,
            average_monthly_bill=engine.average_monthly_bill,
            max_demand_kw=engine.max_demand_kw,
            created_on=engine.created_on,
            modified_on=engine.modified_on,
            links={"delete": delete},
        )
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e)) from e
