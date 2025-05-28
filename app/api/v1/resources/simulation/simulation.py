from fastapi import APIRouter, Depends, HTTPException
from fastapi.params import Depends
from uuid import UUID
from app.api.authorization.authorization import permission
from app.api.authorization.enums import Resources, Permission
from app.api.v1.dependencies.container_instance import get_simulation_algorithm_service, \
    get_net_metering_algorithm_service, get_simulation_runs_service, get_net_metering_policy_service, \
    get_gross_metering_policy_service, get_tou_rate_policy_service, get_simulation_selected_policy_service, \
    get_house_bill_service
from app.api.v1.models.requests.simulation_request import SimulationRunsRequestModel, NetMeteringRequestModel, \
    GrossMeteringRequestModel, TimeOfUseRequestModel, SimulationSelectedRequestModel, HouseBillRequestModel, \
    SimulationRunsUpdateModel, NetMeteringUpdateModel, GrossMeteringUpdateModel, TimeOfUseUpdateModel, \
    SimulationSelectedUpdateModel, HouseBillUpdateModel
from app.api.v1.models.responses.simulation_response import SimulationAlgorithmResponse, \
    SimulationAlgorithmListResponse, NetMeteringAlgorithmListResponse, NetMeteringAlgorithmResponse, \
    NetMeteringPolicyResponse, SimulationRunsResponse, GrossMeteringPolicyResponse, TimeOfUseResponse, \
    SimulationSelectedResponse, HouseBillResponse
from app.domain.interfaces.i_service import IService

simulation_router = APIRouter(tags=["Simulation"])
GetSimulationAlgorithmServiceDep = Depends(get_simulation_algorithm_service)
GetNetMeteringAlgorithmServiceDep = Depends(get_net_metering_algorithm_service)
GetSimulationRunServiceDep = Depends(get_simulation_runs_service)
GetNetMeteringPolicyServiceDep = Depends(get_net_metering_policy_service)
GetGrossMeteringPolicyServiceDep = Depends(get_gross_metering_policy_service)
GetTOURatePolicyServiceDep = Depends(get_tou_rate_policy_service)
GetSimulationSelectedPolicyServiceDep = Depends(get_simulation_selected_policy_service)
GetHouseBillServiceDep = Depends(get_house_bill_service)
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


