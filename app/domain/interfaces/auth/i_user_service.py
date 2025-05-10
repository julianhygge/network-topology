from abc import ABC, abstractmethod


class IUserService(ABC):
    @abstractmethod
    def update_user_logo(self, session_user, user_id, file_logo):
        """"""

    def get_user_logo(self, user_id):
        """"""
