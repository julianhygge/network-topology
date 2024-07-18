from fastapi import APIRouter, Depends, HTTPException
from starlette import status
from app.api.authorization.authorization import permission
from app.api.authorization.enums import Resources, Permission
from app.api.v1.models.responses.breadcrumb import BreadcrumbResponseModel
from app.domain.interfaces.inode_service import INodeService
from app.api.v1.dependencies.container_instance import get_node_service
from app.exceptions.hygge_exceptions import NotFoundException
from uuid import UUID

breadcrumb_router = APIRouter(tags=["Breadcrumbs"])

@breadcrumb_router.get("/nodes/{node_id}/breadcrumb",response_model=BreadcrumbResponseModel)
async def get_breadcrumb(node_id: UUID, 
                         _: str = Depends(permission(Resources.Substations, Permission.Update)),
                         service: INodeService = Depends(get_node_service)):
    try:
        breadcrumb = service.get_breadcrumb_navigation_path(node_id)
        return breadcrumb
    except Exception as e:
        raise HTTPException(status_code=404, detail=str(e))