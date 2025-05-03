from typing import List
from uuid import UUID

from peewee import DoesNotExist

from app.data.interfaces.load.i_load_generation_enginer_repository import \
    ILoadGenerationEngineRepository
from app.data.interfaces.load.i_load_load_profile_repository import \
    ILoadProfileRepository
from app.data.interfaces.load.i_load_profile_builder_repository import \
    ILoadProfileBuilderRepository
from app.data.interfaces.load.i_load_profile_details_repository import \
    ILoadProfileDetailsRepository
from app.data.interfaces.load.i_load_profile_files_repository import \
    ILoadProfileFilesRepository
from app.data.interfaces.load.i_predefined_templates_repository import \
    IPredefinedTemplatesRepository
from app.data.repositories.base_repository import BaseRepository
from app.data.schemas.load_profile.load_profile_schema import (
    LoadGenerationEngine, LoadPredefinedTemplates, LoadProfileBuilderItems,
    LoadProfileDetails, LoadProfileFiles, LoadProfiles)


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

    def get_or_create_by_house_id(self, user_id: UUID, house_id: UUID, load_source):
        try:
            profile = self.model.get(self.model.house_id == house_id)
        except DoesNotExist:
            profile = self.model.create(
                user_id=user_id,
                house_id=house_id,
                created_by=user_id,
                modified_by=user_id,
                profile_name=load_source,
                source=load_source,
                public=False,
                active=True
            )

        return profile

    def get_by_house_id(self, house_id: int):
        profile = self.model.get(house_id=house_id)
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


class LoadProfileBuilderItemsRepository(BaseRepository, ILoadProfileBuilderRepository):
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


class LoadGenerationEngineRepository(BaseRepository, ILoadGenerationEngineRepository):
    model = LoadGenerationEngine
    id_field = LoadGenerationEngine.id

    def delete_by_profile_id(self, profile_id) -> int:
        return self.model.delete().where(self.model.profile_id == profile_id).execute()


class PredefinedTemplatesRepository(BaseRepository, IPredefinedTemplatesRepository):
    model = LoadPredefinedTemplates
    id_field = LoadPredefinedTemplates.id

    def get_by_profile_id(self, profile_id):
        return self.model.get_or_none(self.model.profile_id == profile_id)

    def create_or_update(self, profile_id, template_id):
        template, created = self.model.get_or_create(
            profile_id=profile_id,
            defaults={
                'template_id': template_id
            }
        )
        if not created:
            template.template_id = template_id
            template.save()
        return template
