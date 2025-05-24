"""API endpoints for managing transformer nodes within the topology."""

from fastapi import APIRouter, Depends, HTTPException, status
from pydantic import UUID4

from app.api.authorization.authorization import permission
from app.api.authorization.enums import Permission as p
from app.api.authorization.enums import Resources as r
from app.api.v1.dependencies.container_instance import (
    get_net_topology_service,
    get_transformer_service,
)
from app.api.v1.models.requests.transformer_requests import (
    TransformerResponseModel,
    TransformerUpdateRequestModel,
)
from app.domain.interfaces.i_service import IService
from app.domain.interfaces.net_topology.i_net_topology_service import (
    INetTopologyService,
)
from app.exceptions.hygge_exceptions import NotFoundException

tr_router = APIRouter(tags=["Transformers"])

TransformersUpdatePermissionDep = Depends(permission(r.TRANSFORMERS, p.UPDATE))
GetNetTopologyServiceDep = Depends(get_net_topology_service)
TransformersRetrievePermissionDep = Depends(
    permission(r.TRANSFORMERS, p.RETRIEVE)
)
GetTransformerServiceDep = Depends(get_transformer_service)


@tr_router.put("/{transformer_id}", response_model=TransformerResponseModel)
async def update_transformer(
    transformer_id: UUID4,
    transformer_data: TransformerUpdateRequestModel,
    user_id: str = TransformersUpdatePermissionDep,
    service: INetTopologyService = GetNetTopologyServiceDep,
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
            user_id,
            str(transformer_id),
            transformer_data.model_dump(exclude_unset=True),
        )
        return updated_transformer
    except NotFoundException as e:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail=str(e)
        ) from e


@tr_router.get("/{transformer_id}", response_model=TransformerResponseModel)
async def get(
    transformer_id: UUID4,
    _: str = TransformersRetrievePermissionDep,
    service: IService = GetTransformerServiceDep,
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
