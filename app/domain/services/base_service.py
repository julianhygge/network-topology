"""
Base service class providing common CRUD operations.
"""
import uuid
from typing import Any, Dict, Generic, List, Optional, TypeVar, Union
from uuid import UUID

from app.data.interfaces.i_repository import IRepository
from app.domain.interfaces.i_service import IService
from app.utils.datetime_util import utc_now

T = TypeVar("T")


class BaseService(IService, Generic[T]):
    """
    Base service class with generic repository type.
    """

    def __init__(self, repository: IRepository[T]):
        """
        Initializes the BaseService with a repository.

        Args:
            repository: The repository instance.
        """
        self.repository: IRepository[T] = repository

    def create(self, user_id: UUID, **kwargs: Any) -> Dict[str, Any]:
        """
        Creates a new record.

        Args:
            user_id: The UUID of the user creating the record.
            **kwargs: Keyword arguments for creating the record.

        Returns:
            A dictionary representation of the created record.
        """
        kwargs["created_by"] = user_id
        kwargs["modified_by"] = user_id
        kwargs["active"] = True
        created = self.repository.create(**kwargs)
        created_dicts = self.repository.to_dicts(created)
        return created_dicts

    def read(
        self, item_id: Union[int, UUID]
    ) -> Optional[Dict[str, Any]]:
        """
        Reads a record by its ID.

        Args:
            item_id: The ID of the record.

        Returns:
            A dictionary representation of the record if found, otherwise None.
        """
        items = self.repository.read(item_id)
        item_dict = self.repository.to_dicts(items)
        return item_dict

    def update(
        self, user_id: UUID, item_id: Union[int, UUID], **kwargs: Any
    ) -> Optional[Dict[str, Any]]:
        """
        Updates a record by its ID.

        Args:
            user_id: The UUID of the user updating the record.
            item_id: The ID of the record.
            **kwargs: Keyword arguments for updating the record.

        Returns:
            A dictionary representation of the updated record if found,
            otherwise None.
        """
        kwargs["modified_on"] = utc_now()
        kwargs["modified_by"] = user_id
        update_result = self.repository.update(item_id, **kwargs)
        if update_result:
            updated_dicts = self.repository.read(item_id)
            if updated_dicts:
                return self.repository.to_dicts(updated_dicts)
        return None

    def delete(self, item_id: Union[int, UUID]) -> bool:
        """
        Deletes a record by its ID.

        Args:
            item_id: The ID of the record.

        Returns:
            True if the record was deleted, False otherwise.
        """
        deleted = self.repository.delete(item_id)
        if deleted:
            return True
        return False

    def list(self, user_id: UUID) -> List[Dict[str, Any]]:
        """
        Lists active records for a specific user.

        Args:
            user_id: The UUID of the user.

        Returns:
            A list of dictionary representations of the records.
        """
        list_items = self.repository.list_actives()
        return self.repository.to_dicts(list_items)

    def list_all(self) -> List[Dict[str, Any]]:
        """
        Lists all active records.

        Returns:
            A list of dictionary representations of the records.
        """
        list_items = self.repository.list_actives()
        return self.repository.to_dicts(list_items)
