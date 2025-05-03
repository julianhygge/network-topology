from abc import abstractmethod
from typing import List

from app.data.interfaces.i_repository import IRepository, T
from app.data.schemas.load_profile.load_profile_schema import \
    LoadProfileBuilderItems


class ILoadProfileBuilderRepository(IRepository[T]):

    @abstractmethod
    def get_items_by_profile_id(self, profile_id) -> List[LoadProfileBuilderItems]:
        pass

    @abstractmethod
    def create_items_in_bulk(self, items):
        pass

    @abstractmethod
    def delete_by_profile_id(self, profile_id) -> int:
        pass

    @abstractmethod
    def update_items_in_bulk(self, items):
        pass
