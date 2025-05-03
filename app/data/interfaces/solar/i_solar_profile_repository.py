from abc import abstractmethod

from app.data.interfaces.i_repository import IRepository, T


class ISolarProfileRepository(IRepository[T]):
    @abstractmethod
    def get_solar_profile_by_house_id(self, house_id):
        """"""

    @abstractmethod
    def delete_solar_profile_by_house_id(self, house_id):
        """"""
