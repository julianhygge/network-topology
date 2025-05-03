import datetime

from peewee import DoesNotExist, IntegrityError

from app.data.repositories.base_repository import BaseRepository
from app.data.schemas.auth.auth_schema import Groups, UserGroupRel


class UserGroupRelRepository(BaseRepository):
    model = UserGroupRel
    id_field = UserGroupRel.id

    def delete_by_user_id(self, user_id):
        return self.model.delete().where(self.model.user_record_id == user_id).execute()

    def get_groups_by_user_id(self, user_id):
        return (Groups
                .select()
                .join(self.model, on=(Groups.id == self.model.group_id))
                .where(self.model.user_record_id == user_id)
                .distinct())

    def add_user_to_group(self, logged_user_id, user_id, group_id):
        try:
            self.model.create(
                user_record_id=user_id,
                group_id=group_id,
                validity_start=datetime.datetime.utcnow(),
                validity_end=datetime.datetime.max,
                created_on=datetime.datetime.utcnow(),
                modified_on=datetime.datetime.utcnow(),
                created_by=logged_user_id,
                modified_by=logged_user_id
            )
            return True
        except IntegrityError:
            return False

    def remove_user_from_group(self, user_id, group_id):
        try:
            query = self.model.delete().where(
                (self.model.user == user_id) &
                (self.model.group_id == group_id)
            )
            num_deleted = query.execute()
            return num_deleted > 0
        except DoesNotExist:
            return False
