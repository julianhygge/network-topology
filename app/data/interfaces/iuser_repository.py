"""
Module for the user repository interface.
"""
from abc import abstractmethod
from app.data.interfaces.i_repository import IRepository, T


class IUserRepository(IRepository[T]):
    """
    Interface for the user repository.
    """
    @abstractmethod
    def fetch_user_by_phone_number(self, phone_number):
        """Get the Registered User by phone number"""

    @abstractmethod
    def fetch_account_by_phone_number(self, phone_number):
        """
        Fetch account by phone number.
        """

    @abstractmethod
    def insert_into_user_and_group(self, user_data, data):
        """
        Insert into user and group.
        """

    @abstractmethod
    def insert_into_account(self, **data):
        """
        Insert into account.
        """

    @abstractmethod
    def update_user_group(self, user_id, data):
        """
        Update user group.
        """
