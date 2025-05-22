from abc import ABC, abstractmethod
from typing import List
from uuid import UUID

from app.domain.entities.house_profile import HouseProfile


class IDataPreparationService(ABC):
    @abstractmethod
    def get_house_profile(self, house_id: UUID) -> HouseProfile:
        """Get the solar profile of a house in
        15 minutes intervals for a full year"""

    @abstractmethod
    def get_houses_profile_by_substation_id(
        self, substation_id: UUID
    ) -> List[HouseProfile]:
        """Get the list of solar profile for the houses in a substation
        15 minutes intervals for a full year"""