@simulation_router.get(path="/net-metering/algo", response_model=NetMeteringAlgorithmListResponse)
async def get_net_metering_algorithm(
        service: IService = GetNetMeteringAlgorithmServiceDep,
        _: UUID = SimulationAlgorithmRetrievePermissionDep
):
    """
       Retrieve the net metering algorithm type

       Args:
           service: The net metering algorithm service.
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

@simulation_router.post(path="/simulations-runs", response_model=SimulationRunsResponse)
async def create_simulation_runs(
        data: SimulationRunsRequestModel,
        service: IService = GetSimulationRunServiceDep,
        user_id: UUID = SimulationAlgorithmRetrievePermissionDep
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
        data = data.model_dump()
        response = service.create(user_id, **data)
        return SimulationRunsResponse(**response)
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e)) from e


@simulation_router.put(path="/update/{simulation_run_id}/simulations-runs",
                       response_model=SimulationRunsResponse)
async def update_simulation_runs(
        simulation_run_id: UUID,
        data: SimulationRunsUpdateModel,
        service: IService = GetSimulationRunServiceDep,
        user_id: UUID = SimulationAlgorithmRetrievePermissionDep
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
        data = data.model_dump(exclude_unset=True)
        response = service.update(user_id, simulation_run_id, **data)
        return SimulationRunsResponse(**response)
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e)) from e


@simulation_router.post(path="/policy/net-metering", response_model=NetMeteringPolicyResponse)
async def create_net_metering_policy(
        data: NetMeteringRequestModel,
        service: IService = GetNetMeteringPolicyServiceDep,
        user_id: UUID = SimulationAlgorithmRetrievePermissionDep
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
        data = data.model_dump()
        response = service.create(user_id, **data)
        return NetMeteringPolicyResponse(**response)
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e)) from e

@simulation_router.put(path="/update/{simulation_run_id}/net-metering",
                       response_model=NetMeteringPolicyResponse)
async def update_net_metering_policy(
        simulation_run_id: UUID,
        data: NetMeteringUpdateModel,
        service: IService = GetNetMeteringPolicyServiceDep,
        user_id: UUID = SimulationAlgorithmRetrievePermissionDep
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
        data = data.model_dump(exclude_unset=True)
        response = service.update(user_id, simulation_run_id, **data)
        return NetMeteringPolicyResponse(**response)
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e)) from e

@simulation_router.post(path="/policy/gross-metering", response_model=GrossMeteringPolicyResponse)
async def create_gross_metering_policy(
        data: GrossMeteringRequestModel,
        service: IService = GetGrossMeteringPolicyServiceDep,
        user_id: UUID = SimulationAlgorithmRetrievePermissionDep
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
        data = data.model_dump()
        response = service.create(user_id, **data)
        return GrossMeteringPolicyResponse(**response)
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e)) from e

@simulation_router.put(path="/update/{simulation_run_id}/gross-metering",
                       response_model=GrossMeteringPolicyResponse)
async def update_gross_metering_policy(
        simulation_run_id: UUID,
        data: GrossMeteringUpdateModel,
        service: IService = GetGrossMeteringPolicyServiceDep,
        user_id: UUID = SimulationAlgorithmRetrievePermissionDep
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
        data = data.model_dump(exclude_unset=True)
        response = service.update(user_id, simulation_run_id, **data)
        return GrossMeteringPolicyResponse(**response)
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e)) from e

@simulation_router.post(path="/policy/tou", response_model=TimeOfUseResponse)
async def create_tou_metering_policy(
        data: TimeOfUseRequestModel,
        service: IService = GetTOURatePolicyServiceDep,
        user_id: UUID = SimulationAlgorithmRetrievePermissionDep
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
        data = data.model_dump()
        response = service.create(user_id, **data)
        return TimeOfUseResponse(**response)
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e)) from e

@simulation_router.put(path="/update/{tou_id}/tou", response_model=TimeOfUseResponse)
async def update_tou_metering_policy(
        tou_id: UUID,
        data: TimeOfUseUpdateModel,
        service: IService = GetTOURatePolicyServiceDep,
        user_id: UUID = SimulationAlgorithmRetrievePermissionDep
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
        data = data.model_dump(exclude_unset=True)
        response = service.update(user_id, tou_id, **data)
        return TimeOfUseResponse(**response)
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e)) from e

@simulation_router.post(path="/selected/policies", response_model=SimulationSelectedResponse)
async def create_simulation_selected_policy(
        data: SimulationSelectedRequestModel,
        service: IService = GetSimulationSelectedPolicyServiceDep,
        user_id: UUID = SimulationAlgorithmRetrievePermissionDep
):
    """
                Create Simulation selected policies

                Args:
                    data: data to create simulation selected policies
                    service: The simulation selected policy service.
                    user_id: Dependency to check permission.

                Returns:
                    Created data from simulation selected table

                Raises:
                    HTTPException: If an error occurs during retrieval.
    """
    try:
        data = data.model_dump()
        response = service.create(user_id, **data)
        return SimulationSelectedResponse(**response)
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e)) from e


@simulation_router.put(path="/update/{simulation_run_id}/policies", response_model=SimulationSelectedResponse)
async def update_simulation_selected_policy(
        simulation_run_id: UUID,
        data: SimulationSelectedUpdateModel,
        service: IService = GetSimulationSelectedPolicyServiceDep,
        user_id: UUID = SimulationAlgorithmRetrievePermissionDep
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
        data = data.model_dump(exclude_unset=True)
        response = service.update(user_id, simulation_run_id, **data)
        return SimulationSelectedResponse(**response)
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e)) from e


@simulation_router.get(path="/{house_bill_id}/house-bill", response_model=HouseBillResponse)
async def get_house_bill(
        house_bill_id: UUID,
        service: IService = GetHouseBillServiceDep,
        _: UUID = SimulationAlgorithmRetrievePermissionDep
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
        response = service.read(house_bill_id)
        return HouseBillResponse(**response)
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e)) from e

@simulation_router.post(path="/house-bill", response_model=HouseBillResponse)
async def generate_house_bill(
        data: HouseBillRequestModel,
        service: IService = GetHouseBillServiceDep,
        user_id: UUID = SimulationAlgorithmRetrievePermissionDep
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
        data = data.model_dump()
        response = service.create(user_id, **data)
        return HouseBillResponse(**response)
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e)) from e


@simulation_router.put(path="/update/{simulation_run_id}/house-bill", response_model=HouseBillResponse)
async def update_house_bill(
        simulation_run_id: UUID,
        data: HouseBillUpdateModel,
        service: IService = GetHouseBillServiceDep,
        user_id: UUID = SimulationAlgorithmRetrievePermissionDep
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
        data = data.model_dump(exclude_unset=True)
        response = service.update(user_id, simulation_run_id, **data)
        return HouseBillResponse(**response)
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e)) from e



