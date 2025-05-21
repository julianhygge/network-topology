"""
Interface for the Solar Profile Repository.
"""

from abc import abstractmethod
from uuid import UUID

from app.data.interfaces.i_repository import IRepository
from app.data.schemas.solar.solar_schema import SolarProfile, SolarInstallation


class ISolarProfileRepository(IRepository[SolarProfile]):
    """
    Interface defining specific operations for SolarProfileRepository
    beyond the generic IRepository.
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

class ISolarInstallationRepository(IRepository[SolarInstallation]):

    @abstractmethod
    def get_solar_installation(self, filter_key):
        pass
