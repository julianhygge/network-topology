from typing import Any, Dict, List, Optional, Tuple, cast

from app.data.interfaces.solar.i_solar_repository import (
    ISolarInstallationRepository,
)
from app.data.schemas.solar.solar_schema import SolarInstallation
from app.domain.interfaces.solar.i_solar_service import (
    ISolarInstallationService,
)
from app.domain.services.base_service import BaseService
from app.mock_data_servcice import backfill_missing_data


class SolarInstallationService(
    BaseService[SolarInstallation], ISolarInstallationService
):
    """
    Service class for managing solar installations.
    """

    repository: ISolarInstallationRepository

    def __init__(self, repository: ISolarInstallationRepository):
        """
        Initializes the SolarInstallationService with a repository.

        Args:
            repository: The ISolarProfileRepository instance.
        """
        super().__init__(repository)

    def get_solar_installation(
        self, filter_key: Optional[str], limit: int, offset: int
    ) -> Tuple[List[Dict[str, Any]], int, int, int]:
        """
        Retrieves a paginated list of solar installations, optionally filtered.

        Args:
            filter_key: An optional string to filter installations by.
            limit: The maximum number of items to return.
            offset: The starting offset for pagination.

        Returns:
            A tuple containing:
                - A list of dictionaries representing solar installations.
                - The total number of items matching the criteria.
                - The total number of pages.
                - The current page number.
        """
        (
            items_objects,
            total_items,
            total_pages,
            current_page,
        ) = self.repository.get_solar_installation(filter_key, limit, offset)

        item_dict = cast(
            List[Dict[str, Any]], self.repository.to_dicts(items_objects)
        )

        return item_dict,total_items,total_pages,current_page

    def backfill_missing_data(self):
        backfill_missing_data()
