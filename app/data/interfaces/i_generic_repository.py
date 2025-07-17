"""
Module for the base repository interface.

This module defines the IRepository abstract base class, which serves as a
contract for all repository implementations. It uses a generic type T to
represent the model entity the repository will manage.
"""

from abc import ABC, abstractmethod
from typing import Any, Generic, List, Optional, TypeVar

T = TypeVar("T")


class IGenericRepository(Generic[T], ABC):
    """
    Interface for a generic repository providing common CRUD operations.
    """

    @abstractmethod
    def create(self, **kwargs: Any) -> T:
        """
        Creates a new record.
        :param kwargs: Fields and values for the new record.
        :return: The created model instance.
        """

    @abstractmethod
    def read(self, record_id: Any) -> Optional[T]:
        """
        Retrieves a record by its primary key.
        :param record_id: The ID of the record to retrieve.
        :return: The model instance if found, otherwise None.
        """

    @abstractmethod
    def get_all(
        self, limit: Optional[int] = None, offset: Optional[int] = None
    ) -> List[T]:
        """
        Retrieves all records, with optional pagination.
        :param limit: Maximum number of records to return.
        :param offset: Number of records to skip.
        :return: A list of model instances.
        """

    @abstractmethod
    def filter(
        self,
        limit: Optional[int] = None,
        offset: Optional[int] = None,
        **kwargs: Any,
    ) -> List[T]:
        """
        Filters records based on provided criteria, with optional pagination.
        :param limit: Maximum number of records to return.
        :param offset: Number of records to skip.
        :param kwargs: Field-value pairs to filter by.
        :return: A list of matching model instances.
        """

    @abstractmethod
    def update(self, record_id: Any, **kwargs: Any) -> Optional[T]:
        """
        Updates an existing record.
        :param record_id: The ID of the record to update.
        :param kwargs: Fields and new values to update.
        :return: The updated model instance if found and updated,
                 otherwise None.
        """

    @abstractmethod
    def delete(self, record_id: Any) -> bool:
        """
        Deletes a record by its primary key.
        :param record_id: The ID of the record to delete.
        :return: True if the record was deleted, False otherwise.
        """

    @abstractmethod
    def count(self, **kwargs: Any) -> int:
        """
        Counts records, optionally based on filter criteria.
        :param kwargs: Field-value pairs to filter by before counting.
        :return: The number of matching records.
        """
