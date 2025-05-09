"""Module for the load profile repository interface."""

from abc import abstractmethod
from typing import List, Optional
from uuid import UUID

from app.data.interfaces.i_repository import IRepository, T


class ILoadProfileRepository(IRepository[T]):
    """
    Interface for repositories managing load profile data.
    Extends the generic IRepository with load profile specific operations.
    """

    @abstractmethod
    def get_public_profiles(self) -> List[T]:
        """
        Retrieves all public load profiles.

        Returns:
            A list of public load profile instances (T).
        """
        pass

    @abstractmethod
    def get_load_profiles_by_user_id(self, user_id: UUID) -> List[T]:
        """
        Retrieves all load profiles for a specific user.

        Args:
            user_id: The UUID of the user.

        Returns:
            A list of load profile instances (T) belonging to the user.
        """
        pass

    @abstractmethod
    def get_load_profiles_by_user_id_and_house_id(
        self, user_id: UUID, house_id: UUID
    ) -> List[T]:
        """
        Retrieves load profiles for a specific user and house.

        Args:
            user_id: The UUID of the user.
            house_id: The UUID of the house.

        Returns:
            A list of load profile instances (T) for the user and house.
        """
        pass

    @abstractmethod  # Added abstractmethod as it's implemented in repo
    def get_or_create_by_house_id(
        self, user_id: UUID, house_id: UUID, load_source: str
    ) -> T:
        """
        Retrieves an existing load profile by house_id or creates a new one.

        Args:
            user_id: The UUID of the user creating/owning the profile.
            house_id: The UUID of the house associated with the profile.
            load_source: A string indicating the source of the load data.

        Returns:
            The existing or newly created load profile instance (T).
        """
        pass

    @abstractmethod
    def get_by_house_id(self, house_id: UUID) -> Optional[T]:
        """
        Retrieves a load profile by its associated house_id.

        Args:
            house_id: The UUID of the house.

        Returns:
            A load profile instance (T) if found, otherwise None.
        """
        pass
