"""
Module for the group repository interface.
"""
from abc import abstractmethod
from enum import Enum
from typing import List, NamedTuple

from app.data.interfaces.i_repository import IRepository, T


class UserRoles(Enum):
    """
    Enum for user roles.
    """
    ADMIN = 'Admin'
    USER = 'User'
    GUEST = 'Guest'


class Permission(NamedTuple):
    """
    NamedTuple for permissions.
    """
    resource_name: str
    can_create: bool
    can_retrieve: bool
    can_update: bool
    can_delete: bool
    can_search: bool


class RolePermissionRel(NamedTuple):
    """
    NamedTuple for role permission relationship.
    """
    permission: Permission


class Role(NamedTuple):
    """
    NamedTuple for roles.
    """
    name: UserRoles
    role_permission_rel: RolePermissionRel


class GroupRoleRel(NamedTuple):
    """
    NamedTuple for group role relationship.
    """
    role: Role


class RolePermission(NamedTuple):
    """
    NamedTuple for role permissions.
    """
    group_role_rel: GroupRoleRel


class IGroupRepository(IRepository[T]):
    """
    Interface for the group repository.
    """
    @abstractmethod
    def fetch_roles_and_permissions_by_groups(self, session_user, now) -> List[RolePermission]:
        """
        Abstract method to fetch roles and permissions by groups.
        """
        pass # pylint: disable=syntax-error
