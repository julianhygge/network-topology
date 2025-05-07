"""Module for the GroupRepository."""
import datetime
from typing import Any, List

from app.data.interfaces.i_group_repository import (IGroupRepository,
                                                    RolePermission)
from app.data.repositories.base_repository import BaseRepository
from app.data.schemas.auth.auth_schema import (GroupRoleRel, Groups,
                                               Permissions, RolePermissionRel,
                                               Roles, UserGroupRel)


class GroupRepository(
    BaseRepository[Groups], IGroupRepository[Groups]
):
    """
    Repository for managing user groups and their associated roles and permissions.

    This class extends `BaseRepository` for generic CRUD operations on `Groups`
    and implements `IGroupRepository` for group-specific queries.
    """

    def fetch_roles_and_permissions_by_groups(
        self, session_user: Any, now: datetime.datetime
    ) -> List[RolePermission]:
        """
        Fetches roles and permissions for all groups a user belongs to.

        The query joins through Groups, GroupRoleRel, Roles, RolePermissionRel,
        and Permissions to construct a comprehensive list of what actions
        a user can perform based on their group memberships.

        Args:
            session_user: The user object (or an object with a `record_id`
                          attribute) for whom to fetch permissions.
            now: The current datetime, used to filter for active group
                 memberships based on `validity_start` and `validity_end`.

        Returns:
            A list of RolePermission named tuples, detailing the permissions
            associated with the user's groups.
        """
        query = (
            Groups.select(
                Roles.name,
                Permissions.resource_name,
                Permissions.can_create,
                Permissions.can_retrieve,
                Permissions.can_update,
                Permissions.can_delete,
                Permissions.can_search,
            )
            .join_from(
                Groups,
                GroupRoleRel,
                on=(Groups.id == GroupRoleRel.group),
                attr="group_role_rel",
            )
            .join_from(
                GroupRoleRel,
                Roles,
                on=(GroupRoleRel.role == Roles.id),
                attr="role",
            )
            .join_from(
                Roles,
                RolePermissionRel,
                on=(Roles.id == RolePermissionRel.role),
                attr="role_permission_rel",
            )
            .join_from(
                RolePermissionRel,
                Permissions,
                on=(RolePermissionRel.permission == Permissions.id),
                attr="permission",
            )
            .join_from(
                Groups, UserGroupRel, on=(Groups.id == UserGroupRel.group_id)
            )
            .where(
                (UserGroupRel.user_record_id == session_user.record_id)
                & (UserGroupRel.validity_start <= now)
                & (UserGroupRel.validity_end > now)
            )
        )
        return list(query)
