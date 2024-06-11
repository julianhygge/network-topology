import enum


class Resources(enum.Enum):
    Users = 'users'


class Permission(enum.Enum):
    Create = 'create'
    Retrieve = 'retrieve'
    Update = 'update'
    Delete = 'delete'
    Search = 'search'
