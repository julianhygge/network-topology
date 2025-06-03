from typing import List
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException

from app.api.authorization.authorization import permission
from app.api.authorization.enums import Permission, Resources
from app.api.v1.dependencies.container_instance import (
    get_gross_metering_policy_service,
    get_net_metering_policy_service,
    get_simulation_selected_policy_service,
    get_tou_rate_policy_service,
)
from app.api.v1.models.requests.simulation_request import (
    GrossMeteringRequestModel,
    GrossMeteringUpdateModel,
    NetMeteringRequestModel,
    NetMeteringUpdateModel,
    SimulationSelectedRequestModel,
    SimulationSelectedUpdateModel,
    TimeOfUseRequestModel,
    TimeOfUseUpdateModel,
)
from app.api.v1.models.responses.simulation_response import (
    GrossMeteringPolicyResponse,
    NetMeteringPolicyResponse,
    SimulationSelectedResponse,
    TimeOfUseResponse,
)
from app.domain.interfaces.i_service import IService

policies_router = APIRouter()

GetNetMeteringPolicyServiceDep = Depends(get_net_metering_policy_service)
GetGrossMeteringPolicyServiceDep = Depends(get_gross_metering_policy_service)
GetTOURatePolicyServiceDep = Depends(get_tou_rate_policy_service)
GetSimulationSelectedPolicyServiceDep = Depends(
    get_simulation_selected_policy_service
)

SimulationRetrievePermissionDep = Depends(
    permission(Resources.SIMULATION, Permission.RETRIEVE)
)
SimulationCreatePermissionDep = Depends(
    permission(Resources.SIMULATION, Permission.CREATE)
)
SimulationUpdatePermissionDep = Depends(
    permission(Resources.SIMULATION, Permission.UPDATE)
)


@policies_router.get(
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
        return NetMeteringPolicyResponse.model_validate(data)
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e)) from e


@policies_router.post(
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
        return NetMeteringPolicyResponse.model_validate(response)
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e)) from e


@policies_router.put(
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
        return NetMeteringPolicyResponse.model_validate(response)
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e)) from e


@policies_router.get(
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
        return GrossMeteringPolicyResponse.model_validate(response)
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e)) from e


@policies_router.post(
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
        return GrossMeteringPolicyResponse.model_validate(response)
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e)) from e


@policies_router.put(
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
        return GrossMeteringPolicyResponse.model_validate(response)
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e)) from e


@policies_router.get(
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
        return [TimeOfUseResponse.model_validate(item) for item in response]
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e)) from e


@policies_router.post(path="/policy/tou", response_model=TimeOfUseResponse)
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
        return TimeOfUseResponse.model_validate(response)
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e)) from e


@policies_router.put(path="/{tou_id}/tou", response_model=TimeOfUseResponse)
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
        return TimeOfUseResponse.model_validate(response)
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e)) from e


@policies_router.delete(path="/{tou_id}/policy/tou")
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


@policies_router.get(
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
        return SimulationSelectedResponse.model_validate(response)
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e)) from e


@policies_router.post(
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
        return SimulationSelectedResponse.model_validate(response)
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e)) from e


@policies_router.put(
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
        return SimulationSelectedResponse.model_validate(response)
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e)) from e
