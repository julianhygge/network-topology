from abc import abstractmethod
from typing import List, Optional
from uuid import UUID

from app.data.interfaces.i_repository import IRepository, T
from app.data.schemas.transactional.topology_schema import Locality, Node, Substation


class INodeRepository(IRepository[T]):
    @abstractmethod
    def get_children(self, parent_id: UUID) -> List[Node]:
        """"""

    @abstractmethod
    def read(self, id_value: UUID) -> Optional[Node]:
        """"""

    @abstractmethod
    def get_parent(self, node_id: UUID) -> Optional[Node]:
        """"""

    @abstractmethod
    def get_substation(self, node_id: UUID) -> Optional[Substation]:
        """"""

    @abstractmethod
    def get_locality(self, node_id: UUID) -> Optional[Locality]:
        """"""
