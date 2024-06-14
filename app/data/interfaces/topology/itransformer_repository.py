from abc import abstractmethod
from app.data.interfaces.irepository import IRepository, T


class ITransformerRepository(IRepository[T]):
    @abstractmethod
    def get_transformers_by_substation_id(self, substation_id):
        """"""
