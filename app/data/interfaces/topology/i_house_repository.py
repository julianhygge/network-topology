"""Module for the house repository interface."""
from abc import abstractmethod
from uuid import UUID

from peewee import Select

from app.data.interfaces.i_repository import IRepository, T


# T is House for this interface
class IHouseRepository(IRepository[T]):
    """
    Interface defining specific operations for HouseRepository
    beyond the generic IRepository.
    """

    @abstractmethod
    def get_houses_by_substation_id(self, substation_id: UUID) -> Select:
        """
        Retrieves all houses connected to a specific substation.

        Args:
            substation_id: The UUID of the substation.

        Returns:
            A Peewee Select query yielding House instances.
        """
        pass
