from fastapi import APIRouter, Depends, HTTPException
from fastapi.params import Depends
from uuid import UUID
from app.api.authorization.authorization import permission
from app.api.authorization.enums import Resources, Permission
from app.api.v1.dependencies.container_instance import get_simulation_algorithm_service, \
    get_net_metering_algorithm_service, get_simulation_runs_service
from app.api.v1.models.requests.simulation_request import SimulationRunsRequestModel
from app.api.v1.models.responses.simulation_response import SimulationAlgorithmResponse, \
    SimulationAlgorithmListResponse, NetMeteringAlgorithmListResponse, NetMeteringAlgorithmResponse
from app.domain.interfaces.i_service import IService

simulation_router = APIRouter(tags=["Simulation"])
GetSimulationAlgorithmServiceDep = Depends(get_simulation_algorithm_service)
GetNetMeteringAlgorithmServiceDep = Depends(get_net_metering_algorithm_service)
GetSimulationRunServiceDep = Depends(get_simulation_runs_service)
SimulationAlgorithmRetrievePermissionDep = Depends(
    permission(Resources.SIMULATION, Permission.RETRIEVE)
)
@simulation_router.get(path="/simulation-algo", response_model=SimulationAlgorithmListResponse)
async def get_simulation_algorithm(
        service: IService = GetSimulationAlgorithmServiceDep,
        _: UUID = SimulationAlgorithmRetrievePermissionDep
):
    """
       Retrieve the simulation algorithm type

       Args:
           service: The solar profile service.
           _: Dependency to check permission.

       Returns:
           All the active simulation algorithm

       Raises:
           HTTPException: If an error occurs during retrieval.
       """
    try:
        body = service.list_all()
        response = SimulationAlgorithmListResponse(
            items=[SimulationAlgorithmResponse(**item) for item in body]
        )
        return response
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e)) from e


@simulation_router.get(path="/net-metering/algo", response_model=NetMeteringAlgorithmListResponse)
async def get_net_metering_algorithm(
        service: IService = GetNetMeteringAlgorithmServiceDep,
        _: UUID = SimulationAlgorithmRetrievePermissionDep
):
    """
       Retrieve the net metering algorithm type

       Args:
           service: The solar profile service.
           _: Dependency to check permission.

       Returns:
           All the active net metring algorithm

       Raises:
           HTTPException: If an error occurs during retrieval.
       """
    try:
        body = service.list_all()
        response = NetMeteringAlgorithmListResponse(
            items=[NetMeteringAlgorithmResponse(**item) for item in body]
        )
        return response
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e)) from e

@simulation_router.post(path="/simulations-runs")
async def create_simulation_runs(
        data: SimulationRunsRequestModel,
        service: IService = GetSimulationRunServiceDep,
        user_id: UUID = SimulationAlgorithmRetrievePermissionDep
):
    try:
        data = data.model_dump()
        response = service.create(user_id, **data)
        print(response)
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e)) from e


@simulation_router.post(path="/{simulation_id}/net-metring")
async def create_net_metering_policy(
        simulation_id: UUID,
        service: IService = GetNetMeteringAlgorithmServiceDep,
        _: UUID = SimulationAlgorithmRetrievePermissionDep
):
    try:
        print("HI")
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e)) from e