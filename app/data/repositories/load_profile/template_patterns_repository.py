"""Repository for managing template consumption patterns in the database."""

from datetime import time
from typing import Any, Dict, List, Optional, Union

from app.data.interfaces.load.i_template_load_patterns_repository import (
    ITemplateConsumptionPatternsRepository,
)
from app.data.repositories.base_repository import BaseRepository
from app.data.schemas.load_profile.load_profile_schema import (
    TemplateConsumptionPatterns,
)
from app.exceptions.hygge_exceptions import DatabaseException, ValidationError
from app.utils.logger import logger


class TemplateConsumptionPatternsRepository(
    BaseRepository[TemplateConsumptionPatterns],
    ITemplateConsumptionPatternsRepository,
):
    """
    Repository for managing template consumption patterns in the database.

    This repository provides methods to create, retrieve, update, and delete
    template consumption patterns, which represent 15-minute interval
    consumption data for predefined templates.
    """

    def __init__(self):
        """Initialize the repository with the database session."""
        super().__init__(TemplateConsumptionPatterns)

    def create_patterns_in_bulk(
        self, patterns: List[Dict[str, Any]]
    ) -> List[Dict[str, Any]]:
        """
        Creates multiple consumption patterns in bulk.

        Args:
            patterns: A list of dictionaries containing pattern data with keys:
                     - template_id: ID of the template
                     - timestamp: Timestamp of the consumption data point
                     - consumption_kwh: Energy consumption in kWh

        Returns:
            A list of created pattern dictionaries.

        Raises:
            ValidationError: If input data is invalid.
            DatabaseError: If there's an error during database operations.
        """
        if not patterns:
            logger.debug(
                "No patterns provided for bulk creation, returning empty list"
            )
            return []

        try:
            # Validate input data
            for idx, pattern in enumerate(patterns):
                if not all(
                    key in pattern
                    for key in ["template_id", "timestamp", "consumption_kwh"]
                ):
                    raise ValidationError(
                        f"Pattern at index {idx} is missing required fields. "
                        "Required fields: template_id, timestamp, "
                        "consumption_kwh"
                    )

                if (
                    not isinstance(pattern["template_id"], int)
                    or pattern["template_id"] <= 0
                ):
                    raise ValidationError(
                        f"Invalid template_id at index {idx}. "
                        "Must be a positive integer."
                    )

                if (
                    not isinstance(pattern["consumption_kwh"], (int, float))
                    or pattern["consumption_kwh"] < 0
                ):
                    raise ValidationError(
                        f"Invalid consumption_kwh at index {idx}. Must"
                        "be a non-negative number."
                    )

            # Prepare data for bulk insert
            data = [
                {
                    "template_id": p["template_id"],
                    "timestamp": p["timestamp"],
                    "consumption_kwh": float(
                        p["consumption_kwh"]
                    ),  # Ensure float type
                }
                for p in patterns
            ]

            logger.debug(
                f"Creating {len(data)} template consumption patterns in bulk"
            )

            # Perform bulk insert with transaction
            with self.database_instance.atomic():
                query = self._model.insert_many(data).returning(self._model)
                created = list(query.dicts())

            logger.info(
                f"Successfully created {len(created)}"
                f" template consumption patterns"
            )
            return created

        except Exception as e:
            logger.error(
                f"Error creating template consumption patterns "
                f"in bulk: {str(e)}"
            )
            raise DatabaseException(
                f"Failed to create template consumption patterns: {str(e)}"
            ) from e

    def delete_by_template_id(self, template_id: int) -> int:
        """
        Deletes all consumption patterns associated with a given template ID.

        Args:
            template_id: The ID of the predefined template.

        Returns:
            The number of pattern records deleted.
        """
        query = self._model.delete().where(
            self._model.template_id == template_id
        )
        return query.execute()

    def get_patterns_by_template_id(
        self, template_id: int, as_dict: bool = True
    ) -> Optional[
        Union[List[Dict[str, Any]], List[TemplateConsumptionPatterns]]
    ]:
        """
        Retrieves consumption patterns by template ID.

        Args:
            template_id: The ID of the predefined template.
            as_dict: If True, returns a list of dictionaries. If False,
            returns model instances.

        Returns:
            A list of pattern dictionaries
            (with 'timestamp' and 'consumption_kwh')
            or model instances, or None if no patterns are found.

        Raises:
            ValidationError: If template_id is invalid.
            DatabaseError: If there's an error during database operations.
        """
        if not isinstance(template_id, int) or template_id <= 0:
            raise ValidationError("template_id must be a positive integer")

        try:
            logger.debug(
                f"Retrieving consumption patterns"
                f"for template_id: {template_id}"
            )

            query = (
                self._model.select()
                .where(self._model.template_id == template_id)
                .order_by(self._model.timestamp.asc())
            )

            if not as_dict:
                return list(query)

            patterns = list(query.dicts())

            if not patterns:
                logger.debug(
                    f"No patterns found for template_id: {template_id}"
                )
                return None

            logger.debug(
                f"Retrieved {len(patterns)} patterns "
                f"for template_id: {template_id}"
            )
            return patterns

        except Exception as e:
            logger.error(
                f"Error retrieving patterns "
                f"for template_id {template_id}: {str(e)}",
                exc_info=True,
            )
            raise DatabaseException(
                f"Failed to retrieve patterns "
                f"for template_id {template_id}: {str(e)}"
            ) from e

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
            start_time: Start time of the range.
            end_time: End time of the range.
            as_dict: If True, returns a list of dictionaries.
            If False, returns model instances.

        Returns:
            A list of pattern dictionaries or model instances,
            or None if no patterns are found.

        Raises:
            ValidationError: If input parameters are invalid.
            DatabaseError: If there's an error during database operations.
        """
        if not isinstance(template_id, int) or template_id <= 0:
            raise ValidationError("template_id must be a positive integer")

        if not isinstance(start_time, time) or not isinstance(end_time, time):
            raise ValidationError(
                "start_time and end_time must be datetime.time objects"
            )

        try:
            logger.debug(
                f"Retrieving patterns for template_id {template_id} "
                f"between {start_time} and {end_time}"
            )

            # Create a base query
            query = (
                self._model.select()
                .where(
                    (self._model.template_id == template_id)
                    & (self._model.timestamp.cast("time") >= start_time)
                    & (self._model.timestamp.cast("time") <= end_time)
                )
                .order_by(self._model.timestamp.asc())
            )

            if not as_dict:
                return list(query)

            patterns = list(query.dicts())

            if not patterns:
                logger.debug(
                    f"No patterns found for template_id {template_id} "
                    f"between {start_time} and {end_time}"
                )
                return None

            logger.debug(
                f"Retrieved {len(patterns)} patterns "
                f"for template_id {template_id} "
                f"between {start_time} and {end_time}"
            )
            return patterns

        except Exception as e:
            logger.error(
                f"Error retrieving patterns for template_id {template_id} "
                f"between {start_time} and {end_time}: {str(e)}",
                exc_info=True,
            )
            raise DatabaseException(
                f"Failed to retrieve patterns for time range: {str(e)}"
            ) from e
