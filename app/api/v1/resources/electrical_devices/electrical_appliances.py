"""API endpoints for managing electrical appliances."""
from fastapi import APIRouter, Depends, HTTPException

from app.api.authorization.authorization import permission
from app.api.authorization.enums import Permission, Resources
from app.api.v1.dependencies.container_instance import \
    get_electrical_appliances_service
from app.api.v1.models.requests.electrical_appliances import AppliancesRequest
from app.api.v1.models.responses.electrical_appliances import (
    AppliancesListResponse, AppliancesResponse)
from app.domain.interfaces.i_service import IService

appliances_router = APIRouter(tags=['Appliances'])


@appliances_router.get('/', response_model=AppliancesListResponse)
async def get_appliances(
    service: IService = Depends(get_electrical_appliances_service),
    _: str = Depends(permission(Resources.ELECTRICALS, Permission.RETRIEVE)),
):
    """
    Retrieve a list of all electrical appliances.

    Args:
        service: The electrical appliances service.
        _: Dependency to check retrieve permission.

    Returns:
        A list of electrical appliances.

    Raises:
        HTTPException: If an error occurs during retrieval.
    """
    try:
        body = service.list_all()
        response = AppliancesListResponse(items=[AppliancesResponse(**item) for item in body])
        return response
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e)) from e


@appliances_router.post('/', response_model=AppliancesResponse)
async def create_appliances(
    data: AppliancesRequest,
    service: IService = Depends(get_electrical_appliances_service),
    user_id: str = Depends(permission(Resources.ELECTRICALS, Permission.CREATE)),
):
    """
    Create a new electrical appliance.

    Args:
        data: The request data for the appliance.
        service: The electrical appliances service.
        user_id: The ID of the user creating the appliance.

    Returns:
        The created electrical appliance.

    Raises:
        HTTPException: If an error occurs during creation.
    """
    try:
        data = data.model_dump()
        body = service.create(user_id, **data)
        return AppliancesResponse(**body)
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e)) from e


@appliances_router.put('/{appliance_id}/update')
async def update_appliances(
    data: AppliancesRequest,
    appliance_id: int,
    service: IService = Depends(get_electrical_appliances_service),
    user_id: str = Depends(permission(Resources.ELECTRICALS, Permission.UPDATE)),
):
    """
    Update an existing electrical appliance.

    Args:
        data: The request data for the appliance update.
        appliance_id: The ID of the appliance to update.
        service: The electrical appliances service.
        user_id: The ID of the user updating the appliance.

    Returns:
        The updated electrical appliance.

    Raises:
        HTTPException: If an error occurs during the update.
    """
    try:
        data = data.model_dump(exclude_unset=True)
        body = service.update(user_id, appliance_id, **data)
        return body
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e)) from e


@appliances_router.delete('/{appliance_id}/delete')
async def delete_appliance(
    appliance_id: int,
    service: IService = Depends(get_electrical_appliances_service),
    _: str = Depends(permission(Resources.ELECTRICALS, Permission.DELETE)),
):
    """
    Delete an electrical appliance.

    Args:
        appliance_id: The ID of the appliance to delete.
        service: The electrical appliances service.
        _: Dependency to check deletion permission.

    Raises:
        HTTPException: If an error occurs during deletion.
    """
    try:
        service.delete(appliance_id)
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e)) from e
