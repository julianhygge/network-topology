import datetime

from peewee import DateTimeField, Model


class BaseModel(Model):
    """Base model for Peewee ORM that sets the database dynamically."""

    @classmethod
    def set_database(cls, db_instance):
        cls._instance = db_instance
        cls._meta.database = db_instance  # type:ignore
        for subclass in cls.__subclasses__():
            subclass.set_database(db_instance)


class InfDateTimeField(DateTimeField):
    """DateTime field that supports 'infinity' and '-infinity' values."""

    def db_value(self, value):
        """Converts Python datetime values to database string representation."""
        if value == datetime.datetime.max:
            return "infinity"
        elif value == datetime.datetime.min:
            return "-infinity"
        else:
            return super().db_value(value)
