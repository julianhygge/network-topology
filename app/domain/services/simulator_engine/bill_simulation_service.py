"""
Module for simulating bills based on energy consumption and generation data.
"""

import datetime
from typing import Any, Dict, List
from uuid import UUID

from app.data.interfaces.i_repository import IRepository
from app.domain.entities.house_profile import HouseProfile
from app.domain.entities.node import Node
from app.domain.interfaces.i_service import IService
from app.domain.interfaces.net_topology.i_net_topology_service import (
    INetTopologyService,
)
from app.domain.interfaces.simulator_engine.i_data_preparation_service import (
    IDataPreparationService,
)
from app.domain.services.simulator_engine.billing_strategies import (
    GrossMeteringStrategy,
    IBillingPolicyStrategy,
    SimpleNetMeteringStrategy,
    TimeOfUseRateStrategy,
)
from app.exceptions.hygge_exceptions import (
    NotFoundException,
    ServiceException,
)
from app.utils.datetime_util import (
    end_of_day,
    end_of_month,
    start_of_day,
    start_of_month,
    utc_now_iso,
)
from app.utils.logger import logger


class BillSimulationService:
    """
    Service responsible for calculating bills for a given simulation run.
    """

    # Hardcoded value as per requirement
    DEFAULT_SANCTIONED_LOAD_KW: float = 5.0

    def __init__(
        self,
        simulation_runs_repository: IRepository,
        selected_policy_repository: IRepository,
        net_metering_policy_repo: IRepository,
        gross_metering_policy_repo: IRepository,
        tou_rate_policy_params_repository: IRepository,
        house_bill_service: IService,
        net_topology_service: INetTopologyService,
        data_preparation_service: IDataPreparationService,
    ):
        """
        Initializes the BillSimulationService.
        """
        self._sim_runs_repo = simulation_runs_repository
        self._selected_policy_repository = selected_policy_repository
        self._net_metering_policy_repo = net_metering_policy_repo
        self._gross_metering_policy_repo = gross_metering_policy_repo
        self._tou_rate_policy_params_repo = tou_rate_policy_params_repository
        self._house_bill_service = house_bill_service
        self._net_topology_service = net_topology_service
        self._data_preparation_service = data_preparation_service

        self._billing_strategies: Dict[str, IBillingPolicyStrategy] = {
            "SIMPLE_NET": SimpleNetMeteringStrategy(),
            "GROSS_METERING": GrossMeteringStrategy(),
            "TOU_RATE": TimeOfUseRateStrategy(),
        }

    def _get_billing_strategy(
        self, policy_code: str
    ) -> IBillingPolicyStrategy:
        """
        Retrieves the billing strategy for the given policy code.
        """
        strategy = self._billing_strategies.get(policy_code)
        if not strategy:
            logger.error(f"Unsupported billing policy code: {policy_code}")
            raise ServiceException(
                f"Unsupported billing policy code: {policy_code}"
            )
        return strategy

    def _fetch_simulation_configuration(
        self,
        simulation_run_id: UUID,
    ) -> Dict[str, Any] | None:
        """
        Fetches the configuration for a given simulation run.

        Args:
            simulation_run_id: The ID of the simulation run.

        Returns:
            A dictionary containing the simulation configuration,
            including policy-specific parameters, or None if data is missing.
        """
        sim_run = self._sim_runs_repo.read_or_none(simulation_run_id)
        if not sim_run:
            logger.warning(
                f"SimulationRun with id {simulation_run_id} not found."
            )
            return None

        policy_details = self._selected_policy_repository.read(
            simulation_run_id
        )
        if not policy_details:
            logger.warning(
                f"SelectedPolicy for run {simulation_run_id} not found."
            )
            return None

        policy_code = policy_details.net_metering_policy_type_id.policy_code
        policy_specific_params = {}

        if policy_code == "SIMPLE_NET":
            params = self._net_metering_policy_repo.read_or_none(
                simulation_run_id
            )
            if not params:
                logger.warning(
                    f"NetMeteringPolicy for run {simulation_run_id} not found."
                )
                return None
            policy_specific_params = {
                "fixed_charge_per_kw": params.fixed_charge_tariff_rate_per_kw,
                "retail_price_per_kwh": params.retail_price_per_kwh,
            }
        elif policy_code == "GROSS_METERING":
            params = self._gross_metering_policy_repo.read_or_none(
                simulation_run_id
            )
            if not params:
                logger.warning(
                    f"GrossMeteringPolicy for run {simulation_run_id} not found."
                )
                return None
            policy_specific_params = {
                "import_retail_price_kwh": params.import_retail_price_per_kwh,
                "exp_whole_price_kwh": params.export_wholesale_price_per_kwh,
                "fixed_charge_per_kw": params.fixed_charge_tariff_rate_per_kw,
            }
        elif policy_code == "TOU_RATE":
            tou_params_list = self._tou_rate_policy_params_repo.filter(
                simulation_run_id=simulation_run_id
            )
            if not tou_params_list:
                logger.warning(
                    f"TimeOfUseRatePolicy for {simulation_run_id} not found."
                )
                return None
            policy_specific_params["tou_periods"] = [
                {
                    "id": str(
                        p.id
                    ),  # Keep for potential future use or detailed logging
                    "time_period_label": p.time_period_label,
                    "start_time": p.start_time,  # Keep as datetime.time
                    "end_time": p.end_time,  # Keep as datetime.time
                    "import_retail_rate_per_kwh": p.import_retail_rate_per_kwh,
                    "exp_whole_rate_per_kwh": p.export_wholesale_rate_per_kwh,
                }
                for p in tou_params_list
            ]
            # fixed_charge_per_kw for TOU
            # might be part of selected_policy_details or a default
            # For now, assuming it might be missing
            # or needs a default if not in specific TOU params.
            # The strategy will handle if it's None.
            policy_specific_params["fixed_charge_per_kw"] = getattr(
                policy_details, "fixed_charge_tariff_rate_per_kw", 0.0
            )

        # Common parameters applicable to all policies
        common_params = {
            "fac_charge_per_kwh": policy_details.fac_charge_per_kwh_imported,
            "tax_rate": policy_details.tax_rate_on_energy_charges,
        }
        policy_specific_params.update(common_params)

        return {
            "simulation_run_id": sim_run.id,
            "billing_cycle_month": sim_run.billing_cycle_month,
            "billing_cycle_year": sim_run.billing_cycle_year,
            "topology_root_node_id": sim_run.topology_root_node_id_id,
            "policy_type": policy_code,
            "policy_config": policy_specific_params,
        }

    def _get_houses_in_topology(self, substation_id: UUID) -> List[Node]:
        """
        Identifies all houses belonging to the given topology root node.
        Uses NetTopologyService to get houses.

        Args:
            topology_root_node_id: The root node ID of the topology
                                   (e.g., substation ID), as a string

        Returns:
            A list of Node (House) entity objects.
        """
        logger.info(
            f"Fetching houses for topology_root_node_id: {substation_id}"
        )

        try:
            houses_in_substation: List[Node] = (
                self._net_topology_service.get_houses_by_substation_id(
                    substation_id=substation_id
                )
            )
        except Exception as e:
            logger.error(
                f"Error fetching houses for substation_id {substation_id}: {e}"
            )
            return []

        if not houses_in_substation:
            logger.warning(
                f"No houses found for substation_id: {substation_id}"
            )
            return []

        logger.info(
            f"Found {len(houses_in_substation)}"
            f"houses for substation {substation_id}"
        )
        return houses_in_substation

    def calculate_bills_for_simulation_run(self, run_id: UUID) -> None:
        """
        Calculates bills for all houses in a given simulation run.

        Args:
            simulation_run_id: The ID of the simulation run.
        """
        logger.info(
            f"Starting bill calculation for simulation_run_id: {run_id}"
        )

        # 1. Fetch Simulation Configuration
        config = self._fetch_simulation_configuration(run_id)
        logger.info(f"Configuration fetched: {config}")

        if not config:
            logger.error(
                f"Error fetching configuration for simulation run {run_id}."
            )
            return

        topology_root_node_id = config.get("topology_root_node_id")
        if not topology_root_node_id:
            logger.error(
                "Error: topology_root_node_id not found in configuration."
            )
            return

        # 2. Iterate Through Houses in the Topology
        houses = self._get_houses_in_topology(topology_root_node_id)
        logger.info(f"Houses found in topology: {houses}")

        if not houses:
            logger.warning(
                f"No houses found for topology root {topology_root_node_id}."
            )
            # Potentially update simulation_runs status
            return

        # Placeholder for next steps (Phase 1, Steps 3, 4, 5)
        for house_entity in houses:  # house_entity is a Node (House) object
            house_node_id = str(house_entity.id)  # Get ID from the entity
            sanctioned_load_kw = getattr(
                house_entity, "connection_kw", self.DEFAULT_SANCTIONED_LOAD_KW
            )
            logger.info(f"Processing house: {house_node_id}")

            # 3. Aggregate Energy Data for the Billing Cycle for Each House
            billing_month = config["billing_cycle_month"]
            billing_year = config[
                "billing_cycle_year"
            ]  # This will be used for record keeping

            logger.info(
                f"  Fetching energy data for house {house_node_id} "
                f"for {billing_month}/{config['billing_cycle_year']}"
            )

            # Get raw 15-min interval data for the house
            # This data is needed by TOU strategy directly.
            # For other strategies, we'll use the aggregated summary.
            try:
                house_profile: HouseProfile | None = (
                    self._data_preparation_service.get_house_profile(
                        house=house_entity
                    )
                )
            except Exception as e:
                logger.error(
                    f"  Error getting profile for house {house_node_id}: {e}"
                )
                continue  # Skip this house

            if not house_profile:
                logger.error(
                    f"  Error getting HouseProfile for house {house_node_id}."
                )
                continue  # Skip this house

            house_profile_data_dict = {
                "timestamps": getattr(house_profile, "timestamps", []),
                "imported_intervals": getattr(
                    house_profile, "imported_units", []
                ),
                "exported_intervals": getattr(
                    house_profile, "exported_units", []
                ),
            }

            # Get aggregated energy summary for the billing period
            # This uses the hardcoded year 2023 as per existing logic
            try:
                (
                    start_of_billing_month_dt,
                    end_of_billing_month_dt,
                ) = self._get_billing_period_datetimes(
                    billing_year,
                    billing_month,
                )
            except ValueError as ve:
                logger.error(
                    f"Invalid billing_month/billing_year:"
                    f"{billing_month}/{billing_year}. Error: {ve}"
                )
                continue

            e_summary = self._get_house_energy_summary_for_period(
                house_entity,
                start_of_billing_month_dt,  # Based on actual billing_year
                end_of_billing_month_dt,  # Based on actual billing_year
            )
            logger.info(
                f"Aggregated for {billing_month}/{billing_year}"
                f"Total Imported: {e_summary['total_imported_units']:.2f} kWh"
                f"Total Exported: {e_summary['total_exported_units']:.2f} kWh"
            )

            # 4. Select and Use Billing Strategy
            policy_type = config["policy_type"]
            policy_specific_config = config["policy_config"]

            try:
                strategy = self._get_billing_strategy(policy_type)
                bill_details = strategy.calculate_bill_components(
                    policy_config=policy_specific_config,
                    energy_summary=e_summary,  # For non-TOU strategies
                    sanctioned_load_kw=sanctioned_load_kw,
                    house_node_id=house_node_id,
                    billing_month=billing_month,
                    billing_year=billing_year,
                    house_profile_data=house_profile_data_dict,
                )
            except Exception as e:
                logger.error(
                    f"Error calculating bill components for house:"
                    f"{house_node_id} using {policy_type}: {e}"
                )
                continue  # Skip this house

            if (
                not bill_details
                or "total_bill_amount_calculated" not in bill_details
            ):
                logger.error(
                    f"Bill calculation error for house {house_node_id}."
                )
                continue

            # 5. Store Bill Results
            try:
                actual_total_imported: float = 0.0
                actual_total_exported: float = 0.0

                if policy_type == "TOU_RATE":
                    actual_total_imported = bill_details.get(
                        "overall_total_imported_kwh", 0.0
                    )
                    actual_total_exported = bill_details.get(
                        "overall_total_exported_kwh", 0.0
                    )
                else:  # For SIMPLE_NET and GROSS_METERING
                    actual_total_imported = bill_details.get(
                        "total_imported_kwh", 0.0
                    )
                    actual_total_exported = bill_details.get(
                        "total_exported_kwh", 0.0
                    )

                actual_total_imported = (
                    float(actual_total_imported)
                    if actual_total_imported is not None
                    else 0.0
                )
                actual_total_exported = (
                    float(actual_total_exported)
                    if actual_total_exported is not None
                    else 0.0
                )

                net_balance_kwh_val = round(
                    actual_total_imported - actual_total_exported, 2
                )

                house_bill_record = {
                    "simulation_run_id": run_id,
                    "house_node_id": house_node_id,
                    "total_energy_imported_kwh": actual_total_imported,
                    "total_energy_exported_kwh": actual_total_exported,
                    "net_energy_balance_kwh": net_balance_kwh_val,
                    "calculated_bill_amount": bill_details[
                        "total_bill_amount_calculated"
                    ],
                    "bill_details": bill_details,
                }
                self._house_bill_service.create(
                    user_id=None, **house_bill_record
                )
                logger.info(
                    f"  Successfully stored bill for house {house_node_id}."
                )
            except Exception as e:
                logger.error(
                    f"  Error storing bill for house {house_node_id}: {e}"
                )

        # 6. Update simulation_runs Status
        #    - Set status to 'COMPLETED' (or 'FAILED').

        final_status = "COMPLETED"  # Assume success unless errors occurred

        # TODO: Implement more robust error tracking throughout the process.
        # If any house bill failed to store, or critical data was missing,
        # the status might be 'PARTIALLY_COMPLETED' or 'FAILED'.

        try:
            data_to_update = {
                "status": final_status,
                "simulation_end_timestamp": utc_now_iso(),
                "modified_on": utc_now_iso(),
            }
            self._sim_runs_repo.update(run_id, data_to_update)
            logger.info(
                f"Simulation run {run_id} status updated to {final_status}."
            )

        except Exception as e:
            logger.error(
                f"Error updating status for simulation run {run_id}: {e}"
            )

        logger.info(
            f"Bill calculation finished for simulation_run_id: {run_id}."
        )

    def _get_billing_period_datetimes(
        self, billing_year: int, billing_month: int
    ) -> tuple[datetime.datetime, datetime.datetime]:
        """
        Calculates the start and end datetimes
        for a given billing month and year.
        Start datetime will be the first day of the month at 00:00:00.
        End datetime will be the last day of the month at 23:59:59.

        Args:
            billing_year: The year of the billing cycle.
            billing_month: The month of the billing cycle.

        Returns:
            A tuple containing the start and end datetime objects (UTC aware).

        Raises:
            ValueError: If the billing_month or billing_year is invalid.
        """
        if not 1 <= billing_month <= 12:
            raise ValueError("Billing month must be between 1 and 12.")
        base_date = datetime.datetime(billing_year, billing_month, 1)

        start_dt = start_of_month(base_date)
        end_dt = end_of_month(base_date)
        return start_dt, end_dt

    def _get_house_energy_summary_for_period(
        self,
        house_entity: Node,
        start_datetime: datetime.datetime,  # Expected to be UTC aware
        end_datetime: datetime.datetime,  # Expected to be UTC aware
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

        timestamps = getattr(
            house_profile, "timestamps", []
        )  # List[datetime.datetime]
        imported_intervals = getattr(
            house_profile, "imported_units", []
        )  # List[float]
        exported_intervals = getattr(
            house_profile, "exported_units", []
        )  # List[float]

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
            # Ensure the timestamp from data is UTC aware for comparison
            if (
                ts_datetime_val.tzinfo is None
                or ts_datetime_val.tzinfo.utcoffset(ts_datetime_val) is None
            ):
                ts_datetime_val = ts_datetime_val.replace(
                    tzinfo=datetime.timezone.utc
                )
            else:
                ts_datetime_val = ts_datetime_val.astimezone(
                    datetime.timezone.utc
                )

            if start_dt_processed <= ts_datetime_val < end_dt_processed:
                total_imported_units += imported_intervals[i]
                total_exported_units += exported_intervals[i]

        logger.debug(
            f"Aggregated for period {start_dt_processed} to {end_dt_processed}"
            f"for house {house_node_id} - "
            f"Total Imported: {total_imported_units:.2f} kWh, "
            f"Total Exported: {total_exported_units:.2f} kWh"
        )
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

        return self._get_house_energy_summary_for_period(
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
            summary = self._get_house_energy_summary_for_period(
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
                summary = self._get_house_energy_summary_for_period(
                    house_entity, start_datetime, end_datetime
                )
                total_imported_for_node += summary["total_imported_units"]
                total_exported_for_node += summary["total_exported_units"]

        return {
            "total_imported_units": round(total_imported_for_node, 2),
            "total_exported_units": round(total_exported_for_node, 2),
        }


"""
TODO:
- Implement detailed bill calculation logic for "Simple Net Metering"
  (Phase 1, Step 4).
- Implement logic to store bill results (Phase 1, Step 5).
- Implement logic to update simulation_runs status (Phase 1, Step 6).
- Add error handling and logging.
- Add unit tests.

"""
