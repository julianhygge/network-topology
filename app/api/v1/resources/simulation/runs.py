from typing import List
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException

from app.api.authorization.authorization import permission
from app.api.authorization.enums import Permission, Resources
from app.api.v1.dependencies.container_instance import (
    get_bill_simulation_service,
    get_simulation_runs_service,
)
from app.api.v1.models.requests.simulation_request import (
    SimulationRunsRequestModel,
    SimulationRunsUpdateModel,
)
from app.api.v1.models.responses.simulation_response import (
    SimulationRunsResponse,
)
from app.domain.interfaces.i_service import IService
from app.domain.services.simulator_engine.bill_simulation_service import (
    BillSimulationService,
)

runs_router = APIRouter()

GetSimulationRunServiceDep = Depends(get_simulation_runs_service)
GetBillSimulationServiceDep = Depends(get_bill_simulation_service)

SimulationRetrievePermissionDep = Depends(
    permission(Resources.SIMULATION, Permission.RETRIEVE)
)
SimulationCreatePermissionDep = Depends(
    permission(Resources.SIMULATION, Permission.CREATE)
)
SimulationUpdatePermissionDep = Depends(
    permission(Resources.SIMULATION, Permission.UPDATE)
)


@runs_router.post(
    path="/simulation-runs/{simulation_run_id}/calculate-bills",
    status_code=202,
)
async def trigger_bill_calculation(
    simulation_run_id: UUID,
    service: BillSimulationService = GetBillSimulationServiceDep,
    _: UUID = SimulationCreatePermissionDep,
):
    """
    Trigger bill calculation for a given simulation run.

    Args:
        simulation_run_id: The ID of the simulation run.
        service: The BillSimulationService instance.
        _: Dependency to check permission.

    Returns:
        A status message indicating the calculation has started.

    Raises:
        HTTPException: If an error occurs.
    """
    try:
        service.calculate_bills_for_simulation_run(run_id=simulation_run_id)
        return {
            "message": "Bill calculation started"
            "for simulation run {simulation_run_id}"
        }
    except HTTPException as http_exc:
        raise http_exc
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Error triggering bill calculation: {str(e)}",
        ) from e


@runs_router.get(
    path="/{locality_id}/simulations-runs",
    response_model=List[SimulationRunsResponse],
)
async def get_simulation_runs_by_locality(
    locality_id: UUID,
    service: IService = GetSimulationRunServiceDep,
    _: UUID = SimulationRetrievePermissionDep,
):
    """
    Create the simulation run

    Args:
        locality_id: Unique Id of locality
        service: The simulation run service.
        _: Dependency to check permission.

    Returns:
        Newly Created Simulation

    Raises:
        HTTPException: If an error occurs during retrieval.
    """
    try:
        response = service.filter(locality_id=locality_id)
        return [SimulationRunsResponse.model_validate(i) for i in response]
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e)) from e


@runs_router.post(
    path="/simulations-runs", response_model=SimulationRunsResponse
)
async def create_simulation_runs(
    data: SimulationRunsRequestModel,
    service: IService = GetSimulationRunServiceDep,
    user_id: UUID = SimulationCreatePermissionDep,
):
    """
    Create the simulation run

    Args:
        data: data to create simulation runs
        service: The simulation run service.
        user_id: Dependency to check permission.

    Returns:
        Newly Created Simulation

    Raises:
        HTTPException: If an error occurs during retrieval.
    """
    try:
        data_dicts = data.model_dump()
        response = service.create(user_id, **data_dicts)
        return SimulationRunsResponse.model_validate(response)
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e)) from e


@runs_router.put(
    path="/{simulation_run_id}/simulations-runs",
    response_model=SimulationRunsResponse,
)
async def update_simulation_runs(
    simulation_run_id: UUID,
    data: SimulationRunsUpdateModel,
    service: IService = GetSimulationRunServiceDep,
    user_id: UUID = SimulationUpdatePermissionDep,
):
    """
    Update the simulation run

    Args:
        simulation_run_id: Unique ID of Simulation run to update
        data: data to update simulation runs
        service: The simulation run service.
        user_id: Dependency to check permission.

    Returns:
        Newly Updated Simulation

    Raises:
        HTTPException: If an error occurs during retrieval.
    """
    try:
        data_dicts = data.model_dump(exclude_unset=True)
        response = service.update(user_id, simulation_run_id, **data_dicts)
        return SimulationRunsResponse.model_validate(response)
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e)) from e
