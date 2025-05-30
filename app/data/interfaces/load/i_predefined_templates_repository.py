"""Module for the predefined templates repository interface."""

from abc import abstractmethod
from typing import Optional

from app.data.interfaces.i_repository import IRepository, T


# T is LoadPredefinedTemplates for this interface
class IPredefinedTemplatesRepository(IRepository[T]):
    """
    Interface for managing predefined templates associated with load profiles.
    Extends IRepository for CRUD on LoadPredefinedTemplates.
    """

    @abstractmethod
    def get_by_profile_id(self, profile_id: int) -> Optional[T]:
        """
        Retrieves a predefined template record by its associated profile ID.

        Args:
            profile_id: The int of the load profile.

        Returns:
            A LoadPredefinedTemplates instance if found, otherwise None.
        """

    @abstractmethod
    def create_or_update(self, profile_id: int, template_id: int) -> T:
        """
        Creates a new predefined template association
        or updates an existing one.

        Args:
            profile_id: The int of the load profile.
            template_id: The template's int.

        Returns:
            The created or updated LoadPredefinedTemplates instance.
        """
