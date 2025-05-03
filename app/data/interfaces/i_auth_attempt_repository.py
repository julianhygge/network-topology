"""
Module for the authentication attempt repository interface.
"""
from abc import abstractmethod

from app.data.interfaces.i_repository import IRepository, T


class IAuthAttemptRepository(IRepository[T]):
    """
    Interface for the authentication attempt repository.
    """
    @abstractmethod
    def fetch_all_previous_records_for_user(self, phone_number, records_after_time):
        """ Fetch all Previous otp attempts"""

