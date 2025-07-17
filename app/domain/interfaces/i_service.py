"""
Base interface for services.
"""

from abc import ABC, abstractmethod
from typing import Any, Dict, Generic, List, Optional, TypeVar

UserIdGeneric = TypeVar("UserIdGeneric")
ItemIdGeneric = TypeVar("ItemIdGeneric")


class IService(ABC, Generic[UserIdGeneric, ItemIdGeneric]):
    """
    Base interface for services with generic user and item ID types.
    """

    @abstractmethod
    def create(self, user_id: UserIdGeneric, **kwargs: Any) -> Dict[str, Any]:
        """
        Abstract method to create a new record.
        """

    @abstractmethod
    def read(self, item_id: ItemIdGeneric) -> Optional[Dict[str, Any]]:
        """
        Abstract method to read a record by its ID.
        """

    @abstractmethod
    def read_or_none(self, item_id: ItemIdGeneric) -> Optional[Dict[str, Any]]:
        """
        Abstract method to read a record by its ID.
        """

    @abstractmethod
    def update(
        self, user_id: UserIdGeneric, item_id: ItemIdGeneric, **kwargs: Any
    ) -> Optional[Dict[str, Any]]:
        """
        Abstract method to update a record by its ID.
        """

    @abstractmethod
    def list(self, user_id: UserIdGeneric) -> List[Dict[str, Any]]:
        """
        Abstract method to list records for a specific user.
        """

    @abstractmethod
    def list_all(self) -> List[Dict[str, Any]]:
        """
        Abstract method to list all records.
        """

    @abstractmethod
    def delete(self, item_id: ItemIdGeneric) -> int:
        """
        Abstract method to delete a record by its ID.
        """

    @abstractmethod
    def filter(self, **filters: Any) -> List[Dict[str, Any]]:
        """
        Filters records based on Peewee expressions and equality filters.

        Args:
            **filters: Field names and values for equality filtering.

        Returns:
            A list of dictionaries representing matching model instances.
        """
