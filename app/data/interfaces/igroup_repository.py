from abc import abstractmethod
from enum import Enum
from typing import NamedTuple, List
from app.data.interfaces.irepository import IRepository, T


class UserRoles(Enum):
    Admin = 'Admin'
    User = 'User'
    Guest = 'Guest'



class Permission(NamedTuple):
    resource_name: str
    can_create: bool
    can_retrieve: bool
    can_update: bool
    can_delete: bool
    can_search: bool


class RolePermissionRel(NamedTuple):
    permission: Permission


class Role(NamedTuple):
    name: UserRoles  # Changed from str to UserRoles
    role_permission_rel: RolePermissionRel


class GroupRoleRel(NamedTuple):
    role: Role


class RolePermission(NamedTuple):
    group_role_rel: GroupRoleRel


class IGroupRepository(IRepository[T]):
    @abstractmethod
    def fetch_roles_and_permissions_by_groups(self, session_user, now) -> List[RolePermission]:
        pass
