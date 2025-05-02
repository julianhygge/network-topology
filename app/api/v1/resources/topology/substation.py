"""API endpoints for managing substations and their topology."""

from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, status
from pydantic import UUID4

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
from app.domain.interfaces.i_service import IService
from app.domain.interfaces.net_topology.i_net_topology_service import INetTopologyService
from app.domain.interfaces.net_topology.i_substation_service import ISubstationService
from app.utils.logger import logger

substation_router = APIRouter(tags=["Substations"])


@substation_router.get("/{substation_id}", response_model=SubstationTopology)
async def get_substation_topology(
    substation_id: UUID,
    _: str = Depends(permission(Resources.Substations, Permission.Retrieve)), # Corrected permission
    service: INetTopologyService = Depends(get_net_topology_service),
) -> SubstationTopology:
    """
    Retrieve the topology structure for a specific substation.

    Requires retrieve permission on the Substations resource.

    Args:
        substation_id: The ID of the substation.
        _: Placeholder for permission dependency.
        service: Injected network topology service instance.

    Returns:
        The topology structure starting from the substation.

    Raises:
        HTTPException: If the substation is not found (404).
    """
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
) -> SubstationTopology:
    """
    Update the topology structure for a specific substation.

    Requires update permission on the Substations resource.

    Args:
        substation_id: The ID of the substation to update.
        topology_data: The new topology structure data.
        user_id: ID of the user performing the action (from permission).
        service: Injected network topology service instance.

    Returns:
        The updated topology structure.

    Raises:
        HTTPException: If the substation is not found after update (404).
                       (Indicates potential issue if update succeeded but fetch failed)
    """
    service.update_topology(user_id, substation_id, topology_data.model_dump())
    # Fetch again to return the updated topology
    topology = service.get_topology_by_substation_id(str(substation_id))
    if not topology:
        # This case might indicate an issue if the update succeeded
        # but the subsequent fetch failed.
        logger.error("Failed to fetch topology after update for %s", substation_id)
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Substation not found after update attempt."
        )
    return topology


@substation_router.post("/", response_model=SubstationResponseModel)
async def create(
    data: SubstationRequestModel,
    user_id: UUID = Depends(permission(Resources.Substations, Permission.Create)),
    service: IService = Depends(get_substation_service),
) -> SubstationResponseModel:
    """
    Create a new substation.

    Requires create permission on the Substations resource.

    Args:
        data: Request body containing substation details.
        user_id: ID of the user performing the action (from permission).
        service: Injected substation service instance.

    Returns:
        The created substation details.
    """
    body = service.create(str(user_id), **data.model_dump())
    return SubstationResponseModel(**body)


@substation_router.post("/generate", response_model=SubstationResponseModelList)
async def generate_substations(
    data: SubstationsRequestModel,
    user_id: UUID = Depends(permission(Resources.Substations, Permission.Create)),
    service: ISubstationService = Depends(get_substation_service),
) -> SubstationResponseModelList:
    """
    Generate multiple substations within a locality.

    Requires create permission on the Substations resource.

    Args:
        data: Request body specifying locality and number of substations.
        user_id: ID of the user performing the action (from permission).
        service: Injected substation service instance.

    Returns:
        A list of the newly created substations.

    Raises:
        HTTPException: If an error occurs during bulk creation.
    """
    try:
        data_list = service.create_bulk(user_id, **data.model_dump())
        response = SubstationResponseModelList(
            items=[SubstationResponseModel(**item) for item in data_list]
        )
        return response
    except Exception as e:
        logger.exception("Error generating substations: %s", e)
        raise HTTPException(status_code=400, detail=str(e)) from e


@substation_router.get("", response_model=SubstationResponseModelList)
async def get(
    _: str = Depends(permission(Resources.Substations, Permission.Retrieve)),
    service: IService = Depends(get_substation_service),
) -> SubstationResponseModelList:
    """
    Retrieve a list of all substations.

    Requires retrieve permission on the Substations resource.

    Args:
        _: Placeholder for permission dependency.
        service: Injected substation service instance.

    Returns:
        A list of all substations, sorted by creation date.

    Raises:
        HTTPException: If an error occurs during retrieval.
    """
    try:
        data_list = service.list_all()
        # Ensure sorting happens correctly, assuming 'created_on' exists
        data_list.sort(key=lambda x: x.get("created_on"))
        response = SubstationResponseModelList(
            items=[SubstationResponseModel(**item) for item in data_list]
        )
        return response
    except Exception as e:
        logger.exception("Error retrieving substations: %s", e)
        raise HTTPException(status_code=400, detail=str(e)) from e


@substation_router.delete(
    path="/{substation_id}/delete",
    status_code=status.HTTP_204_NO_CONTENT
)
async def delete(
    substation_id: UUID,
    service: IService = Depends(get_substation_service),
    _: str = Depends(permission(Resources.Substations, Permission.Delete)),
) -> None:
    """
    Delete a substation.

    Requires delete permission on the Substations resource.

    Args:
        substation_id: The ID of the substation to delete.
        service: Injected substation service instance.
        _: Placeholder for permission dependency.

    Raises:
        HTTPException: If an error occurs during deletion.
    """
    try:
        service.delete(substation_id)
        return None # Return None for 204 No Content
    except Exception as e:
        logger.exception("Error deleting substation %s: %s", substation_id, e)
        # Consider raising NotFoundException if applicable from service.delete
        raise HTTPException(status_code=400, detail=str(e)) from e
