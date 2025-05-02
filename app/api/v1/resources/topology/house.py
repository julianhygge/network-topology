from fastapi import APIRouter, Depends, HTTPException
from pydantic import UUID4
from starlette import status
from app.api.authorization.authorization import permission
from app.api.authorization.enums import Resources, Permission
from app.api.v1.models.requests.transtormer_requests import HouseUpdateRequestModel, HouseResponseModel
from app.domain.interfaces.i_service import IService
from app.domain.interfaces.net_topology.i_net_topology_service import INetTopologyService
from app.api.v1.dependencies.container_instance import get_net_topology_service, get_house_service
from app.exceptions.hygge_exceptions import NotFoundException

house_router = APIRouter(tags=["Houses"])


@house_router.put("/{house_id}", response_model=HouseResponseModel)
async def update_house(house_id: UUID4,
                       house_data: HouseUpdateRequestModel,
                       _: str = Depends(permission(Resources.Houses, Permission.Update)),
                       service: INetTopologyService = Depends(get_net_topology_service)):
    try:
        updated_house = service.update_house(str(house_id), house_data.model_dump())
        return updated_house
    except NotFoundException as e:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(e))


@house_router.get("/{house_id}", response_model=HouseResponseModel)
async def get(house_id: UUID4,
              _: str = Depends(permission(Resources.Houses, Permission.Update)),
              service: IService = Depends(get_house_service)):
    try:
        data = service.read(house_id)
        return data
    except NotFoundException as e:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(e))

