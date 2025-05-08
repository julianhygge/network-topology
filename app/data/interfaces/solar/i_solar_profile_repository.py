"""
Interface for the Solar Profile Repository.
"""

from abc import abstractmethod
from typing import Optional
from uuid import UUID

from app.data.interfaces.i_repository import IRepository
from app.data.schemas.solar.solar_profile_schema import SolarProfile


class ISolarProfileRepository(IRepository[SolarProfile]):
    """
    Interface defining specific operations for SolarProfileRepository
    beyond the generic IRepository.
    """

    @abstractmethod
    def get_solar_profile_by_house_id(
        self, house_id: UUID
    ) -> Optional[SolarProfile]:
        """
        Retrieves a solar profile by its associated house ID.

        Args:
            house_id: The UUID of the house.

        Returns:
            A SolarProfile instance if found, otherwise None.
        """

    @abstractmethod
    def delete_solar_profile_by_house_id(self, house_id: UUID) -> int:
        """
        Deletes a solar profile by its associated house ID.

        Args:
            house_id: The UUID of the house.

        Returns:
            The number of rows deleted.
        """
