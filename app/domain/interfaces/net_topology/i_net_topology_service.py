from abc import ABC, abstractmethod
from typing import Any, Dict, List
from uuid import UUID

from app.domain.entities.node import Node


class INetTopologyService(ABC):
    @abstractmethod
    def get_topology_by_substation_id(
        self, substation_id: UUID
    ) -> Dict[str, Any]:
        pass

    @abstractmethod
    def update_topology(
        self, user_id: UUID, substation_id: UUID, data: Dict[str, Any]
    ) -> None:
        pass

    @abstractmethod
    def update_transformer(self, user_id: UUID, transformer_id: UUID, data: Dict[str, Any]):
        pass

    @abstractmethod
    def update_house(self, user_id: UUID, house_id: UUID, data: Dict[str, Any]):
        pass

    @abstractmethod
    def get_houses_by_substation_id(self, substation_id: UUID) -> List[Node]:
        pass

    @abstractmethod
    def get_node_by_id(self, node_id: UUID) -> Node | None:
        pass

    @abstractmethod
    def get_houses_by_parent_node_id(self, parent_node_id: UUID) -> List[Node]:
        pass
