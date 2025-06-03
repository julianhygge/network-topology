from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException

from app.api.authorization.authorization import permission
from app.api.authorization.enums import Permission, Resources
from app.api.v1.dependencies.container_instance import get_house_bill_service
from app.api.v1.models.requests.simulation_request import (
    HouseBillRequestModel,
    HouseBillUpdateModel,
)
from app.api.v1.models.responses.simulation_response import (
    HouseBillResponse,
)
from app.domain.interfaces.i_service import IService

bills_router = APIRouter()

GetHouseBillServiceDep = Depends(get_house_bill_service)

SimulationRetrievePermissionDep = Depends(
    permission(Resources.SIMULATION, Permission.RETRIEVE)
)
SimulationCreatePermissionDep = Depends(
    permission(Resources.SIMULATION, Permission.CREATE)
)
SimulationUpdatePermissionDep = Depends(
    permission(Resources.SIMULATION, Permission.UPDATE)
)


@bills_router.get(
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
        return HouseBillResponse.model_validate(response)
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e)) from e


@bills_router.post(path="/house-bill", response_model=HouseBillResponse)
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
        return HouseBillResponse.model_validate(response)
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e)) from e


@bills_router.put(
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
        return HouseBillResponse.model_validate(response)
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e)) from e
