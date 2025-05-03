from abc import abstractmethod

from app.data.interfaces.irepository import IRepository, T


class ILoadGenerationEngineRepository(IRepository[T]):

    @abstractmethod
    def delete_by_profile_id(self, profile_id) -> int:
        pass
