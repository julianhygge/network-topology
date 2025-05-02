from fastapi import APIRouter, Depends, HTTPException
from app.api.authorization.authorization import permission
from app.api.authorization.enums import Resources, Permission
from app.api.v1.dependencies.container_instance import get_solar_profile_service
from app.api.v1.models.requests.solar.solar_profile_request import SolarProfileRequestModel, SolarProfileUpdateModel
from app.api.v1.models.responses.solar.solar_profile_response import SolarProfileResponse, SolarProfileListResponse
from app.domain.interfaces.i_service import IService
from uuid import UUID
from app.domain.interfaces.solar.isolar_profile_service import ISolarProfileService

solar_router = APIRouter(tags=["Solar"])


@solar_router.post('/', response_model=SolarProfileResponse)
async def create_solar_profile(
        data: SolarProfileRequestModel,
        service: ISolarProfileService = Depends(get_solar_profile_service),
        user_id: str = Depends(permission(Resources.LoadProfiles, Permission.Create))
):
    try:
        data = data.model_dump()
        body = service.create(user_id, **data)
        return SolarProfileResponse(**body)
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))


@solar_router.get("/{house_id}")
async def get_solar_profile(
        house_id: UUID,
        service: ISolarProfileService = Depends(get_solar_profile_service),
        _: str = Depends(permission(Resources.LoadProfiles, Permission.Create))):
    try:
        body = service.get_solar_profile_by_house_id(house_id)
        if body:
            response = SolarProfileResponse(**body)
            return response
        # response = SolarProfileListResponse(items=[SolarProfileResponse(**item) for item in body])
        return None
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))


@solar_router.put('/{house-id}')
async def update_solar_profile(
        house_id: UUID,
        data: SolarProfileUpdateModel,
        service: ISolarProfileService = Depends(get_solar_profile_service),
        user_id: str = Depends(permission(Resources.LoadProfiles, Permission.Create))):

    try:
        data = data.model_dump(exclude_unset=True)
        service.update_solar_profile(user_id, house_id, **data)
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))


@solar_router.delete('/{house_id}')
async def delete_solar_profile(
        house_id: UUID,
        service: ISolarProfileService = Depends(get_solar_profile_service),
        _: str = Depends(permission(Resources.LoadProfiles, Permission.Create))):
    try:
        service.delete_solar_profile_by_house_id(house_id)
        return f"Solar Profile deleted with house_id {house_id}"
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))


