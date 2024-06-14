from abc import abstractmethod

from app.data.interfaces.irepository import IRepository, T


class IHouseRepository(IRepository[T]):
    @abstractmethod
    def get_houses_by_substation_id(self, substation_id):
        """"""
