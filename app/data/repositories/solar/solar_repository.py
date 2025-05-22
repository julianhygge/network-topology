# pyright: reportUnknownMemberType=false, reportUnknownVariableType=false

"""
Solar Profile Repository implementation.

This module provides the concrete implementation for managing SolarProfile
data, extending the generic BaseRepository and implementing the
ISolarProfileRepository interface.
"""

from uuid import UUID

from peewee import ModelSelect

from app.data.interfaces.solar.i_solar_repository import (
    ISolarInstallationRepository,
    ISolarProfileRepository,
)
from app.data.repositories.base_repository import BaseRepository
from app.data.schemas.solar.solar_schema import SolarInstallation, SolarProfile


class SolarProfileRepository(
    BaseRepository[SolarProfile], ISolarProfileRepository
):
    """
    Repository for managing SolarProfile data.

    This class extends `BaseRepository` to provide generic CRUD operations
    for the `SolarProfile` model and implements `ISolarProfileRepository`
    for specific data access methods related to solar profiles.
    """

    def __init__(self):
        super().__init__(model=SolarProfile)

    def delete_solar_profile_by_house_id(self, house_id: UUID) -> int:
        """
        Deletes a solar profile by its associated house ID.

        Args:
            house_id: The UUID of the house.

        Returns:
            The number of rows deleted.
        """
        query = self._model.delete().where(self._model.house_id == house_id)
        return query.execute()


class SolarInstallationRepository(
    BaseRepository[SolarInstallation], ISolarInstallationRepository
):
    def __init__(self):
        super().__init__(model=SolarInstallation)

    def get_solar_installation(
        self, filter_key: str | None, limit: int | None, offset: int | None
    ) -> tuple[list[SolarInstallation], int, int, int]:
        base_query: ModelSelect = self._model.select().where(
            (self._model.status == "Active")
            & (self._model.profile_updated_on.is_null(False))
        )

        if filter_key:
            filter_condition = (
                self._model.city.contains(filter_key)
                | self._model.country.contains(filter_key)
                | self._model.zip_code.contains(filter_key)
            )
            query = base_query.where(filter_condition)
        else:
            query = base_query

        total_items = query.count()
        total_pages = (total_items + limit - 1) // limit if limit else 1
        current_page = 1
        if limit and offset is not None:
            current_page = (offset // limit) + 1

        if limit:
            query = query.limit(limit)
        if offset is not None:
            query = query.offset(offset)

        items = list(query.execute())

        return items, total_items, total_pages, current_page
