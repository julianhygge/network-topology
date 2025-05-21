"""
Module for the base repository implementation.
"""

from enum import Enum
from functools import reduce
import operator
from typing import (
    Any,
    Dict,
    Iterable,
    List,
    Optional,
    Type,
    TypeVar,
    Union,
    cast,
)
from uuid import UUID

from peewee import Expression, IntegrityError, ModelSelect, DoesNotExist
from playhouse.pool import PooledPostgresqlDatabase  # type: ignore[import]

from app.data.interfaces.i_repository import IRepository
from app.data.schemas.hygge_database import HyggeDatabase
from app.data.schemas.schema_base import BaseModel

T = TypeVar("T", bound=BaseModel)


class BaseRepository(IRepository[T]):
    """
    Generic base repository implementation using Peewee.

    The Peewee model and its ID field are automatically inferred from the
    generic type argument (BaseRepository[MyModel]).
    The model (T) must be a Peewee Model subclass.
    The ID field is inferred from _model._meta.primary_key.
    """

    def __init__(self, model: Type[T]):
        self._model = model

    @property
    def database_instance(self) -> PooledPostgresqlDatabase:
        return HyggeDatabase.get_instance()

    def create(self, data: Dict[str, Any]) -> T:
        obj = self._model.create(**data)
        return obj

    def read(self, id_value: Union[int, UUID]) -> T | None:
        obj = self._model.get_or_none(self._model.id == id_value)
        return obj

    def read_or_none(self, id_value: Union[int, UUID]) -> T | None:
        """
        Abstract method to read a record by its ID.

        Args:
            id_value (Union[int, UUID]): The ID of the record to retrieve.

        Returns:
            T | None: The model instance if found, otherwise None.
        """
        try:
            obj = self._model.get_by_id(id_value)
            return obj
        except DoesNotExist:
            return None

    def update(
        self, id_value: Union[int, UUID], data: Dict[str, Any]
    ) -> Optional[T]:
        """
        Updates an existing record.
        :param id_value: The ID of the record to update.
        :param data: Fields and new values to update.
        :return: The updated model instance if found and updated or None.
        :raises IntegrityError: If data integrity is violated.
        """
        instance = self.read(id_value)
        if instance:
            for key, value in data.items():
                if hasattr(instance, key):
                    setattr(instance, key, value)
            try:
                instance.save()
                return instance
            except IntegrityError as e:
                raise e
        return None

    def delete(self, id_value: Union[int, UUID]) -> int:
        return self._model.delete_by_id(id_value)

    def list(self) -> List[T]:
        return list(cast(Iterable[T], self._model.select()))

    def list_actives(self) -> List[T]:
        if not hasattr(self._model, "active"):
            raise AttributeError(
                f"Model {self._model.__name__} has no 'active' property."
            )
        active_field = self._model.active
        # Use implicit boolean check for 'active_field'
        return list(
            cast(Iterable[T], self._model.select().where(active_field))
        )

    def upsert(
        self,
        conflict_target: List[str],
        defaults: Dict[str, Any],
        data: Dict[str, Any],
    ) -> Any:
        insert_data = {**data, **defaults}
        conflict_fields_objects = [
            getattr(self._model, field_name) for field_name in conflict_target
        ]
        query = self._model.insert(**insert_data).on_conflict(
            conflict_target=conflict_fields_objects,
            update=defaults,
        )
        return query.execute()

    def upsert_and_retrieve(
        self,
        conflict_target: List[str],
        defaults: Dict[str, Any],
        data: Dict[str, Any],
    ) -> T | None:
        self.upsert(
            conflict_target=conflict_target, defaults=defaults, data=data
        )
        retrieval_query: ModelSelect = self._model.select()
        where_conditions: List[Expression] = []
        for field_name in conflict_target:
            model_field = getattr(self._model, field_name)
            if field_name in data:
                where_conditions.append(model_field == data[field_name])
            elif field_name in defaults:
                where_conditions.append(model_field == defaults[field_name])

        if not where_conditions:
            return None

        return retrieval_query.where(*where_conditions).first()

    def list_public(self) -> List[T]:
        """
        Lists all public and active records for the _model.
        Assumes the model has 'public' and 'active' boolean fields.
        """
        try:
            public_field = self._model.public
            active_field = self._model.active
        except AttributeError as e:
            # Fix duplicated f-string content
            raise AttributeError(
                f"The model '{self._model.__name__}' must have 'public' and "
                "'active' fields for list_public to work."
            ) from e
        query = self._model.select().where(public_field & active_field)
        return list(cast(Iterable[T], query))

    def list_no_public_by_user_id(self, user_id: Union[int, UUID]) -> List[T]:
        required_fields = ["created_by", "active", "public"]
        for field in required_fields:
            if not hasattr(self._model, field):
                raise AttributeError(
                    f"Model {self._model.__name__} does not have required "
                    f"'{field}' property for list_no_public_by_user_id."
                )

        created_by_field = self._model.created_by
        active_field = self._model.active
        public_field = self._model.public

        query: ModelSelect = self._model.select().where(
            (created_by_field == user_id) & active_field & (~public_field)
        )
        return cast(List[T], list(cast(ModelSelect, query)))

    def to_dicts(
        self, obj
    ) -> Union[Dict[str, Any], List[Dict[str, Any]], Any]:
        if isinstance(obj, ModelSelect):
            return [self.to_dicts(item) for item in obj]
        elif hasattr(obj, "__data__"):
            return {
                key: self.to_dicts(value)
                for key, value in obj.__data__.items()
                if not key.startswith("_")
            }
        elif isinstance(obj, list):
            return [self.to_dicts(item) for item in obj]
        elif isinstance(obj, Enum):
            return obj.value
        elif hasattr(obj, "__dict__"):
            return {
                key: self.to_dicts(value)
                for key, value in obj.__dict__.items()
                if not key.startswith("_")
            }
        else:
            return obj

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
        query = self._model.select()

        filter_expressions = []
        for field_name, value in kwargs.items():
            if hasattr(self._model, field_name):
                field = getattr(self._model, field_name)
                filter_expressions.append((field == value))
        if filter_expressions:
            combined_filter = reduce(operator.and_, filter_expressions)
            query = query.where(combined_filter)

        if offset is not None:
            query = query.offset(offset)
        if limit is not None:
            query = query.limit(limit)

        return list(query)

    def list_by_user_id(self, user_id: Union[int, UUID]) -> List[T]:
        """
        Lists records filtered by a specific user ID and active status.

        This method assumes that the repository's model (T) has both
        a 'created_by' field (to match against user_id) and an
        'active' boolean field.

        Args:
            user_id (Union[int, UUID]): The ID of the user whose records
                                        are to be retrieved.

        Returns:
            List[T]: A list of active model instances created by the
                     specified user.

        Raises:
            AttributeError: If the repository's model does not have the
                            required 'created_by' or 'active' fields.
        """
        try:
            # Attempt to get the Peewee field descriptors from the model class
            created_by_field = self._model.created_by
            active_field = self._model.active
        except AttributeError as e:
            model_name = self._model.__name__
            raise AttributeError(
                f"The model '{model_name}' must have 'created_by' and "
                "'active' fields for list_by_user_id to work."
            ) from e

        query = self._model.select().where(
            (created_by_field == user_id) & active_field
        )
        return list(cast(Iterable[T], query))
