"""Module for the template consumption patterns repository interface."""

from abc import abstractmethod
from datetime import time
from typing import Any, Dict, List, Optional, Union

from app.data.interfaces.i_repository import IRepository, T
from app.data.schemas.load_profile.load_profile_schema import (
    TemplateConsumptionPatterns,
)


class ITemplateConsumptionPatternsRepository(IRepository[T]):
    """
    Interface for repositories managing template consumption pattern data.

    This interface defines the contract for repositories that handle operations
    related to template-based consumption patterns,
    which store 15-minute interval
    consumption data for predefined templates.
    """

    @abstractmethod
    def create_patterns_in_bulk(
        self, patterns: List[Dict[str, Any]]
    ) -> List[Dict[str, Any]]:
        """
        Creates multiple template consumption pattern records in bulk.

        Args:
            patterns: A list of dictionaries containing pattern data with keys:
                     - template_id: ID of the template (int)
                     - timestamp: Timestamp of the consumption (datetime)
                     - consumption_kwh: Energy consumption in kWh (float)

        Returns:
            A list of dictionaries representing the created pattern records.

        Raises:
            ValidationError: If input data is invalid.
            DatabaseError: If there's an error during database operations.
        """

    @abstractmethod
    def delete_by_template_id(self, template_id: int) -> int:
        """
        Deletes all consumption patterns associated with a given template ID.

        Args:
            template_id: The ID of the predefined template
            (must be a positive integer).

        Returns:
            int: The number of pattern records deleted.

        Raises:
            ValidationError: If template_id is invalid.
            DatabaseError: If there's an error during database operations.
        """

    @abstractmethod
    def get_patterns_by_template_id(
        self, template_id: int, as_dict: bool = True
    ) -> Optional[
        Union[List[Dict[str, Any]], List[TemplateConsumptionPatterns]]
    ]:
        """
        Retrieves consumption patterns by template ID.

        Args:
            template_id: The ID of the predefined template.
            as_dict: If True, returns a list of dictionaries.
            If False, returns model instances.

        Returns:
            A list of pattern dictionaries
            (with 'timestamp' and 'consumption_kwh')
            or model instances, or None if no patterns are found.

        Raises:
            ValidationError: If template_id is invalid.
            DatabaseError: If there's an error during database operations.
        """

    @abstractmethod
    def get_patterns_for_time_range(
        self,
        template_id: int,
        start_time: time,
        end_time: time,
        as_dict: bool = True,
    ) -> Optional[
        Union[List[Dict[str, Any]], List[TemplateConsumptionPatterns]]
    ]:
        """
        Retrieves consumption patterns for a specific time range within a day.

        Args:
            template_id: The ID of the predefined template.
            start_time: Start time of the range (datetime.time).
            end_time: End time of the range (datetime.time).
            as_dict: If True, returns a list of dictionaries.
            If False, returns model instances.

        Returns:
            A list of pattern dictionaries or model instances,
            or None if no patterns are found.
            Each dictionary contains 'timestamp' and 'consumption_kwh'.

        Raises:
            ValidationError: If input parameters are invalid.
            DatabaseError: If there's an error during database operations.
        """
