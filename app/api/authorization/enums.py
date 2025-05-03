"""Enums for authorization resources and permissions."""

import enum


class Resources(enum.Enum):
    """Enum representing available resources for authorization."""
    USERS = 'users'
    GROUPS = 'groups'
    ROLES = 'roles'
    HOUSES = 'houses'
    ACCOUNTS = 'accounts'
    LOCALITIES = 'localities'
    SUBSTATIONS = 'substations'
    TRANSFORMERS = 'transformers'
    ELECTRICALS = 'electricals'
    LOAD_PROFILE_DETAILS = 'load_profile_details'
    LOAD_PROFILES = 'load_profiles'


class Permission(enum.Enum):
    """Enum representing available permissions for authorization."""
    CREATE = 'create'
    RETRIEVE = 'retrieve'
    UPDATE = 'update'
    DELETE = 'delete'
    SEARCH = 'search'
