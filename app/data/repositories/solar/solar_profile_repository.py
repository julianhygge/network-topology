# pyright: reportUnknownMemberType=false, reportUnknownVariableType=false

"""
Solar Profile Repository implementation.

This module provides the concrete implementation for managing SolarProfile
data, extending the generic BaseRepository and implementing the
ISolarProfileRepository interface.
"""

from typing import Optional
from uuid import UUID

from app.data.interfaces.solar.i_solar_profile_repository import (
    ISolarProfileRepository,
)
from app.data.repositories.base_repository import BaseRepository
from app.data.schemas.solar.solar_profile_schema import SolarProfile


class SolarProfileRepository(
    BaseRepository[SolarProfile], ISolarProfileRepository
):
    """
    Repository for managing SolarProfile data.

    This class extends `BaseRepository` to provide generic CRUD operations
    for the `SolarProfile` model and implements `ISolarProfileRepository`
    for specific data access methods related to solar profiles.
    """

    def get_solar_profile_by_house_id(
        self, house_id: UUID
    ) -> Optional[SolarProfile]:
        """
        Retrieves a solar profile by its associated house ID.

        Args:
            house_id: The UUID of the house.

        Returns:
            A SolarProfile instance if found, otherwise None.
        """
        solar_profile: SolarProfile = self.model.get_or_none(
            self.model.house_id == house_id
        )

        return solar_profile

    def delete_solar_profile_by_house_id(self, house_id: UUID) -> int:
        """
        Deletes a solar profile by its associated house ID.

        Args:
            house_id: The UUID of the house.

        Returns:
            The number of rows deleted.
        """
        query = self.model.delete().where(self.model.house_id == house_id)
        return query.execute()
