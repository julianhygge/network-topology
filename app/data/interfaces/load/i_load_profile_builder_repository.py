"""Module for the load profile builder repository interface."""

from abc import abstractmethod
from typing import Any, Dict, List

from app.data.interfaces.i_repository import IRepository, T
from app.data.schemas.load_profile.load_profile_schema import (
    LoadProfileBuilderItems,
)


# T is LoadProfileBuilderItems for this interface
class ILoadProfileBuilderRepository(IRepository[T]):
    """
    Interface for managing items used in building load profiles.
    Extends IRepository for CRUD on LoadProfileBuilderItems.
    """

    @abstractmethod
    def get_items_by_profile_id(
        self, profile_id: int
    ) -> List[LoadProfileBuilderItems]:
        """
        Retrieves all builder items associated with a specific load profile.

        Args:
            profile_id: The int of the load profile.

        Returns:
            A list of LoadProfileBuilderItems instances.
        """

    @abstractmethod
    def create_items_in_bulk(self, items: List[Dict[str, Any]]) -> None:
        """
        Creates multiple load profile builder items in bulk.

        Args:
            items: A list of dictionaries, each representing an item's data.
        """

    @abstractmethod
    def delete_by_profile_id(self, profile_id: int) -> int:
        """
        Deletes all builder items associated with a specific load profile.

        Args:
            profile_id: The int of the load profile.

        Returns:
            The number of items deleted.
        """

    @abstractmethod
    def update_items_in_bulk(self, items: List[Dict[str, Any]]) -> None:
        """
        Updates multiple load profile builder items in bulk.
        Each dictionary in the list should contain an 'id' for the item
        to be updated, along with the fields to update.

        Args:
            items: A list of dictionaries, each representing an item's data
                   including its 'id'.
        """
