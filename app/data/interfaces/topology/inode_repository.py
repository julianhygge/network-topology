from abc import abstractmethod
from app.data.interfaces.irepository import IRepository, T


class INodeRepository(IRepository[T]):
    @abstractmethod
    def get_children(self, parent_id):
        """"""

    @abstractmethod
    def read(self, id_value):
        """"""

    @abstractmethod
    def get_parent(self, node_id):
        """"""
