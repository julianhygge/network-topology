"""
Base interface for services.
"""
from abc import ABC, abstractmethod
from typing import Any, Dict, Generic, List, Optional, TypeVar

UserIdType = TypeVar("UserIdType")
ItemIdType = TypeVar("ItemIdType")


class IService(ABC, Generic[UserIdType, ItemIdType]):
    """
    Base interface for services with generic user and item ID types.
    """

    @abstractmethod
    def create(self, user_id: UserIdType, **kwargs: Any) -> Dict[str, Any]:
        """
        Abstract method to create a new record.
        """
        pass

    @abstractmethod
    def read(self, item_id: ItemIdType) -> Optional[Dict[str, Any]]:
        """
        Abstract method to read a record by its ID.
        """
        pass

    @abstractmethod
    def update(
        self, user_id: UserIdType, item_id: ItemIdType, **kwargs: Any
    ) -> Optional[Dict[str, Any]]:
        """
        Abstract method to update a record by its ID.
        """
        pass

    @abstractmethod
    def list(self, user_id: UserIdType) -> List[Dict[str, Any]]:
        """
        Abstract method to list records for a specific user.
        """
        pass

    @abstractmethod
    def list_all(self) -> List[Dict[str, Any]]:
        """
        Abstract method to list all records.
        """
        pass

    @abstractmethod
    def delete(self, item_id: ItemIdType) -> bool:
        """
        Abstract method to delete a record by its ID.
        """
        pass
