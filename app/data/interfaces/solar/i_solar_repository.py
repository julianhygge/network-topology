"""
Interface for the Solar Profile Repository.
"""

from abc import abstractmethod
from uuid import UUID

from app.data.interfaces.i_repository import IRepository
from app.data.schemas.solar.solar_schema import SolarInstallation, SolarProfile


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
    def get_solar_installation(
        self, filter_key: str | None, limit: int | None, offset: int | None
    ) -> tuple[list[SolarInstallation], int, int, int]:
        """
        Retrieves solar installations with optional filtering, pagination.

        Args:
            filter_key: Optional string to filter results.
            limit: Optional integer for the number of items per page.
            offset: Optional integer for the number of items to skip.

        Returns:
            A tuple containing:
                - list[SolarInstallation]: List of solar installation objects.
                - int: Total number of items matching the filter.
                - int: Total number of pages.
                - int: Current page number.
        """
