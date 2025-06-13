from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException

from app.api.authorization.authorization import permission
from app.api.authorization.enums import Permission, Resources
from app.api.v1.dependencies.container_instance import (
    get_simulation_container_service,
)
from app.api.v1.models.requests.simulation_request import (
    SimulationContainerRequestModel,
)
from app.api.v1.models.responses.simulation_response import (
    SimulationContainerResponse,
    SimulationContainerResponseList,
    SimulationContainerStatusResponse,
)
from app.domain.interfaces.simulator_engine.I_simulation_container_service import (
    ISimulationContainerService,
)

container_router = APIRouter()


GetSimulationContainerServiceDep = Depends(get_simulation_container_service)
SimulationContainerCreatePermissionDep = Depends(
    permission(Resources.SIMULATION, Permission.CREATE)
)
SimulationContainerRetrievePermissionDep = Depends(
    permission(Resources.SIMULATION, Permission.RETRIEVE)
)


@container_router.get(
    path="/containers", response_model=SimulationContainerResponseList
)
async def get_simulation_container_list(
    service: ISimulationContainerService = GetSimulationContainerServiceDep,
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
    service: ISimulationContainerService = GetSimulationContainerServiceDep,
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
        response = service.create_simulation_container(user_id, **data_dicts)
        return SimulationContainerResponse(**response)
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e)) from e
