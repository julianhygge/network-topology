"""API endpoints for managing house nodes within the topology."""

from fastapi import APIRouter, Depends, HTTPException, status
from pydantic import UUID4

from app.api.authorization.authorization import permission
from app.api.authorization.enums import Permission, Resources
from app.api.v1.dependencies.container_instance import (
    get_house_service, get_net_topology_service)
from app.api.v1.models.requests.transtormer_requests import (
    HouseResponseModel, HouseUpdateRequestModel)
from app.domain.interfaces.i_service import IService
from app.domain.interfaces.net_topology.i_net_topology_service import \
    INetTopologyService
from app.exceptions.hygge_exceptions import NotFoundException

house_router = APIRouter(tags=["Houses"])


@house_router.put("/{house_id}", response_model=HouseResponseModel)
async def update_house(
    house_id: UUID4,
    house_data: HouseUpdateRequestModel,
    _: str = Depends(permission(Resources.HOUSES, Permission.UPDATE)),
    service: INetTopologyService = Depends(get_net_topology_service)
) -> HouseResponseModel:
    """
    Update the details of a specific house node.

    Requires update permission on the Houses resource.

    Args:
        house_id: The ID of the house to update.
        house_data: Request body containing the updated house details.
        _: Placeholder for permission dependency.
        service: Injected network topology service instance.

    Returns:
        The updated house details.

    Raises:
        HTTPException: If the house is not found (404).
    """
    try:
        updated_house = service.update_house(
            str(house_id), house_data.model_dump(exclude_unset=True)
        )
        return updated_house
    except NotFoundException as e:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail=str(e)
        ) from e


@house_router.get("/{house_id}", response_model=HouseResponseModel)
async def get(
    house_id: UUID4,
    _: str = Depends(permission(Resources.HOUSES, Permission.RETRIEVE)), # Corrected permission
    service: IService = Depends(get_house_service)
) -> HouseResponseModel:
    """
    Retrieve the details of a specific house node.

    Requires retrieve permission on the Houses resource.

    Args:
        house_id: The ID of the house to retrieve.
        _: Placeholder for permission dependency.
        service: Injected house service instance.

    Returns:
        The details of the specified house.

    Raises:
        HTTPException: If the house is not found (404).
    """
    try:
        data = service.read(house_id)
        return data
    except NotFoundException as e:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail=str(e)
        ) from e
