"""Module for various load profile related repositories."""

from typing import Any, Dict, List, Optional
from uuid import UUID

from peewee import DoesNotExist

from app.data.interfaces.load.i_load_generation_engine_repository import (
    ILoadGenerationEngineRepository,
)
from app.data.interfaces.load.i_load_load_profile_repository import (
    ILoadProfileRepository,
)
from app.data.interfaces.load.i_load_profile_builder_repository import (
    ILoadProfileBuilderRepository,
)
from app.data.interfaces.load.i_load_profile_details_repository import (
    ILoadProfileDetailsRepository,
)
from app.data.interfaces.load.i_load_profile_files_repository import (
    ILoadProfileFilesRepository,
)
from app.data.interfaces.load.i_predefined_templates_repository import (
    IPredefinedTemplatesRepository,
)
from app.data.repositories.base_repository import BaseRepository

# Schemas used by these repositories
from app.data.schemas.load_profile.load_profile_schema import (
    LoadGenerationEngine,
    LoadPredefinedTemplates,
    LoadProfileBuilderItems,
    LoadProfileDetails,
    LoadProfileFiles,
    LoadProfiles,
)


class LoadProfilesRepository(
    BaseRepository[LoadProfiles], ILoadProfileRepository
):
    """
    Repository for managing LoadProfiles data.
    Implements ILoadProfileRepository for load profile specific operations.
    """

    def __init__(self):
        super().__init__(model=LoadProfiles)

    def get_load_profiles_by_user_id(
        self, user_id: UUID
    ) -> List[LoadProfiles]:
        """Retrieves all load profiles for a specific user."""
        try:
            return list(
                self._model.select()
                .where(
                    (self._model.user_id == user_id) & (~self._model.public)
                )
                .order_by(self._model.id.asc())
            )
        except DoesNotExist:
            return []

    def get_public_profiles(self) -> List[LoadProfiles]:
        """Retrieves all public load profiles."""
        try:
            return list(
                self._model.select()
                .where(self._model.public)
                .order_by(self._model.id.asc())
            )
        except DoesNotExist:
            return []

    def get_load_profiles_by_user_id_and_house_id(
        self, user_id: UUID, house_id: UUID
    ) -> List[LoadProfiles]:
        """Retrieves load profiles for a specific user and house."""
        try:
            return list(
                self._model.select()
                .where(
                    (self._model.user_id == user_id)
                    & (~self._model.public)
                    & (self._model.house_id == house_id)
                )
                .order_by(self._model.id.asc())
            )
        except DoesNotExist:
            return []

    def get_or_create_by_house_id(
        self, user_id: UUID, house_id: UUID, load_source: str
    ) -> LoadProfiles:
        """
        Retrieves an existing load profile by house_id or creates a new one.
        """
        try:
            profile = self._model.get(self._model.house_id == house_id)
        except DoesNotExist:
            profile = self._model.create(
                user_id=user_id,
                house_id=house_id,
                created_by=user_id,
                modified_by=user_id,
                profile_name=load_source,
                source=load_source,
                public=False,
                active=True,
            )
        return profile

    def get_by_house_id(self, house_id: UUID) -> Optional[LoadProfiles]:
        """Retrieves a load profile by its associated house_id."""
        return self._model.get_or_none(self._model.house_id == house_id)


class LoadProfileDetailsRepository(
    BaseRepository[LoadProfileDetails],
    ILoadProfileDetailsRepository[LoadProfileDetails],
):
    """
    Repository for managing LoadProfileDetails data.
    Implements ILoadProfileDetailsRepository for detail-specific operations.
    """

    def __init__(self):
        super().__init__(model=LoadProfileDetails)

    def delete_by_profile_id(self, profile_id: int) -> int:
        """
        Deletes all load profile details associated with a given profile ID.
        """
        return (
            self._model.delete()
            .where(self._model.profile_id == profile_id)
            .execute()
        )

    def create_details_in_bulk(self, details: List[Dict[str, Any]]) -> None:
        """Creates multiple load profile detail records in bulk."""
        self._model.insert_many(details).execute()

    def get_load_details_by_load_id(
        self, load_id: UUID
    ) -> Optional[List[Dict[str, Any]]]:
        """
        Retrieves load profile details (timestamp, consumption) by load ID.
        """
        load_details_dicts = (
            self._model.select(
                self._model.timestamp, self._model.consumption_kwh
            )
            .where(self._model.profile_id == load_id)
            .order_by(self._model.timestamp.asc())
            .dicts()
        )
        return list(load_details_dicts) if load_details_dicts else None


