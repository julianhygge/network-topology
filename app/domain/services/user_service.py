import datetime
import uuid
from typing import List, Dict, Any

from app.data.interfaces.irepository import IRepository
from app.data.interfaces.iuser_repository import IUserRepository
from app.domain.interfaces.i_token_service import ITokenService
from app.domain.interfaces.i_user_service import IUserService
from app.domain.interfaces.enums.groups_enum import Groups
from app.domain.services.base_service import BaseService


class UserService(BaseService, IUserService):

    def __init__(self, token_service: ITokenService,
                 user_repository: IUserRepository,
                 group_repository: IRepository,
                 account_repository: IRepository,
                 user_group_repository):
        super().__init__(user_repository)
        self._token_service = token_service
        self._user_repository = user_repository
        self._user_group_repository = user_group_repository
        self._group_repository = group_repository
        self._account_repository = account_repository

    def create(self, user_id, **user_data):
        account = self._user_repository.fetch_account_by_phone_number(user_data['phone_number'])

        txn_id = str(uuid.uuid4())

        user_data["id"] = account.id
        user_data["created_by"] = account.id
        user_data['modified_by'] = account.id
        user_data["record_id"] = account.id
        user_data["user_name"] = user_data["name"]
        user_data["alias_name"] = user_data["name"]
        user_data["active"] = True

        data = {
            "created_by": account.id,
            "modified_by": account.id,
            "user_record_id": account.id,
            "group_id": Groups.User.value,
            "active": True

        }
        account_data = {
            "type": str(Groups.User),
            "alias_name": user_data["name"]
        }

        with self._user_repository.database_instance.atomic():
            user = self._user_repository.insert_into_user_and_group(user_data, data)
            self._account_repository.update(account.id, **account_data)
        updated_account = self._account_repository.read(account.id)
        session_token = self._token_service.issue_new_token(account, txn_id)
        refresh_token = self._token_service.issue_refresh_token(account)
        user["session_token"] = session_token
        user["refresh_token"] = refresh_token
        user["role"] = updated_account.type
        user["name"] = updated_account.alias_name

        return user

    def list_all(self) -> List[Dict[str, Any]]:
        list_items = self._user_repository.list_actives()
        list_dicts = self.repository.to_dicts(list_items)
        print(list_dicts)

        all_groups = self._group_repository.list()
        all_groups_dicts = self.repository.to_dicts(all_groups)

        groups_info = {group['id']: group for group in all_groups_dicts}

        for item in list_dicts:
            user_groups = self._user_group_repository.get_groups_by_user_id(item["id"])
            user_groups_dicts = self.repository.to_dicts(user_groups)
            user_group_ids = set(group['id'] for group in user_groups_dicts)

            item['groups'] = [
                {'id': group_id, 'name': groups_info[group_id]['description'], 'is_member': group_id in user_group_ids}
                for group_id in groups_info]

        return list_dicts

    def delete(self, user_id):
        with self._user_repository.database_instance.atomic():
            self._user_group_repository.delete_by_user_id(user_id)
            return self._user_repository.delete(user_id)

    def add_user_to_group(self, logged_user_id, user_id, group_id):
        result = self._user_group_repository.add_user_to_group(logged_user_id, user_id, group_id)
        return result

    def remove_user_from_group(self, user_id, group_id):
        result = self._user_group_repository.remove_user_from_group(user_id, group_id)
        return result

    def update_user_logo(self, session_user, user_id, file_logo):
        data = {
            "modified_by": session_user,
            "logo": file_logo,
            "modified_on": datetime.datetime.utcnow()
        }
        obj = self._user_repository.update(user_id, **data)
        return obj

    def get_user_logo(self, user_id):
        user = self._user_repository.read(user_id)
        if user.logo:
            return user.logo
        else:
            return None
