import uuid
from abc import ABC, abstractmethod
from typing import Any, Dict, List, Optional, Union
from uuid import UUID

from app.domain.entities.energy_interval import EnergyInterval
from app.domain.entities.house import House


class IAllocationService(ABC):
    @abstractmethod
    def get_total_load_by_house_intervals(self, house: House) -> List[House]:
        """Get the total load(ev + loads...) of a house in
        15 minutes intervals"""
        pass

    @abstractmethod
    def get_load_intervals_by_load_profile(
        self, load_profile: UUID
    ) -> List[EnergyInterval]:
        pass
