from abc import ABC, abstractmethod
from typing import Dict, Any


class INetTopologyService(ABC):

    @abstractmethod
    def get_topology_by_substation_id(self, substation_id: str) -> Dict[str, Any]:
        pass

    @abstractmethod
    def update_topology(self, user_id, substation_id, data: Dict[str, Any]) -> None:
        pass

    @abstractmethod
    def update_transformer(self, transformer_id, data):
        pass

    @abstractmethod
    def update_house(self, house_id, data):
        pass