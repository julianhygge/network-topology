"""
Module for the authentication attempt repository interface.
"""
import datetime
from abc import abstractmethod
from typing import List

from app.data.interfaces.i_repository import IRepository, T
from app.data.schemas.auth.auth_schema import AuthAttempts


class IAuthAttemptRepository(IRepository[T]):
    """
    Interface for the authentication attempt repository.
    """

    @abstractmethod
    def fetch_all_previous_records_for_user(
        self, phone_number: str, records_after_time: datetime.datetime
    ) -> List[AuthAttempts]:
        """
        Fetches all previous OTP attempts for a user.

        Args:
            phone_number: The user's phone number.
            records_after_time: The timestamp after which to fetch records.

        Returns:
            A list of AuthAttempts objects matching the criteria.
        """
