from typing import List
from peewee import DoesNotExist
from app.data.interfaces.load.iload_load_profile_repository import ILoadProfileRepository
from app.data.interfaces.load.iload_profile_details_repository import ILoadProfileDetailsRepository
from app.data.interfaces.load.iload_profile_files_repository import ILoadProfileFilesRepository
from app.data.repositories.base_repository import BaseRepository
from app.data.schemas.load_profile.load_profile_schema import LoadProfiles, LoadProfileDetails, LoadProfileFiles, \
    LoadProfileBuilderItems


class LoadProfilesRepository(BaseRepository, ILoadProfileRepository):
    model = LoadProfiles
    id_field = LoadProfiles.id

    def get_load_profiles_by_user_id(self, user_id) -> List[LoadProfiles]:
        try:
            return list(self.model.select().where((self.model.user_id == user_id) & (~self.model.public))
                        .order_by(self.model.id.asc()))
        except DoesNotExist:
            return []

    def get_public_profiles(self) -> List[LoadProfiles]:
        try:
            return list(self.model.select().where(self.model.public).order_by(self.model.id.asc()))
        except DoesNotExist:
            return []

    def get_load_profiles_by_user_id_and_house_id(self, user_id, house_id) -> List[LoadProfiles]:
        try:
            return list(self.model.select().where((self.model.user_id == user_id) & (~self.model.public) &
                                                  (self.model.house_id == house_id))
                        .order_by(self.model.id.asc()))
        except DoesNotExist:
            return []

    def get_or_create_by_house_id(self, house_id: int):
        profile, created = self.model.get_or_create(house_id=house_id)
        return profile


class LoadProfileDetailsRepository(BaseRepository, ILoadProfileDetailsRepository):
    model = LoadProfileDetails
    id_field = LoadProfileDetails.id

    def delete_by_profile_id(self, profile_id) -> int:
        return self.model.delete().where(self.model.profile_id == profile_id).execute()

    def create_details_in_bulk(self, details):
        self.model.insert_many(details).execute()

    def get_load_details_by_load_id(self, load_id):
        load_details_dicts = (self.model
                              .select(self.model.timestamp, self.model.consumption_kwh)
                              .where(self.model.profile_id == load_id)
                              .order_by(self.model.timestamp.asc())
                              .dicts())

        return list(load_details_dicts) if load_details_dicts else None


class LoadProfileFilesRepository(BaseRepository, ILoadProfileFilesRepository):
    model = LoadProfileFiles
    id_field = LoadProfileFiles.id

    def save_file(self, profile_id, filename, content):
        return self.model.create(profile_id=profile_id, filename=filename, content=content)

    def get_file(self, profile_id):
        return self.model.get(self.model.profile_id == profile_id)


class LoadProfileBuilderItemsRepository(BaseRepository):
    model = LoadProfileBuilderItems
    id_field = LoadProfileBuilderItems.id

    def get_items_by_profile_id(self, profile_id) -> List[LoadProfileBuilderItems]:
        return list(self.model.select().where(self.model.profile_id == profile_id))

    def create_items_in_bulk(self, items):
        self.model.insert_many(items).execute()

    def delete_by_profile_id(self, profile_id) -> int:
        return self.model.delete().where(self.model.profile_id == profile_id).execute()

    def update_items_in_bulk(self, items):
        with self.database_instance.atomic():
            for item in items:
                self.model.update(**item).where(self.model.id == item['id']).execute()
