from abc import ABC, abstractmethod
from typing import Any, Dict, List

from app.domain.entities.node import Node


class INetTopologyService(ABC):
    @abstractmethod
    def get_topology_by_substation_id(
        self, substation_id: str
    ) -> Dict[str, Any]:
        pass

    @abstractmethod
    def update_topology(
        self, user_id, substation_id, data: Dict[str, Any]
    ) -> None:
        pass

    @abstractmethod
    def update_transformer(self, user_id, transformer_id, data):
        pass

    @abstractmethod
    def update_house(self, user_id, house_id, data):
        pass

    @abstractmethod
    def get_houses_by_substation_id(self, substation_id) -> List[Node]:
        pass
