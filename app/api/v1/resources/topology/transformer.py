from fastapi import APIRouter, Depends, HTTPException
from pydantic import UUID4
from starlette import status
from app.api.authorization.authorization import permission
from app.api.authorization.enums import Resources, Permission
from app.api.v1.models.requests.transtormer_requests import TransformerResponseModel, TransformerUpdateRequestModel
from app.domain.interfaces.iservice import IService
from app.domain.interfaces.net_topology.inet_topology_service import INetTopologyService
from app.api.v1.dependencies.container_instance import get_net_topology_service, get_transformer_service
from app.exceptions.hygge_exceptions import NotFoundException

transformer_router = APIRouter(tags=["Transformers"])


@transformer_router.put("/{transformer_id}", response_model=TransformerResponseModel)
async def update_transformer(transformer_id: UUID4,
                             transformer_data: TransformerUpdateRequestModel,
                             _: str = Depends(permission(Resources.Transformers, Permission.Update)),
                             service: INetTopologyService = Depends(get_net_topology_service)):
    try:
        updated_transformer = service.update_transformer(str(transformer_id), transformer_data.model_dump())
        return TransformerResponseModel(**updated_transformer)
    except NotFoundException as e:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(e))


@transformer_router.get("/{transformer_id}")
async def get(transformer_id: UUID4,
              _: str = Depends(permission(Resources.Houses, Permission.Update)),
              service: IService = Depends(get_transformer_service)):
    try:
        data = service.read(transformer_id)
        return data
    except NotFoundException as e:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(e))
