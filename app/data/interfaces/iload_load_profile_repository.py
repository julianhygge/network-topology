from abc import abstractmethod
from typing import List
from app.data.interfaces.irepository import IRepository, T


class ILoadProfileRepository(IRepository[T]):

    @abstractmethod
    def get_public_profiles(self) -> List[T]:
        pass

    @abstractmethod
    def get_load_profiles_by_user_id(self, user_id) -> List[T]:
        pass
