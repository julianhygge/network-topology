"""Module for the load profile files repository interface."""

from abc import abstractmethod
from typing import Optional
from uuid import UUID

from app.data.interfaces.i_repository import IRepository, T


class ILoadProfileFilesRepository(IRepository[T]):  # T is LoadProfileFiles
    """
    Interface for repositories managing files associated with load profiles.
    Extends IRepository for CRUD operations on load profile file metadata
    and content.
    """

    @abstractmethod
    def save_file(self, profile_id: UUID, filename: str, content: bytes) -> T:
        """
        Saves a file associated with a load profile.

        Args:
            profile_id: The UUID of the load profile.
            filename: The name of the file.
            content: The binary content of the file.

        Returns:
            The created file record instance (T).
        """
        pass

    @abstractmethod
    def get_file(self, file_id: UUID) -> Optional[T]:
        """
        Retrieves a file record by its ID (or associated profile_id,
        depending on implementation).

        Args:
            file_id: The UUID identifier for the file or its associated
                profile.

        Returns:
            A file record instance (T) if found, otherwise None.
        """
        pass
