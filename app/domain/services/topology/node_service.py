from uuid import UUID
from typing import Dict, Any, Optional
from app.data.interfaces.topology.inode_repository import INodeRepository
from app.api.v1.models.responses.breadcrumb import BreadcrumbResponseModel, BreadcrumbItem
from app.domain.interfaces.inode_service import INodeService

class NodeService(INodeService):
    def __init__(self, node_repo: INodeRepository):
        self.node_repo = node_repo

    def read(self, item_id: UUID) -> Optional[Dict[str, Any]]:
        node = self.node_repo.read(item_id)
        if node:
            return {
                "id": node.id,
                "name": node.name,
                "nomenclature": node.nomenclature
            }
        return None

    def get_breadcrumb_navigation_path(self, node_id: UUID) -> BreadcrumbResponseModel:
        path = []
        current_node = self.node_repo.read(node_id)

        while current_node:
            path.append(BreadcrumbItem(
                id=current_node.id,
                name=current_node.name,
                nomenclature=current_node.nomenclature
            ))
            current_node = self.node_repo.get_parent(current_node.id)

        path.reverse()

        locality = path[0].name if path else "Unknown Locality"
        substation_id = path[1].id if len(path) > 1 else UUID("00000000-0000-0000-0000-000000000000")
        substation_name = path[1].name if len(path) > 1 else "Unknown Substation"
        substation_nomenclature = path[1].nomenclature if len(path) > 1 else "Unknown Nomenclature"

        return BreadcrumbResponseModel(
            locality=locality,
            substation_id=substation_id,
            substation_name=substation_name,
            substation_nomenclature=substation_nomenclature,
            path=path[2:] 
        )
