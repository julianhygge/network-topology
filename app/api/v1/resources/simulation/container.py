from typing import List
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException

from app.api.authorization.authorization import permission
from app.api.authorization.enums import Permission, Resources
from app.api.v1.dependencies.container_instance import (
    get_simulation_container_service,
)
from app.api.v1.models.requests.simulation_request import SimulationContainerRequestModel

from app.api.v1.models.responses.simulation_response import (
    SimulationRunsResponse, SimulationContainerResponse, SimulationContainerResponseList,
    SimulationContainerStatusResponse,
)

from app.domain.interfaces.i_service import IService
from app.domain.services.simulator_engine.simulation_container_service import SimulationContainerService

container_router = APIRouter()


GetSimulationContainerServiceDep = Depends(get_simulation_container_service)
SimulationContainerCreatePermissionDep = Depends(
    permission(Resources.SIMULATION, Permission.CREATE)
)
SimulationContainerRetrievePermissionDep = Depends(
    permission(Resources.SIMULATION, Permission.RETRIEVE))





@container_router.get(
    path="/container",
    response_model=SimulationContainerResponseList
)
async def get_simulation_container_list(
    service: SimulationContainerService = GetSimulationContainerServiceDep,
    _: UUID = SimulationContainerRetrievePermissionDep,
):
    """
    get list of simulation container

    Args:
        service: The simulation container service.
        _: Dependency to check permission.

    Returns:
        List of Simulation container

    Raises:
        HTTPException: If an error occurs during retrieval.
    """
    try:
         data = service.get_simulation_container_list()
         response = SimulationContainerResponseList(
             items=[
                 SimulationContainerStatusResponse.model_validate(item)
                 for item in data
             ]
         )
         return response
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e)) from e


@container_router.post(
    path="/container", response_model=SimulationContainerResponse
)
async def create_simulation_container(
    data: SimulationContainerRequestModel,
    service: IService = GetSimulationContainerServiceDep,
    user_id: UUID = SimulationContainerCreatePermissionDep,
):
    """
    Create the simulation container

    Args:
        data: data to create parent simulation
        service: The simulation container service.
        user_id: Dependency to check permission.

    Returns:
        Newly Created parent simulation

    Raises:
        HTTPException: If an error occurs during retrieval.
    """
    try:
        data_dicts = data.model_dump()
        response = service.create(user_id, **data_dicts)
        return SimulationContainerResponse(**response)
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e)) from e


