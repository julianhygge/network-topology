"""
Implementation of the Solar Profile Service.
"""
from typing import Any, Dict, cast
from uuid import UUID

# IRepository import removed
from app.data.interfaces.solar.i_solar_profile_repository import (  # Added
    ISolarProfileRepository,
)
from app.data.schemas.solar.solar_profile_schema import SolarProfile
from app.domain.interfaces.solar.i_solar_profile_service import (
    ISolarProfileService,
)
from app.domain.services.base_service import BaseService


class SolarProfileService(BaseService[SolarProfile], ISolarProfileService):
    """
    Service class for managing solar profiles.
    """

    def __init__(self, repository: ISolarProfileRepository):
        """
        Initializes the SolarProfileService with a repository.

        Args:
            repository: The ISolarProfileRepository instance.
        """
        super().__init__(repository)
        # Re-annotate self.repository to its specific type
        # ISolarProfileRepository. This allows access to specific methods
        # like get_solar_profile_by_house_id. Pylance might warn about this
        # override if it's overly strict on variance, but
        # ISolarProfileRepository is a subtype of IRepository[SolarProfile].
        self.repository: ISolarProfileRepository = repository

    def create(self, user_id: UUID, **kwargs: Any) -> Dict[str, Any]:
        """
        Creates a new solar profile.

        Args:
            user_id: The UUID of the user creating the profile.
            **kwargs: Keyword arguments containing the solar profile data.

        Returns:
            A dictionary representation of the created solar profile.
        """
        kwargs["id"] = kwargs["house_id"]
        kwargs["created_by"] = user_id
        kwargs["modified_by"] = user_id
        kwargs["active"] = True

        if not kwargs.get("solar_available"):
            kwargs["installed_capacity_kw"] = None
            kwargs["years_since_installation"] = None

        if not kwargs.get("solar_available") and not kwargs.get(
            "simulate_using_different_capacity"
        ):
            kwargs["simulated_available_space_sqft"] = None

        created = self.repository.create(**kwargs)
        # `to_dicts` from BaseRepository should return Dict[str, Any]
        # when a single model instance is passed.
        created_dict = cast(Dict[str, Any], self.repository.to_dicts(created))

        # `created.tilt_type` is a CharField.
        # Check for existing and truthy (non-empty) tilt_type.
        if hasattr(created, "tilt_type") and created.tilt_type:
            created_dict["tilt_type"] = created.tilt_type
        return created_dict

    def get_solar_profile_by_house_id(
        self, house_id: UUID
    ) -> Dict[str, Any] | None:
        """
        Retrieves a solar profile by its associated house ID.

        Args:
            house_id: The UUID of the house.

        Returns:
            A dictionary representation of the solar profile if found,
            otherwise None.
        """
        lst = self.repository.get_solar_profile_by_house_id(house_id)
        if lst is not None:
            # `lst` is a SolarProfile model instance here.
            # `to_dicts` should return Dict[str, Any].
            solar_data = cast(Dict[str, Any], self.repository.to_dicts(lst))
            return solar_data
        return None

    def delete_solar_profile_by_house_id(self, house_id: UUID) -> None:
        """
        Deletes a solar profile by its associated house ID.

        Args:
            house_id: The UUID of the house.
        """
        self.repository.delete_solar_profile_by_house_id(house_id)

    def update_solar_profile(
        self, user_id: UUID, house_id: UUID, **kwargs: Any
    ) -> None:
        """
        Updates an existing solar profile.

        Args:
            user_id: The UUID of the user updating the profile.
            house_id: The UUID of the house associated with the profile.
            **kwargs: Keyword arguments containing the updated solar profile
                data.
        """
        kwargs["modified_by"] = user_id
        self.repository.update(house_id, **kwargs)
