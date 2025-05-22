from app.data.interfaces.solar.i_solar_repository import ISolarInstallationRepository
from app.data.schemas.solar.solar_schema import SolarInstallation
from app.domain.interfaces.solar.i_solar_service import ISolarInstallationService
from app.domain.services.base_service import BaseService
from app.mock_data_servcice import backfill_missing_data


class SolarInstallationService(BaseService[SolarInstallation], ISolarInstallationService):
    """
    Service class for managing solar profiles.
    """

    repository: ISolarInstallationRepository

    def __init__(self, repository: ISolarInstallationRepository):
        """
        Initializes the SolarProfileService with a repository.

        Args:
            repository: The ISolarProfileRepository instance.
        """
        super().__init__(repository)

    def get_solar_installation(self, filter_key, limit, offset):
        query = self.repository.get_solar_installation(filter_key)

        total_items = query.count()
        total_pages = (total_items + limit - 1) // limit if limit else 1
        current_page = (offset // limit) + 1 if limit and offset else 1

        if limit:
            query = query.limit(limit)
        if offset:
            query = query.offset(offset)

        items = query.execute()
        item_dict = self.repository.to_dicts(list(items))

        return item_dict,total_items,total_pages,current_page

    def backfill_missing_data(self):
        backfill_missing_data()