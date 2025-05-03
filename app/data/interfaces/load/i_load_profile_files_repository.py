from abc import abstractmethod

from app.data.interfaces.i_repository import IRepository, T


class ILoadProfileFilesRepository(IRepository[T]):
    @abstractmethod
    def save_file(self, profile_id, filename, content):
        pass

    @abstractmethod
    def get_file(self, file_id):
        pass
