"""Module for Account and User repositories."""

from typing import Any, Dict, Optional

from peewee import IntegrityError

from app.data.interfaces.i_user_repository import IUserRepository
from app.data.repositories.base_repository import BaseRepository
from app.data.schemas.auth.auth_schema import UserGroupRel
from app.data.schemas.transactional.user_schema import Account, User
from app.utils.logger import logger


class AccountRepository(BaseRepository[Account]):
    """
    Repository for managing Account data.

    This class extends `BaseRepository` to provide generic CRUD operations
    for the `Account` model.
    """

    def __init__(self):
        super().__init__(model=Account)


class UserRepository(BaseRepository[User], IUserRepository[User]):
    """
    Repository for managing User data and related entities like Account and
    UserGroupRel.

    Extends `BaseRepository` for `User` model CRUD and implements
    `IUserRepository` for user-specific operations.
    """

    def __init__(self):
        super().__init__(model=User)

    model_user_group = UserGroupRel
    model_account = Account

    def fetch_user_by_phone_number(self, phone_number: str) -> Optional[User]:
        """
        Retrieves a user by their phone number.

        Args:
            phone_number: The phone number of the user to fetch.

        Returns:
            A User instance if found, otherwise None.
        """
        return self._model.get_or_none(
            self._model.phone_number == phone_number
        )

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
        return self.model_account.get_or_none(
            self.model_account.phone_number == phone_number
        )

    def insert_into_user_and_group(
        self, user_data: Dict[str, Any], data: Dict[str, Any]
    ) -> User:
        """
        Inserts a new user and associates them with a group atomically.

        Args:
            user_data: Dictionary containing data for the new user.
                       Must include an 'id' key for the user_id.
            data: Dictionary containing data for the user-group relationship.

        Returns:
            The created User instance.

        Raises:
            IntegrityError: If a database integrity constraint is violated.
        """
        try:
            with self.database_instance.atomic():
                user = self._model.create(**user_data)
                user_id = user_data["id"]  # Assumes user_data contains id
                # Pass data for UserGroupRel update directly
                self.update_user_group(user_id, data)
                return user
        except IntegrityError as e:
            logger.exception(
                "Integrity error during user and group insertion: %s", e
            )
            raise

    def create(self, query) -> User:
        """
        Creates a new user, handling logo file if provided.

        Overrides BaseRepository.create to include custom logic for
        handling a 'logo_file' path by reading the file into a 'logo'
        bytes field.

        Args:
            **query: Keyword arguments for user creation. If 'logo_file' is
                     present, its content will be read into 'logo'.

        Returns:
            The created User instance.
        """
        if "logo_file" in query and query["logo_file"]:
            logo_file_path = query.pop("logo_file")
            with open(logo_file_path, "rb") as f:
                query["logo"] = f.read()
        obj = self._model.create(**query)
        return obj

    def insert_into_account(self, data: Any) -> Account:
        """
        Inserts a new account.

        Args:
            **data: Keyword arguments containing account data.

        Returns:
            The created Account instance.
        """
        obj = self.model_account.create(**data)
        return obj

    def update_user_group(self, user_id: int, data: Dict[str, Any]) -> None:
        """
        Updates a user's group association.

        Args:
            user_id: The ID of the user whose group association is to be
                updated.
            data: Dictionary containing data for updating the
                UserGroupRel record.
        """
        UserGroupRel.update(data).where(
            UserGroupRel.user_record_id == user_id
        ).execute()
