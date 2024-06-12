from abc import abstractmethod
from app.data.interfaces.irepository import IRepository, T


class IUserRepository(IRepository[T]):
    @abstractmethod
    def fetch_user_by_phone_number(self, phone_number):
        """Get the Registered User by phone number"""

    @abstractmethod
    def fetch_account_by_phone_number(self, phone_number):
        """"""

    @abstractmethod
    def insert_into_user_and_group(self, user_data, data):
        """"""

    @abstractmethod
    def insert_into_account(self, **data):
        """"""

    @abstractmethod
    def update_user_group(self, user_id, data):
        """"""