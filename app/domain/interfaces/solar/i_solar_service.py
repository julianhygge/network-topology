"""
Interface for the Solar Profile Service.
"""

from abc import abstractmethod
from typing import Any, Dict, List, Optional, Tuple
from uuid import UUID

from app.domain.interfaces.i_service import IService


class ISolarProfileService(IService):
    """
    Abstract base class for the Solar Profile Service.
    Defines the interface for managing solar profiles.
    """

    @abstractmethod
    def create(self, user_id: UUID, **kwargs: Any) -> Dict[str, Any]:
        """
        Creates a new solar profile.

        Args:
            user_id: The UUID of the user creating the profile.
            **kwargs: Keyword arguments containing the solar profile data.

        Returns:
            A dictionary representation of the created solar profile.
        """

    @abstractmethod
    def delete_solar_profile_by_house_id(self, house_id: UUID) -> None:
        """
        Deletes a solar profile by its associated house ID.

        Args:
            house_id: The UUID of the house.
        """

    @abstractmethod
    def update_solar_profile(
        self, user_id: UUID, house_id: UUID, **kwargs: Any
    ) -> None:
        """
        Updates an existing solar profile.

        Args:
            user_id: The UUID of the user updating the profile.
            house_id: The UUID of the house associated with the profile.
            **kwargs: Keyword arguments containing the updated solar profile
                data.
        """


class ISolarInstallationService(IService):
    @abstractmethod
    def get_solar_installation(
        self, filter_key: Optional[str], limit: int, offset: int
    ) -> Tuple[List[Dict[str, Any]], int, int, int]:
        pass

    @abstractmethod
    def backfill_missing_data(self):
        pass