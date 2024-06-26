from abc import abstractmethod
from app.data.interfaces.irepository import IRepository, T


class INodeRepository(IRepository[T]):
    @abstractmethod
    def get_children(self, parent_id):
        """"""
