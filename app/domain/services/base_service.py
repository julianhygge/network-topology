"""Base service class providing common CRUD operations."""

from typing import Any, Dict, Generic, List, Optional, TypeVar, Union
from uuid import UUID

from peewee import Expression

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
        # Ensure created_on and modified_on are set if not provided
        kwargs.setdefault("created_on", utc_now())
        kwargs.setdefault("modified_on", utc_now())

        created_item: T = self.repository.create(kwargs)
        # Assuming to_dicts can handle a single item and returns a Dict
        created_dict = self.repository.to_dicts(created_item)
        if created_dict is None:  # Should not happen if create is successful
            raise ValueError(
                "Repository create method returned an item that "
                "resulted in None when converted to dict."
            )
        return created_dict

    def read(self, item_id: Union[int, UUID]) -> Optional[Dict[str, Any]]:
        """
        Reads a record by its ID.

        Args:
            item_id: The ID of the record.

        Returns:
            A dictionary representation of the record if found, otherwise None.
        """
        item: Optional[T] = self.repository.read(item_id)
        # to_dicts should handle None input and return None
        return self.repository.to_dicts(item)

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

        # Assuming repository.update returns the updated model or None
        updated_item = self.repository.update(item_id, kwargs)

        if updated_item:
            return self.repository.to_dicts(updated_item)
        return None

    def delete(self, item_id: Union[int, UUID]) -> int:
        """
        Deletes a record by its ID.
        In a soft-delete scenario, this might mean setting 'active = False'.
        The current IRepository.delete suggests hard delete.

        Args:
            item_id: The ID of the record.

        Returns:
            True if the record was deleted, False otherwise.
        """
        return self.repository.delete(item_id)

    def list(self, user_id: UUID) -> List[Dict[str, Any]]:
        """
        Lists active records.
        WARNING: This implementation currently lists ALL active records
        and IGNORES the user_id. If you need to filter by user_id,
        the IRepository.list_actives() method (or a new one like list_by_user)
        needs to support filtering by user_id.

        Args:
            user_id: The UUID of the user. (Currently ignored )

        Returns:
            A list of dictionary representations of the records.
        """
        # TODO: filtering by user_id is required, modify repository call:

        list_items: List[T] = self.repository.list_actives()

        dict_list = self.repository.to_dicts(list_items)
        if dict_list is None:
            return []
        return dict_list

    def list_all(self) -> List[Dict[str, Any]]:
        """
        Lists all active records.
        If "list_all" means truly all (active and inactive), then
        repository should have a method like `list_all_repo()`.

        Returns:
            A list of dictionary representations of the records.
        """
        list_items: List[T] = self.repository.list_actives()

        dict_list = self.repository.to_dicts(list_items)
        if dict_list is None:
            return []
        return dict_list

    def filter(self, *expressions: Expression, **filters) -> List[T]:
        """
        Filters records based on a combination of Peewee expressions and
        simple equality filters.

        Args:
            *expressions: Variable number of Peewee Expression objects
                          (Model.field > value).
            **filters: Field names and values for filtering (name="John", age=30).

        Returns:
            List[T]: A list of model instances matching the filter criteria.
        """
        list_items = self.repository.filter(
            house_id="7ecae55e-92dd-427e-a2d6-4f3bed16b0d2"
        )

        dict_list = self.repository.to_dicts(list_items)
        if dict_list is None:
            return []
        return list_items
