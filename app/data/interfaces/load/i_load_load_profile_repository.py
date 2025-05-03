from abc import abstractmethod
from typing import List
from uuid import UUID

from app.data.interfaces.irepository import IRepository, T


class ILoadProfileRepository(IRepository[T]):

    @abstractmethod
    def get_public_profiles(self) -> List[T]:
        pass

    @abstractmethod
    def get_load_profiles_by_user_id(self, user_id) -> List[T]:
        pass

    @abstractmethod
    def get_load_profiles_by_user_id_and_house_id(self, user_id, house_id) -> List[T]:
        pass

    def get_or_create_by_house_id(self, user_id: UUID, house_id: UUID, load_source):
        pass

    @abstractmethod
    def get_by_house_id(self, house_id: int):
        pass