class LoadProfileFilesRepository(
    BaseRepository[LoadProfileFiles],
    ILoadProfileFilesRepository[LoadProfileFiles],
):
    """
    Repository for managing files associated with LoadProfiles.
    Implements ILoadProfileFilesRepository for file-specific operations.
    """

    def __init__(self):
        super().__init__(model=LoadProfileFiles)

    def save_file(
        self, profile_id: UUID, filename: str, content: bytes
    ) -> LoadProfileFiles:
        """Saves a file associated with a load profile."""
        return self._model.create(
            profile_id=profile_id, filename=filename, content=content
        )

    def get_file(self, file_id: UUID) -> Optional[LoadProfileFiles]:
        """
        Retrieves a file record by its ID (assuming file_id is profile_id here
        based on implementation).
        """
        # Implementation uses profile_id for lookup, so file_id is profile_id
        return self._model.get_or_none(self._model.profile_id == file_id)


class LoadProfileBuilderItemsRepository(
    BaseRepository[LoadProfileBuilderItems],
    ILoadProfileBuilderRepository[LoadProfileBuilderItems],
):
    """
    Repository for managing items used in building LoadProfiles.
    Implements ILoadProfileBuilderRepository for builder item operations.
    """

    def __init__(self):
        super().__init__(model=LoadProfileBuilderItems)

    def get_items_by_profile_id(
        self, profile_id: int
    ) -> List[LoadProfileBuilderItems]:
        """
        Retrieves all builder items associated with a specific load profile.
        """
        return list(
            self._model.select().where(self._model.profile_id == profile_id)
        )

    def create_items_in_bulk(self, items: List[Dict[str, Any]]) -> None:
        """Creates multiple load profile builder items in bulk."""
        self._model.insert_many(items).execute()

    def delete_by_profile_id(self, profile_id: int) -> int:
        """
        Deletes all builder items associated with a specific load profile.
        """
        return (
            self._model.delete()
            .where(self._model.profile_id == profile_id)
            .execute()
        )

    def update_items_in_bulk(self, items: List[Dict[str, Any]]) -> None:
        """
        Updates multiple load profile builder items in bulk.
        Each dictionary in items should include an 'id' field.
        """
        with self.database_instance.atomic():
            for item_data in items:
                item_id = item_data.get("id")
                if item_id is None:
                    # Or raise error, or log and skip
                    continue
                self._model.update(**item_data).where(
                    self._model.id == item_id
                ).execute()


class LoadGenerationEngineRepository(
    BaseRepository[LoadGenerationEngine],
    ILoadGenerationEngineRepository[LoadGenerationEngine],
):
    """
    Repository for LoadGenerationEngine settings.
    Implements ILoadGenerationEngineRepository.
    """

    def __init__(self):
        super().__init__(model=LoadGenerationEngine)

    def delete_by_profile_id(self, profile_id: int) -> int:
        """
        Deletes load generation engine settings for a profile ID.
        """
        return (
            self._model.delete()
            .where(self._model.profile_id == profile_id)
            .execute()
        )


class PredefinedTemplatesRepository(
    BaseRepository[LoadPredefinedTemplates],
    IPredefinedTemplatesRepository[LoadPredefinedTemplates],
):
    """
    Repository for managing predefined templates linked to LoadProfiles.
    Implements IPredefinedTemplatesRepository.
    """

    def __init__(self):
        super().__init__(model=LoadPredefinedTemplates)

    def get_by_profile_id(
        self, profile_id: int
    ) -> Optional[LoadPredefinedTemplates]:
        """
        Retrieves a predefined template record by its associated profile ID.
        """
        return self._model.get_or_none(self._model.profile_id == profile_id)

    def create_or_update(
        self, profile_id: int, template_id: int
    ) -> LoadPredefinedTemplates:
        """
        Creates or updates a predefined template linked to a load profile.
        """
        # Ensure defaults is a dictionary
        defaults_data = {"template_id": template_id}
        template, created = self._model.get_or_create(
            profile_id=profile_id,
            defaults=defaults_data,
        )
        if not created:
            # Only update if it changed and is different
            if template.template_id != template_id:
                template.template_id = template_id
                template.save()
        return template
