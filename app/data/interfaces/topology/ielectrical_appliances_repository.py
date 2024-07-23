from abc import abstractmethod

from app.data.interfaces.irepository import IRepository, T


class IElectricalAppliancesRepository(IRepository[T]):

    @abstractmethod
    def read(self, id_value) -> T:
        pass
