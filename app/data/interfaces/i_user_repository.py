"""Module for the user repository interface."""

from abc import abstractmethod
from typing import Any, Dict, Optional

from app.data.interfaces.i_repository import IRepository, T
from app.data.schemas.transactional.user_schema import Account


class IUserRepository(IRepository[T]):  # T is typically User schema
    """
    Interface for the user repository, extending generic repository operations.
    """

    @abstractmethod
    def fetch_user_by_phone_number(self, phone_number: str) -> Optional[T]:
        """
        Retrieves a user by their phone number.

        Args:
            phone_number: The phone number of the user to fetch.

        Returns:
            An instance of the user model (T) if found, otherwise None.
        """

    @abstractmethod
    def fetch_account_by_phone_number(
        self, phone_number: str
    ) -> Optional[Account]:
        """
        Retrieves an account by its associated phone number.

        Args:
            phone_number: The phone number linked to the account.

        Returns:
            An Account instance if found, otherwise None.
        """

    @abstractmethod
    def insert_into_user_and_group(
        self, user_data: Dict[str, Any], data: Dict[str, Any]
    ) -> T:
        """
        Inserts a new user and associates them with a group atomically.

        Args:
            user_data: Dictionary containing data for the new user.
            data: Dictionary containing data for the user-group relationship.

        Returns:
            An instance of the created user model (T).
        """

    @abstractmethod
    def insert_into_account(self, **data: Any) -> Account:
        """
        Inserts a new account.

        Args:
            **data: Keyword arguments containing account data.

        Returns:
            The created Account instance.
        """

    @abstractmethod
    def update_user_group(self, user_id: int, data: Dict[str, Any]) -> None:
        """
        Updates a user's group association.

        Args:
            user_id: The ID of the user whose group association is to be
                updated.
            data: Dictionary containing data for updating the user-group link.
        """
