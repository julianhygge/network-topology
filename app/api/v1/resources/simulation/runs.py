from typing import List
from uuid import UUID
from datetime import datetime
from fastapi import APIRouter, Depends, HTTPException, status

from app.api.authorization.authorization import permission
from app.api.authorization.enums import Permission, Resources
from app.api.v1.dependencies.container_instance import (
    get_bill_simulation_service,
    get_data_preparation_service,
    get_simulation_runs_service,
)
from app.domain.interfaces.simulator_engine.i_data_preparation_service import (
    IDataPreparationService,
)
from app.api.v1.models.requests.simulation_request import (
    SimulationRunsRequestModel,
    SimulationRunsUpdateModel,
)
from app.api.v1.models.responses.simulation_response import (
    SimulationRunsResponse,
)
from app.api.v1.resources.simulation.container import GetSimulationContainerServiceDep
from app.domain.interfaces.i_service import IService
from app.domain.services.simulator_engine.bill_simulation_service import (
    BillSimulationService,
)
from app.domain.services.simulator_engine.simulation_container_service import SimulationContainerService
from app.exceptions.hygge_exceptions import NotFoundException

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


@runs_router.delete(
    path="/{simulation_run_id}/allocation",
    status_code=status.HTTP_204_NO_CONTENT,
)
async def reset_run_allocation(
    simulation_run_id: UUID,
    service: BillSimulationService = GetBillSimulationServiceDep,
    _: UUID = SimulationCreatePermissionDep,
):
    """
    Reset the configuration of a simulation run: deletes the generated
    house bills, the selected policy and its parameters, and clears the
    configured allocation algorithm, so the run can be set up again.

    Args:
        simulation_run_id: The ID of the simulation run to reset.
        service: The BillSimulationService instance.
        _: Dependency to check permission.

    Raises:
        HTTPException: 404 if the run is not found, 400 for other errors.
    """
    try:
        service.reset_run_configuration(simulation_run_id)
    except HTTPException:
        raise
    except NotFoundException as e:
        raise HTTPException(status_code=404, detail=str(e)) from e
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e)) from e


@runs_router.get(
    path="/{container_id}/simulations-runs",
    response_model=List[SimulationRunsResponse],
)
async def get_simulation_runs_by_locality(
    container_id: UUID,
    service: IService = GetSimulationRunServiceDep,
    _: UUID = SimulationRetrievePermissionDep,
):
    """
    Create the simulation run

    Args:
        container_id: Unique ID of simulation container
        service: The simulation run service.
        _: Dependency to check permission.

    Returns:
        Newly Created Simulation

    Raises:
        HTTPException: If an error occurs during retrieval.
    """
    try:
        response = service.filter(simulation_container_id=container_id)
        response.sort(key=lambda x: x.get("created_on", datetime.min))
        return [SimulationRunsResponse.model_validate(i) for i in response]
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e)) from e


@runs_router.get(path="/topology/{root_node_id}/readiness")
async def get_topology_readiness(
    root_node_id: UUID,
    service: IDataPreparationService = Depends(
        get_data_preparation_service
    ),
    _: UUID = SimulationRetrievePermissionDep,
):
    """
    Check whether every house under the given topology root has the
    profiles required to run a billing simulation (load profile required,
    solar profile optional).
    """
    try:
        return service.get_topology_readiness(root_node_id)
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e)) from e


@runs_router.get(
    path="/simulations-runs/{simulation_run_id}",
    response_model=SimulationRunsResponse,
)
async def get_simulation_run(
    simulation_run_id: UUID,
    service: IService = GetSimulationRunServiceDep,
    _: UUID = SimulationRetrievePermissionDep,
):
    """
    Retrieve a single simulation run by its ID.

    Args:
        simulation_run_id: Unique ID of the simulation run.
        service: The simulation run service.
        _: Dependency to check permission.

    Returns:
        The simulation run.

    Raises:
        HTTPException: 404 if the run is not found.
    """
    try:
        response = service.read_or_none(simulation_run_id)
        return SimulationRunsResponse.model_validate(response)
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=404, detail=str(e)) from e


@runs_router.post(
    path="/simulations-runs", response_model=SimulationRunsResponse
)
async def create_simulation_runs(
    data: SimulationRunsRequestModel,
    service: SimulationContainerService = GetSimulationContainerServiceDep,
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


@runs_router.delete(
    path="/{simulation_run_id}/simulations-runs",
    status_code=status.HTTP_204_NO_CONTENT,
)
async def delete_simulation_runs(
    simulation_run_id: UUID,
    service: IService = GetSimulationRunServiceDep,
    _: UUID = SimulationCreatePermissionDep,
):
    """
    Delete a simulation run by its ID.

    Args:
        simulation_run_id: Unique ID of Simulation run to delete
        service: The simulation run service.
        _: Dependency to check permission.

    Raises:
        HTTPException: 404 if the run is not found, 400 for other errors.
    """
    try:
        result = service.delete(simulation_run_id)
        if not result:
            raise HTTPException(
                status_code=404, detail="Simulation run not found"
            )
    except HTTPException:
        raise
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
