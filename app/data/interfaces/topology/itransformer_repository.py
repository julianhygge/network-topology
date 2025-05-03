"""
Module for the transformer repository interface.
"""
from abc import abstractmethod
from app.data.interfaces.irepository import IRepository, T


class ITransformerRepository(IRepository[T]):
    """
    Interface for the transformer repository.
    """
    @abstractmethod
    def get_transformers_by_substation_id(self, substation_id):
        """
        Abstract method to get transformers by substation ID.
        """
