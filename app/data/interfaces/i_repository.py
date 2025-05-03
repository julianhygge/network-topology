"""
Module for the base repository interface.
"""
from abc import ABC, abstractmethod
from typing import Any, Dict, Generic, List, TypeVar, Union
from uuid import UUID

T = TypeVar('T')


class IRepository(ABC, Generic[T]):
    """
    Base interface for repositories.
    """
    @property
    @abstractmethod
    def model(self) -> Any:
        """
        Abstract property for the repository's model.
        """

    @property
    @abstractmethod
    def id_field(self) -> Union[int, UUID]:
        """
        Abstract property for the model's ID field.
        """

    @abstractmethod
    def create(self, **query) -> T:
        """
        Abstract method to create a new record.
        """

    @abstractmethod
    def read(self, id_value) -> T:
        """
        Abstract method to read a record by its ID.
        """

    @abstractmethod
    def update(self, id_value, **query) -> int:
        """
        Abstract method to update a record by its ID.
        """

    @abstractmethod
    def delete(self, id_value) -> int:
        """
        Abstract method to delete a record by its ID.
        """

    @abstractmethod
    def list(self) -> List[T]:
        """
        Abstract method to list all records.
        """

    @abstractmethod
    def list_actives(self) -> List[T]:
        """
        Abstract method to list active records.
        """

    @abstractmethod
    def list_public(self) -> List[T]:
        """
        Abstract method to list public records.
        """

    @abstractmethod
    def upsert(self, conflict_target: List[str], defaults: Dict[str, any],
               **query) -> T:
        """
        Abstract method to upsert a record.
        """

    @abstractmethod
    def upsert_and_retrieve(self, conflict_target: List[str],
                            defaults: Dict[str, any], **query) -> T:
        """
        Abstract method to upsert and retrieve a record.
        """

    @abstractmethod
    def list_no_public_by_user_id(self, user_id) -> List[T]:
        """
        Abstract method to list non-public records by user ID.
        """

    @property
    @abstractmethod
    def database_instance(self):
        """
        Abstract property for the database instance.
        """

    @abstractmethod
    def to_dicts(self, obj) -> Union[Dict[str, Any], List[Dict[str, Any]], Any]:
        """
        Abstract method to convert an object or list of objects to dictionaries.
        """

    def list_by_user_id(self, user_id) -> List[T]:
        """
        List records filtered by user ID and active status.
        """
        return list(self.model.select().where((self.model.created_by == user_id) &
                                              self.model.active))  # pylint: disable=syntax-error
