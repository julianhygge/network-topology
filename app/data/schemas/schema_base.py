"""
Base model and custom field definitions for Peewee ORM.

This module provides a `BaseModel` class that allows dynamic database
instance setting for all subclasses. It also includes `InfDateTimeField`
for handling 'infinity' and '-infinity' timestamp values in PostgreSQL.
"""

import datetime
from typing import Optional

from peewee import Database, DateTimeField, Model


class BaseModel(Model):
    """Base model for Peewee ORM that sets the database dynamically."""

    @classmethod
    def set_database(cls, db_instance: Database):
        """
        Sets the database instance for the model and its subclasses.

        This allows dynamic binding of models to a specific database
        connection.

        Args:
            db_instance: The Peewee database instance to use.
        """  
        # pylint: disable=no-member
        cls._meta.database = db_instance  # type: ignore[assignment, no-member]
        for subclass in cls.__subclasses__():
            subclass.set_database(db_instance)


class InfDateTimeField(DateTimeField):
    """DateTime field that supports 'infinity' and '-infinity' values."""

    def db_value(self, value: Optional[datetime.datetime]) -> Optional[str]:
        """Converts Python datetime values to DB string representation."""
        if value == datetime.datetime.max:
            return "infinity"
        if value == datetime.datetime.min:
            return "-infinity"
        return super().db_value(value)  # type: ignore[return-value]
