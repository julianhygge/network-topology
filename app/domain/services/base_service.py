"""Base service class providing common CRUD operations."""

from typing import Any, Dict, Generic, List, Optional, TypeVar, Union, cast
from uuid import UUID

from app.data.interfaces.i_repository import IRepository
from app.data.schemas.schema_base import BaseModel
from app.domain.interfaces.i_service import IService
from app.utils.datetime_util import utc_now

T = TypeVar("T", bound=BaseModel)


class BaseService(IService[UUID, Union[int, UUID]], Generic[T]):
    """
    Base service class providing common CRUD operations.

    Implements IService with UUID for user IDs and Union[int, UUID] for IDs.
    Generic over T, which is the type of the model handled by the repository.
    """

    def __init__(self, repository: IRepository[T]):
        """
        Initializes the BaseService with a repository.

        Args:
            repository: The repository instance that handles models of type T.
        """
        self.repository = repository

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
        kwargs.setdefault("created_on", utc_now())
        kwargs.setdefault("modified_on", utc_now())

        created_item: T = self.repository.create(kwargs)
        result = self.repository.to_dicts(created_item)

        if isinstance(result, dict):
            return cast(Dict[str, Any], result)
        # This case should ideally not be reached if create is successful
        # and to_dicts works as expected for a single model.
        raise ValueError(
            "Failed to convert created item to dictionary."
        )

    def read(self, item_id: Union[int, UUID]) -> Optional[Dict[str, Any]]:
        """
        Reads a record by its ID.

        Args:
            item_id: The ID of the record.

        Returns:
            A dictionary representation of the record if found, otherwise None.
        """
        item: Optional[T] = self.repository.read(item_id)
        if item is None:
            return None
        result = self.repository.to_dicts(item)
        if isinstance(result, dict):
            return cast(Dict[str, Any], result)
        return None  # Should not happen if item was a model

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

        updated_count = self.repository.update(item_id, kwargs)

        if updated_count > 0:
            # Re-fetch the item to return its latest state as a dict
            updated_item = self.repository.read(item_id)
            if updated_item:
                result = self.repository.to_dicts(updated_item)
                if isinstance(result, dict):
                    return cast(Dict[str, Any], result)
        return None

    def delete(self, item_id: Union[int, UUID]) -> int:
        """
        Deletes a record by its ID.

        Args:
            item_id: The ID of the record.

        Returns:
            The number of records deleted (0 or 1).
        """
        return self.repository.delete(item_id)

    def list(self, user_id: UUID) -> List[Dict[str, Any]]:
        """
        Lists active records.

        Args:
            user_id: The UUID of the user. (Currently ignored by list_actives)

        Returns:
            A list of dictionary representations of the records.
        """
        # TODO: Implement user_id filtering if IRepository.list_actives changes
        # or a new method like list_by_user is used.
        list_items: List[T] = self.repository.list_actives()
        result = self.repository.to_dicts(list_items)

        if isinstance(result, list):
            # Ensure all items in the list are dictionaries
            return [
                item for item in result if isinstance(item, dict)
            ]
        return []

    def list_all(self) -> List[Dict[str, Any]]:
        """
        Lists all active records.

        Returns:
            A list of dictionary representations of the records.
        """
        list_items: List[T] = self.repository.list_actives()
        result = self.repository.to_dicts(list_items)

        if isinstance(result, list):
            return [
                item for item in result if isinstance(item, dict)
            ]
        return []

    def filter(  
        self, **filters: Any
    ) -> List[Dict[str, Any]]:
        """
        Filters records based on Peewee expressions and equality filters.

        Args:
            **filters: Field names and values for equality filtering.

        Returns:
            A list of dictionaries representing matching model instances.
        """
        list_items: List[T] = self.repository.filter(
            **filters
        )
        result = self.repository.to_dicts(list_items)

        if isinstance(result, list):
            return [
                item for item in result if isinstance(item, dict)
            ]
        if isinstance(result, dict):
            return [cast(Dict[str, Any], result)]
        return []
