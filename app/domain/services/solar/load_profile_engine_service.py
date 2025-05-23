"""Service for managing load profile generation engine configurations."""

from typing import Any, Optional
from uuid import UUID

from app.data.interfaces.load.i_load_generation_engine_repository import (
    ILoadGenerationEngineRepository,
)
from app.data.interfaces.load.i_load_load_profile_repository import (
    ILoadProfileRepository,
)
from app.domain.interfaces.enums.load_source_enum import LoadSource


class LoadProfileEngineService:
    """
    Service responsible for managing configurations related to the
    load profile generation engine.
    """

    def __init__(
        self,
        load_profile_repo: ILoadProfileRepository,
        load_gen_engine_repo: ILoadGenerationEngineRepository,
    ):
        self._load_profile_repo = load_profile_repo
        self._load_generation_engine_repository = load_gen_engine_repo

    def save_load_generation_engine(
        self, user_id: UUID, house_id: UUID, data: dict
    ) -> Any:  # Assuming LoadGenerationEngine
        """
        Saves or updates the load generation engine configuration for a given
        house and user.
        """
        load_profile = self._load_profile_repo.get_or_create_by_house_id(
            user_id, house_id, LoadSource.Engine.value
        )
        profile_id = load_profile.id

        engine_data = {
            "user_id": user_id,
            "profile_id": profile_id,  
            "type": data["type"],
            "average_kwh": data.get("average_kwh"),
            "average_monthly_bill": data.get("average_monthly_bill"),
            "max_demand_kw": data.get("max_demand_kw"),
            "created_by": user_id,
            "modified_by": user_id,
        }
        self._load_generation_engine_repository.delete_by_profile_id(
            profile_id
        )

        created_engine_config = self._load_generation_engine_repository.create(
            engine_data
        )

        return created_engine_config

    def get_load_generation_engine(
        self, user_id: UUID, house_id: UUID
    ) -> Optional[Any]:  # Assuming Optional[LoadGenerationEngine]
        """
        Retrieves the load generation engine configuration for a given
        house and user.
        """
        load_profiles = (
            self._load_profile_repo.get_load_profiles_by_user_id_and_house_id(
                user_id, house_id
            )
        )

        engine_profile = next(
            (
                profile
                for profile in load_profiles
                if profile.source == LoadSource.Engine.value
            ),
            None,
        )

        if engine_profile:
            return self._load_generation_engine_repository.filter(
                profile_id=engine_profile.id
            )[0]
        return None
