from abc import abstractmethod
from typing import List
from app.data.interfaces.irepository import IRepository, T


class ILoadProfileDetailsRepository(IRepository[T]):
    @abstractmethod
    def create_details_in_bulk(self, details: List[T]) -> None:
        pass

    @abstractmethod
    def delete_by_profile_id(self, profile_id) -> int:
        pass

    @abstractmethod
    def get_load_details_by_load_id(self, load_id):
        pass
