"""
Module for the base repository interface.

This module defines the IRepository abstract base class, which serves as a
contract for all repository implementations. It uses a generic type T to
represent the model entity the repository will manage.
"""

from abc import ABC, abstractmethod
from typing import Any, Dict, Generic, List, Optional, TypeVar, Union
from uuid import UUID

from app.data.schemas.schema_base import BaseModel

T = TypeVar("T", bound=BaseModel)


class IRepository(ABC, Generic[T]):
    """
    Base interface for repositories.

    This generic interface defines standard CRUD operations and other common
    data access methods that repositories should implement.
    """

    @abstractmethod
    def create(self, data: Dict[str, Any]) -> T:
        """
        Abstract method to create a new record.

        Args:
            data (Dict[str, Any]): A dictionary containing the data for the
                                   new record.

        Returns:
            T: The created model instance.
        """

    @abstractmethod
    def read(self, id_value: Union[int, UUID]) -> T:
        """
        Abstract method to read a record by its ID.

        Args:
            id_value (Union[int, UUID]): The ID of the record to retrieve.

        Returns:
            T: The model instance if found, otherwise None.
        """

    @abstractmethod
    def read_or_none(self, id_value: Union[int, UUID]) -> T | None:
        """
        Abstract method to read a record by its ID.

        Args:
            id_value (Union[int, UUID]): The ID of the record to retrieve.

        Returns:
            T | None: The model instance if found, otherwise None.
        """

    @abstractmethod
    def update(
        self, id_value: Union[int, UUID], data: Dict[str, Any]
    ) -> T | None:
        """
        Abstract method to update a record by its ID.

        Args:
            id_value (Union[int, UUID]): The ID of the record to update.
            data (Dict[str, Any]): A dictionary containing the fields to update
                                   and their new values.

        Returns:
            int: The number of rows updated.
        """

    @abstractmethod
    def delete(self, id_value: Union[int, UUID]) -> int:
        """
        Abstract method to delete a record by its ID.

        Args:
            id_value (Union[int, UUID]): The ID of the record to delete.

        Returns:
            int: The number of rows deleted.
        """

    @abstractmethod
    def list(self) -> List[T]:
        """
        Abstract method to list all records.

        Returns:
            List[T]: A list of all model instances.
        """

    @abstractmethod
    def list_actives(self) -> List[T]:
        """
        Abstract method to list active records.

        Assumes the model has an 'active' boolean field.

        Returns:
            List[T]: A list of active model instances.
        """

    @abstractmethod
    def list_public(self) -> List[T]:
        """
        Abstract method to list public records.

        Assumes the model has 'public' and 'active' boolean fields.

        Returns:
            List[T]: A list of public and active model instances.
        """

    @abstractmethod
    def upsert(
        self,
        conflict_target: List[str],
        defaults: Dict[str, Any],
        data: Dict[str, Any],
    ) -> Any:  # Peewee's execute() can return different types
        """
        Abstract method to upsert a record (insert or update on conflict).

        Args:
            conflict_target (List[str]): A list of field names that define
                                         the conflict.
            defaults (Dict[str, Any]): A dictionary of fields to update if a
                                       conflict occurs.
            data (Dict[str, Any]): The data for the record to insert or that
                                   forms part of the conflict identification.

        Returns:
            Any: The result of the database execution (e.g., ID of the
                 inserted/updated row, or number of rows affected, depending
                 on the database and Peewee version).
        """

    @abstractmethod
    def upsert_and_retrieve(
        self,
        conflict_target: List[str],
        defaults: Dict[str, Any],
        data: Dict[str, Any],
    ) -> T | None:
        """
        Abstract method to upsert a record and retrieve it.

        Args:
            conflict_target (List[str]): A list of field names that define
                                         the conflict.
            defaults (Dict[str, Any]): A dictionary of fields to update if a
                                       conflict occurs.
            data (Dict[str, Any]): The data for the record to insert or that
                                   forms part of the conflict identification.

        Returns:
            T | None: The upserted model instance, or None if retrieval fails.
        """

    @abstractmethod
    def list_no_public_by_user_id(self, user_id: Union[int, UUID]) -> List[T]:
        """
        Abstract method to list non-public records by user ID.

        Assumes the model has 'created_by', 'active', and 'public' fields.

        Args:
            user_id (Union[int, UUID]): The ID of the user who created the
                                        records.

        Returns:
            List[T]: A list of non-public, active model instances created by
                     the specified user.
        """

    @property
    @abstractmethod
    def database_instance(self) -> Any:
        """
        Abstract property for the database instance.

        This allows repositories to access the configured database connection.

        Returns:
            Any: The database instance (e.g., a Peewee Database object).
        """

    @abstractmethod
    def to_dicts(
        self, obj: Any
    ) -> Union[Dict[str, Any], List[Dict[str, Any]], Any]:
        """
        Abstract method to convert a model instance or list of instances to
        dictionaries.

        Args:
            obj (Any): The model instance, list of instances, or ModelSelect
                       query to convert.

        Returns:
            Union[Dict[str, Any], List[Dict[str, Any]], Any]:
                The dictionary representation or list of dictionary
                representations. Other types might be returned as is.
        """

    @abstractmethod
    def list_by_user_id(self, user_id: Union[int, UUID]) -> List[T]:
        """
        Abstract method to list records filtered by user ID and active status.

        Assumes the model has 'created_by' and 'active' fields.

        Args:
            user_id (Union[int, UUID]): The ID of the user.

        Returns:
            List[T]: A list of model instances created by the user and active.
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
