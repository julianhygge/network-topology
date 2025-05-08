import operator
from functools import reduce
from typing import Any, List, Optional, Type, TypeVar

from peewee import DoesNotExist, IntegrityError  # Model not directly used

from app.data.interfaces.i_generic_repository import IGenericRepository
from app.data.schemas.schema_base import BaseModel as PeeweeModelClass

# Type variable for Peewee model, subclass of our BaseModel
T = TypeVar("T", bound=PeeweeModelClass)


class GenericRepository(IGenericRepository[T]):  # Implement interface
    """
    A generic repository for Peewee models, providing common CRUD operations.
    """

    def __init__(self, model_class: Type[T]):
        self.model_class = model_class

    def create(self, **kwargs: Any) -> T:
        """
        Creates a new record in the database.
        :param kwargs: Fields and values for the new record.
        :return: The created model instance.
        :raises IntegrityError: If data integrity is violated (e.g., unique
                                 constraint).
        """
        try:
            instance = self.model_class.create(**kwargs)
            return instance
        except IntegrityError as e:
            # Handle or re-raise specific integrity errors if needed
            raise e

    def get_by_id(self, record_id: Any) -> Optional[T]:
        """
        Retrieves a record by its primary key.
        :param record_id: The ID of the record to retrieve.
        :return: The model instance if found, otherwise None.
        """
        try:
            return self.model_class.get_by_id(record_id)
        except DoesNotExist:
            return None

    def get_all(
        self, limit: Optional[int] = None, offset: Optional[int] = None
    ) -> List[T]:
        """
        Retrieves all records, with optional pagination.
        :param limit: Maximum number of records to return.
        :param offset: Number of records to skip.
        :return: A list of model instances.
        """
        query = self.model_class.select()
        if offset is not None:
            query = query.offset(offset)
        if limit is not None:
            query = query.limit(limit)
        return list(query)

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
        query = self.model_class.select()

        filter_expressions = []
        for field_name, value in kwargs.items():
            if hasattr(self.model_class, field_name):
                field = getattr(self.model_class, field_name)
                # Basic equality. More complex filters
                # (like, in, gt, lt) can be added.
                filter_expressions.append((field == value))
            else:
                # Handle cases where the field doesn't exist or log a warning
                print(
                    f"Warning: Field '{field_name}' not found in model "
                    f"{self.model_class.__name__}"
                )

        if filter_expressions:
            # Combine multiple filter expressions using AND logic
            # For OR logic, peewee.Expression.or_() can be used.

            combined_filter = reduce(operator.and_, filter_expressions)
            query = query.where(combined_filter)

        if offset is not None:
            query = query.offset(offset)
        if limit is not None:
            query = query.limit(limit)

        return list(query)

    def update(self, record_id: Any, **kwargs: Any) -> Optional[T]:
        """
        Updates an existing record.
        :param record_id: The ID of the record to update.
        :param kwargs: Fields and new values to update.
        :return: The updated model instance if found and updated,
        :otherwise None.
        :raises IntegrityError: If data integrity is violated.
        """
        instance = self.get_by_id(record_id)
        if instance:
            for key, value in kwargs.items():
                if hasattr(instance, key):
                    setattr(instance, key, value)
                else:
                    # Optionally, raise an error or log a warning
                    # for non-existent fields
                    print(
                        f"Warning: Field '{key}' not found in model "
                        f"{self.model_class.__name__} during update."
                    )
            try:
                instance.save()
                return instance
            except IntegrityError as e:
                raise e
        return None

    def delete(self, record_id: Any) -> bool:
        """
        Deletes a record by its primary key.
        :param record_id: The ID of the record to delete.
        :return: True if the record was deleted, False otherwise.
        """
        instance = self.get_by_id(record_id)
        if instance:
            instance.delete_instance()
            return True
        return False

    def count(self, **kwargs: Any) -> int:
        """
        Counts records, optionally based on filter criteria.
        :param kwargs: Field-value pairs to filter by before counting.
        :return: The number of matching records.
        """
        if kwargs:
            # Simplified count for filtered items. For complex filters,
            # align with `filter` method's logic.
            return len(self.filter(**kwargs))
        return self.model_class.select().count()
