import datetime
from typing import List
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException

from app.api.authorization.authorization import permission
from app.api.authorization.enums import Permission, Resources
from app.api.v1.dependencies.container_instance import (
    get_bill_simulation_service,
    get_gross_metering_policy_service,
    get_house_bill_service,
    get_net_metering_algorithm_service,
    get_net_metering_policy_service,
    get_simulation_algorithm_service,
    get_simulation_runs_service,
    get_simulation_selected_policy_service,
    get_tou_rate_policy_service,
)
from app.api.v1.models.requests.simulation_request import (
    GrossMeteringRequestModel,
    GrossMeteringUpdateModel,
    HouseBillRequestModel,
    HouseBillUpdateModel,
    NetMeteringRequestModel,
    NetMeteringUpdateModel,
    SimulationRunsRequestModel,
    SimulationRunsUpdateModel,
    SimulationSelectedRequestModel,
    SimulationSelectedUpdateModel,
    TimeOfUseRequestModel,
    TimeOfUseUpdateModel,
)
from app.api.v1.models.responses.simulation_response import (
    GrossMeteringPolicyResponse,
    HouseBillResponse,
    NetMeteringAlgorithmListResponse,
    NetMeteringAlgorithmResponse,
    NetMeteringPolicyResponse,
    SimulationAlgorithmListResponse,
    SimulationAlgorithmResponse,
    SimulationRunsResponse,
    SimulationSelectedResponse,
    TimeOfUseResponse,
)
from app.api.v1.models.responses.simulation_responses import (
    EnergySummaryResponse,
)
from app.domain.interfaces.i_service import (
    IService,  # May not be needed if BillSimulationService is directly typed
)
from app.domain.services.simulator_engine.bill_simulation_service import (
    BillSimulationService,
)

simulation_router = APIRouter(tags=["Simulation"])
GetSimulationAlgorithmServiceDep = Depends(get_simulation_algorithm_service)
GetNetMeteringAlgorithmServiceDep = Depends(get_net_metering_algorithm_service)
GetSimulationRunServiceDep = Depends(get_simulation_runs_service)
GetNetMeteringPolicyServiceDep = Depends(get_net_metering_policy_service)
GetGrossMeteringPolicyServiceDep = Depends(get_gross_metering_policy_service)
GetTOURatePolicyServiceDep = Depends(get_tou_rate_policy_service)
GetSimulationSelectedPolicyServiceDep = Depends(
    get_simulation_selected_policy_service
)
GetHouseBillServiceDep = Depends(get_house_bill_service)
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


@simulation_router.get(
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
            items=[SimulationAlgorithmResponse(**item) for item in body]
        )
        return response
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e)) from e


@simulation_router.post(
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
        # The service method is synchronous,
        # but FastAPI can run it in a thread pool
        # if it's defined as `async def` or if we use `run_in_threadpool`.
        # For now, keeping it simple. If it's long-running,
        # background tasks would be better.
        service.calculate_bills_for_simulation_run(run_id=simulation_run_id)
        return {
            "message": "Bill calculation started"
            "for simulation run {simulation_run_id}"
        }
    except HTTPException as http_exc:  # Re-raise HTTPException
        raise http_exc
    except Exception as e:
        # Log the exception e
        raise HTTPException(
            status_code=500,
            detail=f"Error triggering bill calculation: {str(e)}",
        ) from e


@simulation_router.get(
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
            items=[NetMeteringAlgorithmResponse(**item) for item in body]
        )
        return response
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e)) from e


