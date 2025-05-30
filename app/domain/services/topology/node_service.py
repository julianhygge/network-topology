import uuid
from typing import Any, Dict, Optional
from uuid import UUID

from app.api.v1.models.responses.breadcrumb import (
    BreadcrumbItem,
    BreadcrumbResponseModel,
)
from app.data.interfaces.topology.i_node_repository import INodeRepository
from app.domain.interfaces.i_node_service import INodeService


class NodeService(INodeService):
    def __init__(self, node_repo: INodeRepository):
        self.node_repo = node_repo

    def read(self, item_id: UUID) -> Optional[Dict[str, Any]]:
        node = self.node_repo.read(item_id)
        if node:
            return {
                "id": node.id,
                "name": node.name or "Unknown",
                "nomenclature": node.nomenclature or "Unknown",
            }
        return None

    def get_breadcrumb_navigation_path(
        self, node_id: UUID
    ) -> BreadcrumbResponseModel:
        path = []
        current_node = self.node_repo.read(node_id)

        while current_node:
            if current_node.node_type != "substation":
                path.append(
                    BreadcrumbItem(
                        id=current_node.id,
                        name=current_node.name or "Unknown",
                        nomenclature=current_node.nomenclature or "Unknown",
                    )
                )
            current_node = self.node_repo.get_parent(current_node.id)

        path.reverse()

        substation_node = self.node_repo.get_substation(node_id)
        substation_id = substation_node.id if substation_node else uuid.uuid4()
        substation_name = (
            substation_node.name if substation_node else "Unknown Substation"
        )
        substation_nomenclature = (
            substation_node.name if substation_node else "Unknown Nomenclature"
        )

        locality_node = self.node_repo.get_locality(node_id)
        locality_name = (
            locality_node.name if locality_node else "Unknown Locality"
        )

        return BreadcrumbResponseModel(
            locality=locality_name,
            substation_id=substation_id,
            substation_name=substation_name,
            substation_nomenclature=substation_nomenclature,
            path=[
                BreadcrumbItem(
                    id=item.id,
                    name=item.name or "Unknown",
                    nomenclature=item.nomenclature or "Unknown",
                )
                for item in path
            ],
        )
