"""Service for managing household load profiles"""

from typing import (
    Any,
    Dict,
    List,
    Optional,
    Tuple,
    Union,
)
from uuid import UUID

from app.data.interfaces.load.i_load_load_profile_repository import (
    ILoadProfileRepository,
)
from app.data.interfaces.load.i_load_profile_details_repository import (
    ILoadProfileDetailsRepository,
)
from app.data.interfaces.load.i_load_profile_files_repository import (
    ILoadProfileFilesRepository,
)
from app.domain.interfaces.enums.load_source_enum import LoadSource
from app.domain.services.base_service import BaseService
from app.domain.services.solar.load_profile_builder_service import (
    LoadProfileBuilderService,
)
from app.domain.services.solar.load_profile_engine_service import (
    LoadProfileEngineService,
)

# Import new specialized services
from app.domain.services.solar.load_profile_file_service import (
    LoadProfileFileService,
)
from app.domain.services.solar.load_profile_template_service import (
    LoadProfileTemplateService,
)


class LoadProfileService(BaseService):
    """
    Main service for managing load profiles. It orchestrates operations by
    delegating to more specialized services for file handling, builder logic,
    engine configurations, and template-based generation.
    """

    def __init__(
        self,
        repository: ILoadProfileRepository,
        load_details_repository: ILoadProfileDetailsRepository,
        load_profile_files_repository: ILoadProfileFilesRepository,
        load_profile_file_service: LoadProfileFileService,
        load_profile_builder_service: LoadProfileBuilderService,
        load_profile_engine_service: LoadProfileEngineService,
        load_profile_template_service: LoadProfileTemplateService,
    ):
        super().__init__(repository)
        self._load_profile_repo = repository
        self._load_details_repository = load_details_repository
        self._load_profile_files_repository = load_profile_files_repository
        self._file_service = load_profile_file_service
        self._builder_service = load_profile_builder_service
        self._engine_service = load_profile_engine_service
        self._template_service = load_profile_template_service

    def _map_profile_to_dict(self, profile: Any) -> Dict[str, Any]:
        """Maps a load profile ORM object to a dictionary for API responses."""
        data = {
            "house_id": str(profile.house_id.id) if profile.house_id else None,
            "profile_id": str(profile.id),
            "active": profile.active,
            "profile_name": profile.profile_name,
            "user": str(profile.user_id.name),
            "user_id": str(profile.user_id.id) if profile.user_id else None,
            "user_name": profile.user_id.name if profile.user_id else None,
            "created_on": profile.created_on.isoformat()
            if profile.created_on
            else None,
            "modified_on": profile.modified_on.isoformat()
            if profile.modified_on
            else None,
            "source": profile.source,
        }
        if profile.source == LoadSource.File.value:
            try:
                file_record = self._load_profile_files_repository.get_file(
                    profile.id
                )
                data["file_name"] = (
                    file_record.filename if file_record else None
                )
            except Exception:  # pylint: disable=broad-except
                data["file_name"] = None
        return data

    def delete_profile(self, profile_id: UUID) -> Any:
        """
        Deletes a load profile and its associated details.
        Note: File content deletion from storage is handled
        by LoadProfileFileService if needed.
        """
        self._load_details_repository.delete_by_profile_id(profile_id)
        deleted_profile = self._load_profile_repo.delete(profile_id)
        return deleted_profile

    def list_profiles(
        self, user_id: UUID, house_id: UUID
    ) -> List[Dict[str, Any]]:
        """
        Lists all accessible load profiles for a user and house, including
        public profiles.
        """
        private_profiles = list(
            self._get_load_profiles_by_user_id(user_id, house_id)
        )
        public_profiles = list(self._get_public_profiles())
        combined_profiles_map = {str(p.id): p for p in public_profiles}
        for p in private_profiles:
            combined_profiles_map[str(p.id)] = p

        return [
            self._map_profile_to_dict(profile)
            for profile in combined_profiles_map.values()
        ]

    def _get_load_profiles_by_user_id(
        self, user_id: UUID, house_id: UUID
    ) -> List[Any]:  # Assuming List[LoadProfileModel]
        """Retrieves private load profiles for a specific user and house."""
        return (
            self._load_profile_repo.get_load_profiles_by_user_id_and_house_id(
                user_id, house_id
            )
        )

    def _get_public_profiles(
        self,
    ) -> List[Any]:
        """Retrieves all public load profiles."""
        return self._load_profile_repo.get_public_profiles()

    # Methods to be delegated, called from API layer through this service:

    async def upload_profile_file(
        self,
        user_id: UUID,
        profile_name: str,
        file: Any,  # FastAPI UploadFile
        interval_15_minutes: bool,
        house_id: UUID,
    ) -> Dict[str, Union[str, UUID]]:
        """Delegates file upload to LoadProfileFileService."""
        return await self._file_service.upload_profile_file(
            user_id=user_id,
            profile_name=profile_name,
            file=file,
            interval_15_minutes=interval_15_minutes,
            house_id=house_id,
        )

    def save_load_profile_items(
        self, user_id: UUID, house_id: UUID, items: List[dict]
    ) -> Tuple[List[Any], UUID]:
        """Delegates saving load profile items to LoadProfileBuilderService."""
        return self._builder_service.save_load_profile_items(
            user_id=user_id, house_id=house_id, items=items
        )

    def get_load_profile_builder_items(
        self, user_id: UUID, house_id: UUID
    ) -> Tuple[List[Any], UUID]:
        """Delegates getting builder items to LoadProfileBuilderService."""
        return self._builder_service.get_load_profile_builder_items(
            user_id=user_id, house_id=house_id
        )

    def get_load_profile_file_content(self, profile_id: UUID) -> Any:
        """Delegates getting file content to LoadProfileFileService."""
        return self._file_service.get_load_profile_file_content(profile_id)

    def save_load_generation_engine_config(
        self, user_id: UUID, house_id: UUID, data: dict
    ) -> Any:
        """Delegates saving engine config to LoadProfileEngineService."""
        return self._engine_service.save_load_generation_engine(
            user_id=user_id, house_id=house_id, data=data
        )

    def get_load_generation_engine_config(
        self, user_id: UUID, house_id: UUID
    ) -> Optional[Any]:  # Return type from engine service
        """Delegates getting engine config to LoadProfileEngineService."""
        return self._engine_service.get_load_generation_engine(
            user_id=user_id, house_id=house_id
        )

    def create_or_update_profile_from_template(
        self, user_id: UUID, house_id: UUID, template_id: int
    ) -> Any:
        """Delegates creating/updating from template
        to LoadProfileTemplateService."""
        return (
            self._template_service.create_or_update_load_predefined_template(
                user_id=user_id, house_id=house_id, template_id=template_id
            )
        )

    def get_profile_template_config(
        self, user_id: UUID, house_id: UUID
    ) -> Optional[Any]:  # Return type from template service
        """Delegates getting template config to LoadProfileTemplateService."""
        return self._template_service.get_load_predefined_template(
            user_id=user_id, house_id=house_id
        )

    async def generate_profile_values_from_template(
        self,
        template_id: int,
        profile_items: List[Any],  # List[PersonProfileItem]
    ) -> Dict[str, Any]:
        """Delegates generating profile values
        to LoadProfileTemplateService.
        """
        return await self._template_service.generate_profile_from_template(
            template_id=template_id, profile_items=profile_items
        )
