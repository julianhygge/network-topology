from abc import ABC, abstractmethod
from typing import TypeVar, Generic, List, Dict, Union, Any
from uuid import UUID

T = TypeVar('T')


class IRepository(ABC, Generic[T]):
    @property
    @abstractmethod
    def model(self) -> Any:
        pass

    @property
    @abstractmethod
    def id_field(self) -> Union[int, UUID]:
        pass

    @abstractmethod
    def create(self, **query) -> T:
        pass

    @abstractmethod
    def read(self, id_value) -> T:
        pass

    @abstractmethod
    def update(self, id_value, **query) -> int:
        pass

    @abstractmethod
    def delete(self, id_value) -> int:
        pass

    @abstractmethod
    def list(self) -> List[T]:
        pass

    @abstractmethod
    def list_actives(self) -> List[T]:
        pass

    @abstractmethod
    def list_public(self) -> List[T]:
        pass

    @abstractmethod
    def upsert(self, conflict_target: List[str], defaults: Dict[str, any], **query) -> T:
        pass

    @abstractmethod
    def upsert_and_retrieve(self, conflict_target: List[str], defaults: Dict[str, any], **query) -> T:
        pass

    @abstractmethod
    def list_no_public_by_user_id(self, user_id) -> List[T]:
        pass

    @property
    @abstractmethod
    def database_instance(self):
        pass

    @abstractmethod
    def to_dicts(self, obj) -> Union[Dict[str, Any], List[Dict[str, Any]], Any]:
        pass

    def list_by_user_id(self, user_id) -> List[T]:
        return list(self.model.select().where((self.model.created_by == user_id) &
                                              self.model.active))