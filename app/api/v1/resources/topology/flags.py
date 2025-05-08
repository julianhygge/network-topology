from typing import Any, Dict, List
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException
from pydantic import UUID4
from starlette import status

from app.api.authorization.authorization import permission
from app.api.authorization.enums import Permission, Resources
from app.api.v1.dependencies.container_instance import get_flag_service
from app.domain.interfaces.i_service import IService
from app.exceptions.hygge_exceptions import NotFoundException

flag_router = APIRouter(tags=["Flags"])


@flag_router.get("/{house_id}/flags")
async def get_flags(
    house_id: UUID4,
    _: str = Depends(permission(Resources.HOUSES, Permission.RETRIEVE)),
    service: IService[UUID, UUID] = Depends(get_flag_service),
) -> List[Dict[str, Any]]:
    """
    Retrieve the flags of a specific house node.
    Flags are used to give priority when allocating energy to houses.
    Requires retrieve permission on the Houses resource.

    Args:
        house_id: The ID of the house to retrieve.
        _: Placeholder for permission dependency.
        service: Injected flag service instance.

    Returns:
        A list of dictionaries representing the flags of the specified house.

    Raises:
        HTTPException: If the house is not found (404).
    """
    try:
        data = service.filter()
        return data
    except NotFoundException as e:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail=str(e)
        ) from e