@simulation_router.get(
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
        locality_id: Unique ID of locality
        service: The simulation run service.
        _: Dependency to check permission.

    Returns:
        Newly Created Simulation

    Raises:
        HTTPException: If an error occurs during retrieval.
    """
    try:
        response = service.filter(locality_id=locality_id)
        return [SimulationRunsResponse(**item) for item in response]
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e)) from e


@simulation_router.post(
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
        return SimulationRunsResponse(**response)
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e)) from e


@simulation_router.put(
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
        return SimulationRunsResponse(**response)
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e)) from e


@simulation_router.get(
    path="/{simulation_run_id}/policy/net-metering",
    response_model=NetMeteringPolicyResponse,
)
async def get_net_metering_policy(
    simulation_run_id: UUID,
    service: IService = GetNetMeteringPolicyServiceDep,
    _: UUID = SimulationRetrievePermissionDep,
):
    """
    Create Net Metering Policy

    Args:
        simulation_run_id: Unique ID of Simulation run
        service: The net metering policy service.
        _: Dependency to check permission.

    Returns:
        Newly created data from net metering policy table

    Raises:
        HTTPException: If an error occurs during retrieval.
    """
    try:
        data = service.read_or_none(simulation_run_id)
        return NetMeteringPolicyResponse(**data)
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e)) from e


@simulation_router.post(
    path="/policy/net-metering", response_model=NetMeteringPolicyResponse
)
async def create_net_metering_policy(
    data: NetMeteringRequestModel,
    service: IService = GetNetMeteringPolicyServiceDep,
    user_id: UUID = SimulationCreatePermissionDep,
):
    """
    Create Net Metering Policy

    Args:
        data: data to create simulation runs
        service: The net metering policy service.
        user_id: Dependency to check permission.

    Returns:
        Newly created data from net metering policy table

    Raises:
        HTTPException: If an error occurs during retrieval.
    """
    try:
        data_dicts = data.model_dump()
        response = service.create(user_id, **data_dicts)
        return NetMeteringPolicyResponse(**response)
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e)) from e


@simulation_router.put(
    path="/{simulation_run_id}/net-metering",
    response_model=NetMeteringPolicyResponse,
)
async def update_net_metering_policy(
    simulation_run_id: UUID,
    data: NetMeteringUpdateModel,
    service: IService = GetNetMeteringPolicyServiceDep,
    user_id: UUID = SimulationUpdatePermissionDep,
):
    """
    Update Net Metering Policy

    Args:
        simulation_run_id: Unique ID of Simulation run to update
        data: data to create simulation runs
        service: The net metering policy service.
        user_id: Dependency to check permission.

    Returns:
        Updated data from net metering policy table

    Raises:
        HTTPException: If an error occurs during retrieval.
    """
    try:
        data_dicts = data.model_dump(exclude_unset=True)
        response = service.update(user_id, simulation_run_id, **data_dicts)
        return NetMeteringPolicyResponse(**response)
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e)) from e


@simulation_router.get(
    path="/{simulation_run_id}/policy/gross-metering",
    response_model=GrossMeteringPolicyResponse,
)
async def get_gross_metering_policy(
    simulation_run_id: UUID,
    service: IService = GetGrossMeteringPolicyServiceDep,
    _: UUID = SimulationRetrievePermissionDep,
):
    """
    Create Gross Metering Policy

    Args:
        simulation_run_id: Unique ID of simulation run
        service: The gross metering policy service.
        _: Dependency to check permission.

    Returns:
        Newly created data from gross metering policy table

    Raises:
        HTTPException: If an error occurs during retrieval.
    """
    try:
        response = service.read_or_none(simulation_run_id)
        return GrossMeteringPolicyResponse(**response)
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e)) from e


@simulation_router.post(
    path="/policy/gross-metering", response_model=GrossMeteringPolicyResponse
)
async def create_gross_metering_policy(
    data: GrossMeteringRequestModel,
    service: IService = GetGrossMeteringPolicyServiceDep,
    user_id: UUID = SimulationCreatePermissionDep,
):
    """
    Create Gross Metering Policy

    Args:
        data: data to create gross metering policy
        service: The gross metering policy service.
        user_id: Dependency to check permission.

    Returns:
        Newly created data from gross metering policy table

    Raises:
        HTTPException: If an error occurs during retrieval.
    """
    try:
        data_dicts = data.model_dump()
        response = service.create(user_id, **data_dicts)
        return GrossMeteringPolicyResponse(**response)
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e)) from e


@simulation_router.put(
    path="/{simulation_run_id}/gross-metering",
    response_model=GrossMeteringPolicyResponse,
)
async def update_gross_metering_policy(
    simulation_run_id: UUID,
    data: GrossMeteringUpdateModel,
    service: IService = GetGrossMeteringPolicyServiceDep,
    user_id: UUID = SimulationUpdatePermissionDep,
):
    """
    Update Gross Metering Policy

    Args:
        simulation_run_id: Unique ID of Simulation run to update
        data: data to update gross metering policy
        service: The gross metering policy service.
        user_id: Dependency to check permission.

    Returns:
        Updated data from gross metering policy table

    Raises:
        HTTPException: If an error occurs during retrieval.
    """
    try:
        data_dicts = data.model_dump(exclude_unset=True)
        response = service.update(user_id, simulation_run_id, **data_dicts)
        return GrossMeteringPolicyResponse(**response)
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e)) from e


@simulation_router.get(
    path="/{simulation_run_id}/policy/tou",
    response_model=List[TimeOfUseResponse],
)
async def get_tou_metering_policy(
    simulation_run_id: UUID,
    service: IService = GetTOURatePolicyServiceDep,
    _: UUID = SimulationRetrievePermissionDep,
):
    """
    Create Time of Use Rate Policy

    Args:
        simulation_run_id: Unique ID of simulation run
        service: The time of use rate policy service.
        _: Dependency to check permission.

    Returns:
        Created data from time of use rate policy table

    Raises:
        HTTPException: If an error occurs during retrieval.
    """
    try:
        response = service.filter(simulation_run_id=simulation_run_id)
        return [TimeOfUseResponse(**item) for item in response]
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e)) from e


@simulation_router.post(path="/policy/tou", response_model=TimeOfUseResponse)
async def create_tou_metering_policy(
    data: TimeOfUseRequestModel,
    service: IService = GetTOURatePolicyServiceDep,
    user_id: UUID = SimulationCreatePermissionDep,
):
    """
    Create Time of Use Rate Policy

    Args:
        data: data to time of use rate policy
        service: The time of use rate policy service.
        user_id: Dependency to check permission.

    Returns:
        Created data from time of use rate policy table

    Raises:
        HTTPException: If an error occurs during retrieval.
    """
    try:
        data_dicts = data.model_dump()
        response = service.create(user_id, **data_dicts)
        return TimeOfUseResponse(**response)
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e)) from e


@simulation_router.put(path="/{tou_id}/tou", response_model=TimeOfUseResponse)
async def update_tou_metering_policy(
    tou_id: UUID,
    data: TimeOfUseUpdateModel,
    service: IService = GetTOURatePolicyServiceDep,
    user_id: UUID = SimulationUpdatePermissionDep,
):
    """
    Update time of use rate Policy

    Args:
        tou_id: Unique ID of Simulation run to update
        data: data to update time of use rate policy
        service: The time of use rate policy service.
        user_id: Dependency to check permission.

    Returns:
        Updated data from time of use rate policy table

    Raises:
        HTTPException: If an error occurs during retrieval.
    """
    try:
        data_dicts = data.model_dump(exclude_unset=True)
        response = service.update(user_id, tou_id, **data_dicts)
        return TimeOfUseResponse(**response)
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e)) from e


@simulation_router.delete(path="/{tou_id}/policy/tou")
async def delete_tou_metering_policy(
    tou_id: UUID,
    service: IService = GetTOURatePolicyServiceDep,
    _: UUID = SimulationRetrievePermissionDep,
):
    """
    Create Time of Use Rate Policy

    Args:
        tou_id: Unique ID of simulation run
        service: The time of use rate policy service.
        _: Dependency to check permission.

    Returns:
        Created data from time of use rate policy table

    Raises:
        HTTPException: If an error occurs during retrieval.
    """
    try:
        service.delete(tou_id)
        return f"Id {tou_id} deleted successfully"
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e)) from e


@simulation_router.get(
    path="/{simulation_run_id}/selected/policy",
    response_model=SimulationSelectedResponse,
)
async def get_simulation_selected_policy(
    simulation_run_id: UUID,
    service: IService = GetSimulationSelectedPolicyServiceDep,
    _: UUID = SimulationRetrievePermissionDep,
):
    """
    Create Simulation selected policy

    Args:
        simulation_run_id: Unique ID of simulation run
        service: The simulation selected policy service.
        _: Dependency to check permission.

    Returns:
        Created data from simulation selected table

    Raises:
        HTTPException: If an error occurs during retrieval.
    """
    try:
        response = service.read_or_none(simulation_run_id)
        return SimulationSelectedResponse(**response)
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e)) from e


@simulation_router.post(
    path="/selected/policy", response_model=SimulationSelectedResponse
)
async def create_simulation_selected_policy(
    data: SimulationSelectedRequestModel,
    service: IService = GetSimulationSelectedPolicyServiceDep,
    user_id: UUID = SimulationCreatePermissionDep,
):
    """
    Create Simulation selected policy

    Args:
        data: data to create simulation selected policy
        service: The simulation selected policy service.
        user_id: Dependency to check permission.

    Returns:
        Created data from simulation selected table

    Raises:
        HTTPException: If an error occurs during retrieval.
    """
    try:
        data_dicts = data.model_dump()
        response = service.create(user_id, **data_dicts)
        return SimulationSelectedResponse(**response)
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e)) from e


@simulation_router.put(
    path="/{simulation_run_id}/policies",
    response_model=SimulationSelectedResponse,
)
async def update_simulation_selected_policy(
    simulation_run_id: UUID,
    data: SimulationSelectedUpdateModel,
    service: IService = GetSimulationSelectedPolicyServiceDep,
    user_id: UUID = SimulationUpdatePermissionDep,
):
    """
    Update Simulation selected policy table

    Args:
        simulation_run_id: Unique ID of Simulation run to update
        data: data to update selected simulation policy
        service: The simulation selection policy service.
        user_id: Dependency to check permission.

    Returns:
        Updated data from simulation selection policy table

    Raises:
        HTTPException: If an error occurs during retrieval.
    """
    try:
        data_dicts = data.model_dump(exclude_unset=True)
        response = service.update(user_id, simulation_run_id, **data_dicts)
        return SimulationSelectedResponse(**response)
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e)) from e


@simulation_router.get(
    path="/{house_bill_id}/house-bill", response_model=HouseBillResponse
)
async def get_house_bill(
    house_bill_id: UUID,
    service: IService = GetHouseBillServiceDep,
    _: UUID = SimulationRetrievePermissionDep,
):
    """
    Retrieve house bill

    Args:
        house_bill_id: Unique ID of house bill table
        service: The net metering policy service.
        _: Dependency to check permission.

    Returns:
        Get house bill of particular id

    Raises:
        HTTPException: If an error occurs during retrieval.
    """
    try:
        response = service.read_or_none(house_bill_id)
        return HouseBillResponse(**response)
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e)) from e


@simulation_router.post(path="/house-bill", response_model=HouseBillResponse)
async def generate_house_bill(
    data: HouseBillRequestModel,
    service: IService = GetHouseBillServiceDep,
    user_id: UUID = SimulationCreatePermissionDep,
):
    """
    Generate house bill

    Args:
        data: data to create house bill
        service: The house bill service.
        user_id: Dependency to check permission.

    Returns:
        Newly generated  house bill

    Raises:
        HTTPException: If an error occurs during retrieval.
    """
    try:
        data_dicts = data.model_dump()
        response = service.create(user_id, **data_dicts)
        return HouseBillResponse(**response)
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e)) from e


@simulation_router.put(
    path="/{simulation_run_id}/house-bill", response_model=HouseBillResponse
)
async def update_house_bill(
    simulation_run_id: UUID,
    data: HouseBillUpdateModel,
    service: IService = GetHouseBillServiceDep,
    user_id: UUID = SimulationUpdatePermissionDep,
):
    """
    Update house bill

    Args:
        simulation_run_id: Unique ID of simulation run
        data: data to update house bill
        service: The house bill service.
        user_id: Dependency to check permission.

    Returns:
        Updated house bill

    Raises:
        HTTPException: If an error occurs during retrieval.
    """
    try:
        data_dicts = data.model_dump(exclude_unset=True)
        response = service.update(user_id, simulation_run_id, **data_dicts)
        return HouseBillResponse(**response)
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e)) from e


@simulation_router.get(
    path="/houses/{house_id}/energy-summary",
    response_model=EnergySummaryResponse,
)
async def get_house_energy_summary(
    house_id: UUID,
    start_datetime: datetime.datetime,
    end_datetime: datetime.datetime,
    service: BillSimulationService = GetBillSimulationServiceDep,
    _: UUID = SimulationRetrievePermissionDep,
):
    """
    Retrieve the total imported and exported energy for a specific house
    for a given datetime range.
    """
    try:
        summary = service.get_house_energy_summary(
            house_id, start_datetime, end_datetime
        )
        return EnergySummaryResponse(**summary)
    except HTTPException as http_exc:
        raise http_exc
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e)) from e


@simulation_router.get(
    path="/nodes/{node_id}/energy-summary",
    response_model=EnergySummaryResponse,
)
async def get_node_energy_summary(
    node_id: UUID,
    start_datetime: datetime.datetime,
    end_datetime: datetime.datetime,
    service: BillSimulationService = GetBillSimulationServiceDep,
    _: UUID = SimulationRetrievePermissionDep,
):
    """
    Retrieve the total imported and exported energy for all houses under a
    specific node (Locality, substation, substation, or a house itself)
    for a given datetime range.
    """
    try:
        summary = service.get_node_energy_summary(
            node_id, start_datetime, end_datetime
        )
        return EnergySummaryResponse(**summary)
    except HTTPException as http_exc:
        raise http_exc
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e)) from e
