from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException

from app.api.authorization.authorization import permission
from app.api.authorization.enums import Permission, Resources
from app.api.v1.dependencies.container_instance import (
    get_net_metering_algorithm_service,
    get_simulation_algorithm_service,
)
from app.api.v1.models.responses.simulation_response import (
    NetMeteringAlgorithmListResponse,
    NetMeteringAlgorithmResponse,
    SimulationAlgorithmListResponse,
    SimulationAlgorithmResponse,
)
from app.domain.interfaces.i_service import IService

algorithms_router = APIRouter()

GetSimulationAlgorithmServiceDep = Depends(get_simulation_algorithm_service)
GetNetMeteringAlgorithmServiceDep = Depends(get_net_metering_algorithm_service)

SimulationRetrievePermissionDep = Depends(
    permission(Resources.SIMULATION, Permission.RETRIEVE)
)


@algorithms_router.get(
    path="/algorithms", response_model=SimulationAlgorithmListResponse
)
async def get_simulation_algorithm(
    service: IService = GetSimulationAlgorithmServiceDep,
    _: UUID = SimulationRetrievePermissionDep,
):
    """
    Retrieve the simulation algorithm type

    Args:
        service: The simulation algorithm service.
        _: Dependency to check permission.

    Returns:
        All the active simulation algorithm

    Raises:
        HTTPException: If an error occurs during retrieval.
    """
    try:
        body = service.list_all()
        response = SimulationAlgorithmListResponse(
            items=[
                SimulationAlgorithmResponse.model_validate(item)
                for item in body
            ]
        )
        return response
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e)) from e


@algorithms_router.get(
    path="/net-metering/policies",
    response_model=NetMeteringAlgorithmListResponse,
)
async def get_net_metering_algorithm(
    service: IService = GetNetMeteringAlgorithmServiceDep,
    _: UUID = SimulationRetrievePermissionDep,
):
    """
    Retrieve the net metering policies types

    Args:
        service: The net metering algorithm service.
        _: Dependency to check permission.

    Returns:
        All the active net metering policies

    Raises:
        HTTPException: If an error occurs during retrieval.
    """
    try:
        body = service.list_all()
        response = NetMeteringAlgorithmListResponse(
            items=[
                NetMeteringAlgorithmResponse.model_validate(item)
                for item in body
            ]
        )
        return response
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e)) from e
