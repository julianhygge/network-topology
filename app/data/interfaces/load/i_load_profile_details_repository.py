"""Module for the load profile details repository interface."""

from abc import abstractmethod
from typing import Any, Dict, List, Optional
from uuid import UUID

from app.data.interfaces.i_repository import IRepository, T


class ILoadProfileDetailsRepository(IRepository[T]):  # T is LoadProfileDetails
    """
    Interface for repositories managing load profile detail data.
    Extends IRepository for CRUD operations on load profile time-series data.
    """

    @abstractmethod
    def create_details_in_bulk(self, details: List[Dict[str, Any]]) -> None:
        """
        Creates multiple load profile detail records in bulk.

        Args:
            details: A list of dictionaries, where each dictionary contains
                     the data for a load profile detail record.
        """
        pass

    @abstractmethod
    def delete_by_profile_id(self, profile_id: UUID) -> int:
        """
        Deletes all load profile details associated with a given profile ID.

        Args:
            profile_id: The UUID of the load profile.

        Returns:
            The number of detail records deleted.
        """
        pass

    @abstractmethod
    def get_load_details_by_load_id(
        self, load_id: UUID
    ) -> Optional[List[Dict[str, Any]]]:
        """
        Retrieves load profile details (timestamp, consumption) by load ID.

        Args:
            load_id: The UUID of the load profile.

        Returns:
            A list of dictionaries containing 'timestamp' and
            'consumption_kwh', or None if no details are found.
        """
        pass

    # Note: The following methods (save_file, get_file) seem misplaced in this
    # interface as they are typically handled by ILoadProfileFilesRepository.
    # They are not abstract here.
    def save_file(
        self, profile_id: UUID, filename: str, content: bytes
    ) -> Any:
        """
        Saves a file associated with a load profile. (Potentially misplaced)

        Args:
            profile_id: The UUID of the load profile.
            filename: The name of the file.
            content: The binary content of the file.

        Returns:
            Implementation-defined result.
        """
        pass

    def get_file(self, file_id: UUID) -> Any:
        """
        Retrieves a file by its ID. (Potentially misplaced)

        Args:
            file_id: The UUID of the file.

        Returns:
            Implementation-defined result, likely file content or metadata.
        """
        pass
