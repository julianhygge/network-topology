"""
Interface for the Load Profile Service.
"""

from abc import ABC, abstractmethod
from typing import Any, Dict, List
from uuid import UUID


class ILoadProfileService(ABC):
    """
    Abstract base class for the Load Profile Service.
    Defines the interface for managing load profiles.
    """

    @abstractmethod
    def delete_profile(self, profile_id: UUID) -> Any:
        """
        Abstract method to delete a load profile and its associated details.
        """

    @abstractmethod
    def list_profiles(
        self, user_id: UUID, house_id: UUID
    ) -> List[Dict[str, Any]]:
        """
        Abstract method to list all accessible load profiles for a user and house,
        including public profiles.
        """
