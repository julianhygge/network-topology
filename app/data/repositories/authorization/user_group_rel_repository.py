"""Module for the UserGroupRelRepository."""

import datetime
from datetime import timezone

from peewee import DoesNotExist, IntegrityError, Select

from app.data.repositories.base_repository import BaseRepository
from app.data.schemas.auth.auth_schema import Groups, UserGroupRel


class UserGroupRelRepository(BaseRepository[UserGroupRel]):
    """
    Repository for managing the relationship between users and groups.

    This class extends `BaseRepository` to provide generic CRUD operations
    for the `UserGroupRel` model, which links users to groups.
    """
    def __init__(self):
        super().__init__(model=UserGroupRel)

    def delete_by_user_id(self, user_id: int) -> int:
        """
        Deletes all group memberships for a given user.

        Args:
            user_id: The ID of the user whose group memberships are to be
                     deleted.

        Returns:
            The number of rows deleted.
        """
        return (
            self.model.delete()
            .where(self.model.user_record_id == user_id)
            .execute()
        )

    def get_groups_by_user_id(self, user_id: int) -> Select:
        """
        Retrieves all distinct groups a user belongs to.

        Args:
            user_id: The ID of the user.

        Returns:
            A Peewee Select query yielding Group objects.
        """
        return (
            Groups.select()
            .join(self.model, on=(Groups.id == self.model.group_id))
            .where(self.model.user_record_id == user_id)
            .distinct()
        )

    def add_user_to_group(
        self, logged_user_id: int, user_id: int, group_id: int
    ) -> bool:
        """
        Adds a user to a specified group.

        Args:
            logged_user_id: The ID of the user performing the action.
            user_id: The ID of the user to be added to the group.
            group_id: The ID of the group.

        Returns:
            True if the user was successfully added, False if an integrity
            error occurred (e.g., user already in group).
        """
        try:
            self.model.create(
                user_record_id=user_id,
                group_id=group_id,
                validity_start=datetime.datetime.now(timezone.utc),
                validity_end=datetime.datetime.max,
                created_on=datetime.datetime.now(timezone.utc),
                modified_on=datetime.datetime.now(timezone.utc),
                created_by=logged_user_id,
                modified_by=logged_user_id,
            )
            return True
        except IntegrityError:
            return False

    def remove_user_from_group(self, user_id: int, group_id: int) -> bool:
        """
        Removes a user from a specified group.

        Args:
            user_id: The ID of the user to be removed.
            group_id: The ID of the group.

        Returns:
            True if the user was successfully removed (i.e., at least one
            record was deleted), False otherwise (e.g., user not in
            group).
        """
        try:
            query = self.model.delete().where(
                (self.model.user_record_id == user_id)
                & (self.model.group_id == group_id)
            )
            num_deleted = query.execute()
            return num_deleted > 0
        except (
            DoesNotExist
        ):  # Should not happen with delete, but good practice
            return False
