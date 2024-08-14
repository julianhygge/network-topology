import uuid
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException
from pydantic import UUID4
from starlette import status

from app.api.authorization.authorization import permission
from app.api.authorization.enums import Resources, Permission
from app.api.v1.dependencies.container_instance import (
    get_net_topology_service,
    get_substation_service,
)
from app.api.v1.models.requests.substation import (
    SubstationTopologyRequestModel,
    SubstationRequestModel,
    SubstationsRequestModel,
)
from app.api.v1.models.responses.substation import (
    SubstationResponseModel,
    SubstationResponseModelList,
    SubstationTopology,
)
from app.domain.interfaces.iservice import IService
from app.domain.interfaces.net_topology.inet_topology_service import INetTopologyService
from app.domain.interfaces.net_topology.isubstation_service import ISubstationService

substation_router = APIRouter(tags=["Substations"])


@substation_router.get("/{substation_id}", response_model=SubstationTopology)
async def get_substation_topology(
    substation_id: UUID,
    _: str = Depends(permission(Resources.Substations, Permission.Update)),
    service: INetTopologyService = Depends(get_net_topology_service),
):
    topology = service.get_topology_by_substation_id(str(substation_id))
    if not topology:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Substation not found"
        )
    return topology


@substation_router.put("/{substation_id}", response_model=SubstationTopology)
async def update_substation_topology(
    substation_id: UUID4,
    topology_data: SubstationTopologyRequestModel,
    user_id: str = Depends(permission(Resources.Substations, Permission.Update)),
    service: INetTopologyService = Depends(get_net_topology_service),
):
    service.update_topology(user_id, substation_id, topology_data.model_dump())
    topology = service.get_topology_by_substation_id(str(substation_id))
    if not topology:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Substation not found"
        )
    return topology


@substation_router.post("/", response_model=SubstationResponseModel)
async def create(
    data: SubstationRequestModel,
    user_id: UUID = Depends(permission(Resources.Substations, Permission.Create)),
    service: IService = Depends(get_substation_service),
):
    body = service.create(str(user_id), **data.model_dump())
    return SubstationResponseModel(**body)


@substation_router.post("/generate", response_model=SubstationResponseModelList)
async def generate_substations(
    data: SubstationsRequestModel,
    user_id: UUID = Depends(permission(Resources.Substations, Permission.Create)),
    service: ISubstationService = Depends(get_substation_service),
):
    try:
        data_list = service.create_bulk(user_id, **data.model_dump())
        response = SubstationResponseModelList(
            items=[SubstationResponseModel(**item) for item in data_list]
        )
        return response
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))


@substation_router.get("", response_model=SubstationResponseModelList)
async def get(
    _: str = Depends(permission(Resources.Substations, Permission.Retrieve)),
    service: IService = Depends(get_substation_service),
):
    try:
        data_list = service.list_all()
        data_list.sort(key=lambda x: x["created_on"])
        response = SubstationResponseModelList(
            items=[SubstationResponseModel(**item) for item in data_list]
        )
        return response
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))


@substation_router.delete(path="/{substation_id}/delete")
async def delete(
    substation_id: UUID,
    service: IService = Depends(get_substation_service),
    _: str = Depends(permission(Resources.Substations, Permission.Delete)),
):
    try:
        service.delete(substation_id)
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))
