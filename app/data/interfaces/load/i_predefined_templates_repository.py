from abc import abstractmethod
from app.data.interfaces.i_repository import IRepository, T


class IPredefinedTemplatesRepository(IRepository[T]):
    @abstractmethod
    def get_by_profile_id(self, profile_id):
        pass

    @abstractmethod
    def create_or_update(self, profile_id, template_id):
        pass
