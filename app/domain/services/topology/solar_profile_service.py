from typing import Dict, Any

from app.domain.interfaces.solar.isolar_profile_service import ISolarProfileService
from app.domain.services.base_service import BaseService
from app.data.repositories.solar.solar_profile_repository import SolarProfileRepository


class SolarProfileService(BaseService, ISolarProfileService):
    def __init__(self, repository: SolarProfileRepository):
        super().__init__(repository)
        self.repository = repository

    def create(self, user_id, **data):
        data['id'] = data['house_id']
        data["created_by"] = user_id
        data["modified_by"] = user_id
        data["active"] = True

        if not data['solar_available']:
            data['installed_capacity_kw'] = None
            data['years_since_installation'] = None

        if not data['solar_available'] and not data['simulate_using_different_capacity']:
            data['simulated_available_space_sqft'] = None

        created = self.repository.create(**data)
        created_dicts = self.repository.to_dicts(created)
        created_dicts['tilt_type'] = created.tilt_type.value
        return created_dicts

    def get_solar_profile_by_house_id(self, house_id):
        lst = self.repository.get_solar_profile_by_house_id(house_id)

        solar_data = self.repository.to_dicts(lst)

        return solar_data

    def delete_solar_profile_by_house_id(self, house_id):
        self.repository.delete_solar_profile_by_house_id(house_id)

    def update_solar_profile(self, user_id, house_id, **data):
        data['modified_by'] = user_id
        self.repository.update(house_id, **data)
        # self.repository.update_solar_profile(user_id, house_id, **data)
