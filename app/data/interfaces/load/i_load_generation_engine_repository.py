"""Module for the load generation engine repository interface."""

from abc import abstractmethod

from app.data.interfaces.i_repository import IRepository, T


# T is LoadGenerationEngine for this interface
class ILoadGenerationEngineRepository(IRepository[T]):
    """
    Interface for managing load generation engine configurations.
    Extends IRepository for CRUD on LoadGenerationEngine settings.
    """

    @abstractmethod
    def delete_by_profile_id(self, profile_id: int) -> int:
        """
        Deletes load generation engine settings associated with a profile ID.

        Args:
            profile_id: The int of the load profile.

        Returns:
            The number of records deleted.
        """

