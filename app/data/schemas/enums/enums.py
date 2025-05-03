import enum

from peewee import CharField


class EnumField(CharField):
    """
    This class enable an Enum like field for Peewee
    """

    def __init__(self, enum_class, max_length=50, *args, **kwargs):
        self.enum_class = enum_class
        self.max_length = max_length
        super(CharField, self).__init__(*args, **kwargs)

    def db_value(self, value):
        return value.value

    def python_value(self, value):
        return self.enum_class(value)


class UserRoles(enum.Enum):
    Admin = 'Admin'
    User = 'User'
    Guest = 'Guest'


class NodeStatusEnum(enum.Enum):
    Complete = "complete"
    Empty = "empty"
    InProgress = "in_progress"
