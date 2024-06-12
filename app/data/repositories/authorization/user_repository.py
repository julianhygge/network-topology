from app.data.interfaces.irepository import T
from app.data.interfaces.iuser_repository import IUserRepository
from peewee import IntegrityError
from app.data.schemas.auth.auth_schema import UserGroupRel
from app.data.schemas.transactional.user_schema import User, Account
from app.utils.logger import logger
from app.data.repositories.base_repository import BaseRepository


class AccountRepository(BaseRepository):
    model = Account
    id_field = Account.id


class UserRepository(BaseRepository, IUserRepository):
    model = User
    model_user_group = UserGroupRel
    model_account = Account
    id_field = User.id

    def fetch_user_by_phone_number(self, phone_number: str) -> T:
        return self.model.get_or_none(self.model.phone_number == phone_number)

    def fetch_account_by_phone_number(self, phone_number: str) -> T:
        return self.model_account.get_or_none(self.model_account.phone_number == phone_number)

    def insert_into_user_and_group(self, user_data, data) -> T:
        try:
            with self.database_instance.atomic():
                # self.model_account.create(**user_data)
                user = self.model.create(**user_data)
                # self.model_user_group.create(**data)
                user_id = user_data['id']
                # self.model_user_group.update(user_id, **data)
                self.update_user_group(user_id, **data)
                return self.to_dicts(user)
        except IntegrityError as e:
            logger.exception(e)
            raise

    def create(self, **query) -> T:
        if 'logo_file' in query:
            with open(query.pop('logo_file'), 'rb') as f:
                query['logo'] = f.read()
        obj = self.model.create(**query)
        return obj

    def insert_into_account(self, **data):
        obj = self.model_account.create(**data)
        return obj

    def update_user_group(self, user_id, **query):
        UserGroupRel.update(**query).where(UserGroupRel.user_record_id == user_id).execute()

