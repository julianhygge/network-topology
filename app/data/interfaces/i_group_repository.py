"""
Module for the group repository interface.
"""
import datetime
from abc import abstractmethod
from enum import Enum
from typing import Any, List, NamedTuple

from app.data.interfaces.i_repository import IRepository, T


class UserRoles(Enum):
    """
    Enum for user roles.
    """

    ADMIN = "Admin"
    USER = "User"
    GUEST = "Guest"


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
    def fetch_roles_and_permissions_by_groups(
        self,
        session_user: Any,
        now: datetime.datetime,
    ) -> List[RolePermission]:
        """
        Fetches roles and permissions for groups associated with a session user.

        Args:
            session_user: The user object or identifier for the current
                session.
            now: The current datetime, used for validity checks.

        Returns:
            A list of RolePermission objects.
        """
        pass
