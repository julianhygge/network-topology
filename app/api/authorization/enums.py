import enum


class Resources(enum.Enum):
    Users = 'users'
    Groups = 'groups'
    Roles = 'roles'
    Houses = 'houses'
    Accounts = 'accounts'
    Localities = 'localities'
    Substations = 'substations'
    Transformers = 'transformers'
    Electrical = 'electrical'


class Permission(enum.Enum):
    Create = 'create'
    Retrieve = 'retrieve'
    Update = 'update'
    Delete = 'delete'
    Search = 'search'
