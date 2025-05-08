"""
Module for the base repository implementation.
"""

from typing import Any, Dict, Iterable, List, Type, Union, cast, get_args
from uuid import UUID

from peewee import Expression, Field, Model, ModelSelect
from playhouse.pool import PooledPostgresqlDatabase  # type: ignore[import]

from app.data.interfaces.i_repository import IRepository, T
from app.data.schemas.hygge_database import HyggeDatabase


class BaseRepository(IRepository[T]):
    """
    Generic base repository implementation using Peewee.

    The Peewee model and its ID field are automatically inferred from the
    generic type argument (e.g., BaseRepository[MyModel]).
    The model (T) must be a Peewee Model subclass.
    The ID field is inferred from model._meta.primary_key.
    """

    _model_cls: Type[T]
    _id_field_instance: Field

    def __init_subclass__(cls, **kwargs: Any) -> None:
        """
        Automatically sets the Peewee model class and its primary key field
        for subclasses based on the generic type argument.
        """
        super().__init_subclass__(**kwargs)

        if not hasattr(cls, "_model_cls"):
            inferred_model_type: Type[T] | None = None
            orig_bases = getattr(cls, "__orig_bases__", ())

            for base_class in orig_bases:
                if getattr(base_class, "__origin__", None) is BaseRepository:
                    type_args = get_args(base_class)
                    if (
                        type_args
                        and isinstance(type_args[0], type)
                        and issubclass(type_args[0], Model)
                    ):
                        inferred_model_type = cast(Type[T], type_args[0])
                        break

            if inferred_model_type:
                cls._model_cls = inferred_model_type

        model_for_pk = getattr(cls, "_model_cls", None)
        if not hasattr(cls, "_id_field_instance") and model_for_pk:
            if hasattr(model_for_pk, "_meta") and hasattr(
                model_for_pk._meta, "primary_key"
            ):
                pk_field = model_for_pk._meta.primary_key
                if isinstance(pk_field, Field):
                    cls._id_field_instance = pk_field

    def __init__(self):
        """
        Initializes the BaseRepository instance.

        This primarily ensures that the necessary class
        attributes (`_model_cls`,
        `_id_field_instance`) have been correctly set by `__init_subclass__`
        by attempting to access the `model` property and
        `_get_id_field` method.
        """
        _ = self.model
        _ = self._get_id_field()

    @property
    def model(self) -> Type[T]:
        """
        The Peewee model class this repository operates on.
        This is derived from the _model_cls class attribute, typically set
        by __init_subclass__ based on the generic type T.
        """
        m = getattr(self.__class__, "_model_cls", None)
        if m is None:
            # Break long f-string
            cls_name = self.__class__.__name__
            raise AttributeError(
                f"'{cls_name}' must define a '_model_cls' attribute or "
                "inherit using generic type: BaseRepository[YourModel]."
            )
        return m

    def _get_id_field(self) -> Field:
        """
        Retrieves the Peewee Field instance representing the primary key.

        This relies on the `_id_field_instance` class attribute being set,
        typically by `__init_subclass__` inspecting the model's metadata.

        Returns:
            The Peewee Field instance for the primary key.

        Raises:
            AttributeError: If the primary key field cannot be determined.
        """
        id_field_obj = getattr(self.__class__, "_id_field_instance", None)
        if id_field_obj is None or not isinstance(id_field_obj, Field):
            # Break long f-string
            cls_name = self.__class__.__name__
            raise AttributeError(
                f"'{cls_name}' could not determine its primary key field. "
                "Ensure the model used (from BaseRepository[YourModel]) has "
                "a primary key, or explicitly set '_id_field_instance' on "
                "the repository subclass."
            )
        return id_field_obj

    @property
    def database_instance(self) -> PooledPostgresqlDatabase:
        return HyggeDatabase.get_instance()

    def create(self, data: Dict[str, Any]) -> T:
        obj = self.model.create(**data)
        return obj

    def read(self, id_value: Union[int, UUID]) -> T | None:
        obj = self.model.get_or_none(self._get_id_field() == id_value)
        return obj

    def update(self, id_value: Union[int, UUID], data: Dict[str, Any]) -> int:
        query = self.model.update(**data).where(
            self._get_id_field() == id_value
        )
        return query.execute()

    def delete(self, id_value: Union[int, UUID]) -> int:
        query = self.model.delete().where(self._get_id_field() == id_value)
        return query.execute()

    def list(self) -> List[T]:
        return list(cast(Iterable[T], self.model.select()))

    def list_actives(self) -> List[T]:
        if not hasattr(self.model, "active"):
            raise AttributeError(
                f"Model {self.model.__name__} has no 'active' property."
            )
        active_field = self.model.active
        # Use implicit boolean check for 'active_field'
        return list(cast(Iterable[T], self.model.select().where(active_field)))

    def upsert(
        self,
        conflict_target: List[str],
        defaults: Dict[str, Any],
        data: Dict[str, Any],
    ) -> Any:
        insert_data = {**data, **defaults}
        conflict_fields_objects = [
            getattr(self.model, field_name) for field_name in conflict_target
        ]
        query = self.model.insert(**insert_data).on_conflict(
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
        retrieval_query: ModelSelect = self.model.select()
        where_conditions: List[Expression] = []
        for field_name in conflict_target:
            model_field = getattr(self.model, field_name)
            if field_name in data:
                where_conditions.append(model_field == data[field_name])
            elif field_name in defaults:
                where_conditions.append(model_field == defaults[field_name])

        if not where_conditions:
            return None

        return retrieval_query.where(*where_conditions).first()

    def list_public(self) -> List[T]:
        """
        Lists all public and active records for the model.
        Assumes the model has 'public' and 'active' boolean fields.
        """
        try:
            public_field = self.model.public
            active_field = self.model.active
        except AttributeError as e:
            # Fix duplicated f-string content
            raise AttributeError(
                f"The model '{self.model.__name__}' must have 'public' and "
                "'active' fields for list_public to work."
            ) from e
        query = self.model.select().where(public_field & active_field)
        return list(cast(Iterable[T], query))

    def list_no_public_by_user_id(self, user_id: Union[int, UUID]) -> List[T]:
        required_fields = ["created_by", "active", "public"]
        for field in required_fields:
            if not hasattr(self.model, field):
                # Fix grammar ("had not" -> "does not have")
                raise AttributeError(
                    f"Model {self.model.__name__} does not have required "
                    f"'{field}' property for list_no_public_by_user_id."
                )

        created_by_field = self.model.created_by
        active_field = self.model.active
        public_field = self.model.public

        query: ModelSelect = self.model.select().where(
            (created_by_field == user_id) & active_field & (~public_field)
        )
        return cast(List[T], list(cast(ModelSelect, query)))

    def to_dicts(
        self, obj: Any
    ) -> Union[Dict[str, Any], List[Dict[str, Any]], Any]:
        """
        Converts a Peewee model instance, ModelSelect, or list of instances
        to dictionaries.

        Args:
            obj (Any): The object to convert.

        Returns:
            Union[Dict[str, Any], List[Dict[str, Any]], Any]:
                The dictionary representation or list of dictionaries.
        """
        if isinstance(obj, ModelSelect):
            return [self.to_dicts(item) for item in obj]
        if hasattr(obj, "__data__"):  # Peewee model instance
            return {
                key: self.to_dicts(value)
                for key, value in obj.__data__.items()
            }
        if isinstance(obj, list):
            return [self.to_dicts(item) for item in obj]
        # Fallback for other objects, could be expanded
        if hasattr(obj, "__dict__"):
            return {
                key: self.to_dicts(value)
                for key, value in obj.__dict__.items()
                if not key.startswith("_")
            }
        return obj

    def filter(self, *expressions: Expression, **filters):
        """
        Filters records based on a combination of Peewee expressions and
        simple equality filters.

        Args:
            *expressions: Variable number of Peewee Expression objects
                          (Model.field > value).
            filters: A dictionary where keys are field names (strings)
                     and values are the values to filter by
                     ({"name": "John"}).

        Returns:
            List[T]: A list of model instances matching the filter criteria.
        """
        query = self.model.select()

        for expression in expressions:
            query = query.where(expression)

        for field, value in filters.items():
            if hasattr(self.model, field):
                query = query.where(getattr(self.model, field) == value)

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
            created_by_field = self.model.created_by
            active_field = self.model.active
        except AttributeError as e:
            # Re-raise with a more specific and informative message
            # Fix duplicated f-string content
            model_name = self.model.__name__
            raise AttributeError(
                f"The model '{model_name}' must have 'created_by' and "
                "'active' fields for list_by_user_id to work."
            ) from e

        query = self.model.select().where(
            (created_by_field == user_id) & active_field
        )
        return list(cast(Iterable[T], query))
