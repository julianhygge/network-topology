from abc import ABC, abstractmethod
from typing import List
from uuid import UUID

from app.domain.entities.house_profile import HouseProfile
from app.domain.entities.node import Node


class IDataPreparationService(ABC):
    @abstractmethod
    def get_house_profile(self, house: Node) -> HouseProfile:
        """Get the solar profile of a house in
        15 minutes intervals for a full year"""

    @abstractmethod
    def get_houses_profile_by_substation_id(
        self, substation_id: UUID
    ) -> List[HouseProfile]:
        """Get the list of solar profile for the houses in a substation
        15 minutes intervals for a full year"""

    @abstractmethod
    def create_house_profile_csvs_by_substation_id(
        self, substation_id: UUID, output_directory: str = "house_profiles_csv"
    ) -> List[str]:
        """
        Generates CSV files for each house profile under a substation
        and saves them to a specified directory.
        Returns a list of file paths.
        """

    @abstractmethod
    def get_house_profile_csvs_zip_by_substation_id(
        self, substation_id: UUID, output_directory: str = "house_profiles_csv"
    ) -> bytes:
        """
        Generates CSV files for house profiles and returns them as a ZIP file
        in memory.
        """
