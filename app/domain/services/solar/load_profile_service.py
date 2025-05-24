"""Service for managing household load profiles"""

from typing import (
    Any,
    Dict,
    List,
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
from app.domain.interfaces.solar.i_load_profile_service import (
    ILoadProfileService,
)


class LoadProfileService(ILoadProfileService):
    """
    Service for managing load profiles. This service handles core load profile
    operations like listing and deletion, and does not delegate to other
    specialized services.
    """

    def __init__(
        self,
        repository: ILoadProfileRepository,
        load_details_repository: ILoadProfileDetailsRepository,
        load_profile_files_repository: ILoadProfileFilesRepository,
    ):
        self._load_profile_repo = repository
        self._load_details_repository = load_details_repository
        self._load_profile_files_repository = load_profile_files_repository

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
    ) -> List[Any]:
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
