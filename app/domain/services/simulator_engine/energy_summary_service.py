"""
Service for handling energy summaries for houses and nodes in the simulation.
"""

import datetime
from typing import Dict, List
from uuid import UUID

from app.domain.entities.house_profile import HouseProfile
from app.domain.entities.node import Node
from app.domain.interfaces.net_topology.i_net_topology_service import (
    INetTopologyService,
)
from app.domain.interfaces.simulator_engine.i_data_preparation_service import (
    IDataPreparationService,
)
from app.exceptions.hygge_exceptions import NotFoundException
from app.utils.datetime_util import (
    end_of_day,
    start_of_day,
)
from app.utils.logger import logger


class EnergySummaryService:
    """
    Service responsible for aggregating energy data for houses and nodes.
    """

    def __init__(
        self,
        net_topology_service: INetTopologyService,
        data_preparation_service: IDataPreparationService,
    ):
        """
        Initializes the EnergySummaryService.
        """
        self._net_topology_service = net_topology_service
        self._data_preparation_service = data_preparation_service

    def get_house_energy_sum_for_period(
        self,
        house_entity: Node,
        start_datetime: datetime.datetime,
        end_datetime: datetime.datetime,
    ) -> Dict[str, float]:
        """
        Aggregates total imported and exported energy for a specific house
        over a given datetime range.

        Args:
            house_entity: The Node object representing the house.
            start_datetime: The start datetime of the period (00:00).
            end_datetime: The end datetime of the period (23:59).

        Returns:
            A dict with "total_imported_units" and "total_exported_units".
            Returns {"total_imported_units": 0.0, "total_exported_units": 0.0}
            if data is not found or an error occurs.
        """
        # The year replacement is a specific business logic for this
        # simulation.
        # It's applied here as per existing logic.

        start_dt_processed = start_datetime.replace(year=2023)
        start_dt_processed = start_of_day(start_dt_processed)

        end_dt_processed = end_datetime.replace(year=2023)
        end_dt_processed = end_of_day(end_dt_processed)

        house_node_id = str(house_entity.id)
        logger.debug(
            f"Fetching 15-min interval data for house {house_node_id} "
            f"for period {start_dt_processed} to {end_dt_processed}..."
        )

        try:
            house_profile: HouseProfile | None = (
                self._data_preparation_service.get_house_profile(
                    house=house_entity
                )
            )
        except Exception as e:
            logger.error(
                f"Error getting profile for house {house_node_id}: {e}"
            )
            return {
                "total_imported_units": 0.0,
                "total_exported_units": 0.0,
            }

        if not house_profile:
            logger.error(
                f"Error getting HouseProfile for house {house_node_id}."
            )
            return {
                "total_imported_units": 0.0,
                "total_exported_units": 0.0,
            }

        total_imported_units = 0.0
        total_exported_units = 0.0

        timestamps = getattr(house_profile, "timestamps", [])
        imported_intervals = getattr(house_profile, "imported_units", [])
        exported_intervals = getattr(house_profile, "exported_units", [])

        if not (
            len(timestamps)
            == len(imported_intervals)
            == len(exported_intervals)
        ):
            logger.error(
                f"Data mismatch in lengths for house {house_node_id}."
            )
            return {
                "total_imported_units": 0.0,
                "total_exported_units": 0.0,
            }

        for i, ts_datetime_val in enumerate(timestamps):
            if start_dt_processed <= ts_datetime_val < end_dt_processed:
                total_imported_units += imported_intervals[i]
                total_exported_units += exported_intervals[i]

        return {
            "total_imported_units": round(total_imported_units, 2),
            "total_exported_units": round(total_exported_units, 2),
        }

    def get_house_energy_summary(
        self,
        house_id: UUID,
        start_datetime: datetime.datetime,
        end_datetime: datetime.datetime,
    ) -> Dict[str, float]:
        """
        Provides total imported and exported units for a specific house
        for a given datetime range.

        Args:
            house_id: The UUID of the house.
            start_datetime: The start datetime of the period.
            end_datetime: The end datetime of the period.

        Returns:
            A dictionary with "total_imported_units" and
            "total_exported_units".

        Raises:
            NotFoundException: If the house is not found.
        """
        logger.info(
            f"Getting energy summary for house {house_id} "
            f"for period {start_datetime} to {end_datetime}."
        )
        house_entity = self._net_topology_service.get_node_by_id(house_id)
        if not house_entity or house_entity.node_type != "HOUSE":
            raise NotFoundException(f"House with id {house_id} not found.")

        return self.get_house_energy_sum_for_period(
            house_entity, start_datetime, end_datetime
        )

    def get_node_energy_summary(
        self,
        node_id: UUID,
        start_datetime: datetime.datetime,
        end_datetime: datetime.datetime,
    ) -> Dict[str, float]:
        """
        Provides total imported and exported units for all houses under a
        specific node (e.g., transformer, substation, or a house itself)
        for a given datetime range.

        Args:
            node_id: The UUID of the node.
            start_datetime: The start datetime of the period.
            end_datetime: The end datetime of the period.

        Returns:
            A dictionary with "total_imported_units" and
            "total_exported_units" aggregated for all houses under the node.

        Raises:
            NotFoundException: If the node is not found.
        """
        logger.info(
            f"Getting energy summary for node {node_id} and its children "
            f"for period {start_datetime} to {end_datetime}."
        )
        node_entity = self._net_topology_service.get_node_by_id(node_id)
        if not node_entity:
            raise NotFoundException(f"Node with id {node_id} not found.")

        total_imported_for_node = 0.0
        total_exported_for_node = 0.0

        if node_entity.node_type == "HOUSE":
            summary = self.get_house_energy_sum_for_period(
                node_entity, start_datetime, end_datetime
            )
            total_imported_for_node = summary["total_imported_units"]
            total_exported_for_node = summary["total_exported_units"]
        else:
            # For transformers or substations, get all descendant houses
            houses_under_node: List[Node] = (
                self._net_topology_service.get_houses_by_parent_node_id(
                    node_id
                )
            )
            if (
                not houses_under_node
            ):  # if it's a substation, use the other method
                if node_entity.node_type == "SUBSTATION":
                    houses_under_node = (
                        self._net_topology_service.get_houses_by_substation_id(
                            node_id
                        )
                    )
                else:
                    logger.warning(
                        f"No houses found under non-house node {node_id}"
                    )

            for house_entity in houses_under_node:
                summary = self.get_house_energy_sum_for_period(
                    house_entity, start_datetime, end_datetime
                )
                total_imported_for_node += summary["total_imported_units"]
                total_exported_for_node += summary["total_exported_units"]

        return {
            "total_imported_units": round(total_imported_for_node, 2),
            "total_exported_units": round(total_exported_for_node, 2),
        }
