import uuid
from abc import ABC, abstractmethod
from typing import Any, Dict, List, Optional, Union
from uuid import UUID

from app.domain.entities.energy_interval import EnergyInterval
from app.domain.entities.house import House


class IAllocationService(ABC):
    @abstractmethod
    def read(self, houses: List[House],  available_energy: List[EnergyItem], load[LoadItem]) -> List[House]:
        pass

    @abstractmethod
    def get_breadcrumb_navigation_path(self, node_id: UUID) -> List[EnergyInterval]:
        pass
