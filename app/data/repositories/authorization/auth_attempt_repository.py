"""Module for the AuthAttemptRepository."""
import datetime
from typing import List

from peewee import OperationalError

from app.data.interfaces.i_auth_attempt_repository import \
    IAuthAttemptRepository
from app.data.repositories.base_repository import BaseRepository
from app.data.schemas.auth.auth_schema import AuthAttempts
from app.exceptions.hygge_exceptions import DatabaseException


class AuthAttemptRepository(
    BaseRepository[AuthAttempts], IAuthAttemptRepository[AuthAttempts]
):
    """
    Repository for managing authentication attempt data.

    This class extends `BaseRepository` to provide generic CRUD operations
    for the `AuthAttempts` model and implements
    `IAuthAttemptRepository[AuthAttempts]` for specific authentication
    attempt-related queries.
    """
    def fetch_all_previous_records_for_user(
        self, phone_number: str, records_after_time: datetime.datetime
    ) -> List[AuthAttempts]:
        """
        Fetches all previous OTP attempts for a user, filtered by phone number
        and modified time.

        Args:
            phone_number: The user's phone number.
            records_after_time: The timestamp after which to fetch records.

        Returns:
            A list of AuthAttempts objects matching the criteria.

        Raises:
            DatabaseException: If a database error occurs.
        """

        try:
            return (
                self.model.select()
                .where(
                    (self.model.phone_number == phone_number)
                    & (self.model.modified_on > records_after_time)
                )
                .order_by(self.model.modified_on.desc())
            )
        except OperationalError as e:
            raise DatabaseException(str(e)) from e
