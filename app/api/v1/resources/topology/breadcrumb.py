"""API endpoints for retrieving breadcrumb navigation paths."""

from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, status

from app.api.authorization.authorization import permission
from app.api.authorization.enums import Permission, Resources
from app.api.v1.dependencies.container_instance import get_node_service
from app.api.v1.models.responses.breadcrumb import BreadcrumbResponseModel
from app.domain.interfaces.i_node_service import INodeService
from app.exceptions.hygge_exceptions import NotFoundException
from app.utils.logger import logger

breadcrumb_router = APIRouter(tags=["Breadcrumbs"])


@breadcrumb_router.get(
    "/nodes/{node_id}/breadcrumb", response_model=BreadcrumbResponseModel
)
async def get_breadcrumb(
    node_id: UUID,
    _: str = Depends(permission(Resources.SUBSTATIONS, Permission.RETRIEVE)),
    service: INodeService = Depends(get_node_service),
) -> BreadcrumbResponseModel:
    """
    Retrieve the breadcrumb navigation path for a given topology node.

    Requires retrieve permission on the Substations resource (as breadcrumbs
    are typically viewed within the context of the topology).

    Args:
        node_id: The ID of the node for which to get the breadcrumb path.
        _: Placeholder for permission dependency.
        service: Injected node service instance.

    Returns:
        The breadcrumb navigation path details.

    Raises:
        HTTPException: If the node is not found (404) or another error occurs.
    """
    try:
        breadcrumb = service.get_breadcrumb_navigation_path(node_id)
        if (
            breadcrumb is None
        ):  # Assuming service might return None if not found
            raise NotFoundException(f"Node with ID {node_id} not found.")
        return breadcrumb
    except NotFoundException as e:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail=str(e)
        ) from e
    except Exception as e:
        logger.exception(
            "Error retrieving breadcrumb for node %s: %s", node_id, e
        )
        # Use a more generic error for unexpected issues
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="An error occurred while retrieving breadcrumb.",
        ) from e
