from fastapi import APIRouter, HTTPException, Depends
from app.api.v1.dependencies.container_instance import get_electrical_appliances_service
from app.api.v1.models.requests.electrical_appliances import AppliancesRequest
from app.utils.logger import logger
from app.api.authorization.authorization import permission
from app.api.authorization.enums import Resources, Permission
from app.domain.interfaces.iservice import IService
from app.api.v1.models.responses.electrical_appliances import AppliancesResponse, AppliancesListResponse

appliances_router = APIRouter(tags=['Appliances'])


@appliances_router.get('/', response_model=AppliancesListResponse)
async def get_appliances(service: IService = Depends(get_electrical_appliances_service),
                         _: str = Depends(permission(Resources.Electrical, Permission.Retrieve))):
    try:
        body = service.list_all()
        response = AppliancesListResponse(items=[AppliancesResponse(**item) for item in body])
        return response
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))


@appliances_router.post('/', response_model=AppliancesResponse)
async def create_appliances(data: AppliancesRequest,
                            service: IService = Depends(
                                get_electrical_appliances_service),
                            user_id: str = Depends(permission(Resources.Electrical, Permission.Create))):
    try:
        data = data.model_dump()
        body = service.create(user_id, **data)
        return AppliancesResponse(**body)
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))


@appliances_router.put('/{appliance_id}/update')
async def update_appliances(data: AppliancesRequest,
                            appliance_id: int,
                            service: IService = Depends(get_electrical_appliances_service),
                            user_id: str = Depends(permission(Resources.Electrical, Permission.Update))):
    try:
        data = data.model_dump(exclude_unset=True)
        body = service.update(user_id, appliance_id, **data)
        return body
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))


@appliances_router.delete('/{appliance_id}/delete')
async def delete_appliance(appliance_id: int,
                           service: IService = Depends(get_electrical_appliances_service),
                           _: str = Depends(permission(Resources.Electrical, Permission.Delete))):
    try:
        service.delete(appliance_id)
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))
