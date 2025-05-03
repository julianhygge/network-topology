from app.data.interfaces.solar.i_solar_profile_repository import \
    ISolarProfileRepository
from app.data.repositories.base_repository import BaseRepository
from app.data.schemas.solar.solar_profile_schema import SolarProfile


class SolarProfileRepository(BaseRepository, ISolarProfileRepository):
    model = SolarProfile
    id_field = SolarProfile.id

    def get_solar_profile_by_house_id(self, house_id):
        return self.model.get_or_none(self.model.house_id == house_id)
     

    def delete_solar_profile_by_house_id(self, house_id):
        return self.model.delete().where(self.model.house_id == house_id).execute()



