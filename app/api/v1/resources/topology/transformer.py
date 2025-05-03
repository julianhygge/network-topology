"""API endpoints for managing transformer nodes within the topology."""

from fastapi import APIRouter, Depends, HTTPException, status
from pydantic import UUID4

from app.api.authorization.authorization import permission
from app.api.authorization.enums import Permission, Resources
from app.api.v1.dependencies.container_instance import (
    get_net_topology_service, get_transformer_service)
from app.api.v1.models.requests.transtormer_requests import (
    TransformerResponseModel, TransformerUpdateRequestModel)
from app.domain.interfaces.i_service import IService
from app.domain.interfaces.net_topology.i_net_topology_service import \
    INetTopologyService
from app.exceptions.hygge_exceptions import NotFoundException

transformer_router = APIRouter(tags=["Transformers"])


@transformer_router.put("/{transformer_id}", response_model=TransformerResponseModel)
async def update_transformer(
    transformer_id: UUID4,
    transformer_data: TransformerUpdateRequestModel,
    user_id: str = Depends(permission(Resources.TRANSFORMERS, Permission.UPDATE)),
    service: INetTopologyService = Depends(get_net_topology_service),
) -> TransformerResponseModel:
    """
    Update the details of a specific transformer node.

    Requires update permission on the Transformers resource.

    Args:
        transformer_id: The ID of the transformer to update.
        transformer_data: Request body containing updated transformer details.
        user_id: ID of the user performing the action (from permission).
        service: Injected network topology service instance.

    Returns:
        The updated transformer details.

    Raises:
        HTTPException: If the transformer is not found (404).
    """
    try:
        updated_transformer = service.update_transformer(
            user_id, str(transformer_id),
            transformer_data.model_dump(exclude_unset=True)
        )
        return updated_transformer
    except NotFoundException as e:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail=str(e)
        ) from e


@transformer_router.get("/{transformer_id}", response_model=TransformerResponseModel)
async def get(
    transformer_id: UUID4,
    _: str = Depends(permission(Resources.TRANSFORMERS, Permission.RETRIEVE)),
    service: IService = Depends(get_transformer_service),
) -> TransformerResponseModel:
    """
    Retrieve the details of a specific transformer node.

    Requires retrieve permission on the Transformers resource.

    Args:
        transformer_id: The ID of the transformer to retrieve.
        _: Placeholder for permission dependency.
        service: Injected transformer service instance.

    Returns:
        The details of the specified transformer.

    Raises:
        HTTPException: If the transformer is not found (404).
    """
    try:
        data = service.read(transformer_id)
        return data
    except NotFoundException as e:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail=str(e)
        ) from e
