from typing import List
from app.data.interfaces.igroup_repository import IGroupRepository, RolePermission
from app.data.repositories.base_repository import BaseRepository
from app.data.schemas.auth.auth_schema import Groups, Permissions, Roles, UserGroupRel, RolePermissionRel, GroupRoleRel


class GroupRepository(BaseRepository, IGroupRepository):
    model = Groups
    id_field = Groups.id

    def fetch_roles_and_permissions_by_groups(self, session_user, now) -> List[RolePermission]:
        return (Groups.select(Roles.name,
                              Permissions.resource_name,
                              Permissions.can_create,
                              Permissions.can_retrieve,
                              Permissions.can_update,
                              Permissions.can_delete,
                              Permissions.can_search)
                .join_from(Groups, GroupRoleRel, on=(Groups.id == GroupRoleRel.group), attr='group_role_rel')
                .join_from(GroupRoleRel, Roles, on=(GroupRoleRel.role == Roles.id), attr='role')
                .join_from(Roles, RolePermissionRel, on=(Roles.id == RolePermissionRel.role),
                           attr='role_permission_rel')
                .join_from(RolePermissionRel, Permissions, on=(RolePermissionRel.permission == Permissions.id),
                           attr='permission')
                .join_from(Groups, UserGroupRel, on=(Groups.id == UserGroupRel.group_id))
                .where((UserGroupRel.user_record_id == session_user.record_id)
                       & (UserGroupRel.validity_start <= now)
                       & (UserGroupRel.validity_end > now)))
