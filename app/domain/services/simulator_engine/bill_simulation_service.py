"""
Module for simulating bills based on energy consumption and generation data.
"""

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
from app.domain.interfaces.simulator_engine.i_policy_strategy import (
    IBillingPolicyStrategy,
)
from app.domain.services.simulator_engine.billing_strategies import (
    GrossMeteringStrategy,
    SimpleNetMeteringStrategy,
    TimeOfUseRateStrategy,
)
from app.domain.services.simulator_engine.energy_summary_service import (
    EnergySummaryService,
)
from app.exceptions.hygge_exceptions import (
    NotFoundException,
    ServiceException,
)
from app.utils.datetime_util import get_billing_period_datetimes, utc_now_iso
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
        energy_summary_service: EnergySummaryService,
    ):
        """
        Initializes the BillSimulationService.
        """
        self._sim_runs_repo = simulation_runs_repository
        self._selected_policy_repository = selected_policy_repository
        self._net_metering_policy_repo = net_metering_policy_repo
        self._gross_metering_policy_repo = gross_metering_policy_repo
        self._tou_rate_policy_repo = tou_rate_policy_params_repository
        self._house_bill_service = house_bill_service
        self._net_topology_service = net_topology_service
        self._data_preparation_service = data_preparation_service
        self._energy_service = energy_summary_service

        net_metering_strategy = SimpleNetMeteringStrategy(
            net_metering_policy_repo=self._net_metering_policy_repo,
            selected_policy_repository=self._selected_policy_repository,
        )
        gross_metering_strategy = GrossMeteringStrategy(
            gross_metering_policy_repo=self._gross_metering_policy_repo,
            selected_policy_repository=self._selected_policy_repository,
        )
        tou_rate_strategy = TimeOfUseRateStrategy(
            tou_rate_policy_params_repo=self._tou_rate_policy_repo,
            selected_policy_repository=self._selected_policy_repository,
        )

        # Both code styles are accepted: the internal codes (SIMPLE_NET...)
        # and the policy_code values stored in
        # master.net_metering_policy_types (net_metering_standard...).
        self._billing_strategies: Dict[str, IBillingPolicyStrategy] = {
            "SIMPLE_NET": net_metering_strategy,
            "net_metering_standard": net_metering_strategy,
            "GROSS_METERING": gross_metering_strategy,
            "gross_metering_standard": gross_metering_strategy,
            "TOU_RATE": tou_rate_strategy,
            "tou_rate_standard": tou_rate_strategy,
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

        # Common parameters applicable to all policies
        common_params = {
            "fac_charge_per_kwh": policy_details.fac_charge_per_kwh_imported,
            "tax_rate": policy_details.tax_rate_on_energy_charges,
        }

        try:
            strategy = self._get_billing_strategy(policy_code)

            # Delegate fetching policy-specific parameters to the strategy
            # Repositories are now injected via constructor
            policy_specific_params = strategy.get_policy_config(
                simulation_run_id=simulation_run_id,
                common_params=common_params,
            )

        except Exception as e:
            logger.error(
                f"Error getting policy config from strategy {policy_code}"
                f"for run {simulation_run_id}: {e}"
            )
            return None

        return {
            "simulation_run_id": sim_run.id,
            "billing_cycle_month": sim_run.billing_cycle_month,
            "billing_cycle_year": sim_run.billing_cycle_year,
            "topology_root_node_id": sim_run.topology_root_node_id,
            "policy_type": policy_code,
            "policy_config": policy_specific_params,
        }

    def _get_sanctioned_load_kw(self, house_entity) -> float:
        """
        Resolves the sanctioned load (connection_kw) for a house.

        The topology Node entity does not carry connection_kw, so the
        value is read from the houses table; falls back to
        DEFAULT_SANCTIONED_LOAD_KW when missing.
        """
        connection_kw = getattr(house_entity, "connection_kw", None)
        if connection_kw is None:
            try:
                house_record = (
                    self._net_topology_service.house_repo.read_or_none(
                        house_entity.id
                    )
                )
                if house_record is not None:
                    connection_kw = house_record.connection_kw
            except Exception as e:
                logger.warning(
                    f"Could not read house record for "
                    f"{house_entity.id}: {e}"
                )
        if connection_kw is None:
            return self.DEFAULT_SANCTIONED_LOAD_KW
        return float(connection_kw)

    def _get_houses_in_topology(self, substation_id: UUID) -> List[Node]:
        """
        Identifies all houses belonging to the given topology root node.
        Uses NetTopologyService to get houses.

        Args:
            substation_id: The root node ID of the topology
                                   (e.g., substation ID), as a string

        Returns:
            A list of Node (House) entity objects.
        """
        logger.info(f"Fetching houses for substation_id: {substation_id}")

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
            return []
        return houses_in_substation

    def _delete_existing_bills(self, run_id: UUID) -> int:
        """
        Deletes any house bills previously generated for the run, so a
        new calculation replaces them instead of appending duplicates.
        """
        existing_bills = self._house_bill_service.repository.filter(
            simulation_run_id=run_id
        )
        for bill in existing_bills:
            self._house_bill_service.repository.delete(bill.id)
        if existing_bills:
            logger.info(
                f"Deleted {len(existing_bills)} previous house bills "
                f"for simulation run {run_id}."
            )
        return len(existing_bills)

    def reset_run_configuration(self, run_id: UUID) -> Dict[str, Any]:
        """
        Removes everything configured for a simulation run so it can be
        set up from scratch: generated house bills, the selected policy
        and its policy-specific parameters, and the chosen allocation
        algorithm.
        """
        sim_run = self._sim_runs_repo.read_or_none(run_id)
        if not sim_run:
            raise NotFoundException(
                f"Simulation run {run_id} not found."
            )

        deleted_bills = self._delete_existing_bills(run_id)

        # Per-policy parameter tables keyed by simulation_run_id
        self._net_metering_policy_repo.delete(run_id)
        self._gross_metering_policy_repo.delete(run_id)
        tou_rows = self._tou_rate_policy_repo.filter(
            simulation_run_id=run_id
        )
        for row in tou_rows:
            self._tou_rate_policy_repo.delete(row.id)
        self._selected_policy_repository.delete(run_id)

        self._sim_runs_repo.update(
            run_id,
            {
                "simulation_algorithm_type_id": None,
                "status": "PENDING",
                "simulation_start_timestamp": None,
                "simulation_end_timestamp": None,
                "modified_on": utc_now_iso(),
            },
        )
        logger.info(
            f"Simulation run {run_id} configuration reset "
            f"({deleted_bills} bills removed)."
        )
        return {"deleted_bills": deleted_bills}

    def calculate_bills_for_simulation_run(self, run_id: UUID) -> None:
        """
        Calculates bills for all houses in a given simulation run.

        Args:
            run_id: The ID of the simulation run.
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

        # Replace bills from any previous calculation of this run
        self._delete_existing_bills(run_id)

        # Placeholder for next steps (Phase 1, Steps 3, 4, 5)
        for house_entity in houses:  # house_entity is a Node (House) object
            house_node_id = str(house_entity.id)  # Get ID from the entity
            sanctioned_load_kw = self._get_sanctioned_load_kw(house_entity)
            logger.info(f"Processing house: {house_node_id}")

            # 3. Aggregate Energy Data for the Billing Cycle for Each House
            billing_month = config["billing_cycle_month"]
            billing_year = config["billing_cycle_year"]

            logger.info(
                f"  Fetching energy data for house {house_node_id} "
                f"for {billing_month}/{config['billing_cycle_year']}"
            )

            # Get raw 15-min interval data for the house
            # This data is needed by TOU strategy directly.
            # For other strategies, we'll use the aggregated summary.

            house_profile: HouseProfile | None = (
                self._data_preparation_service.get_house_profile(
                    house=house_entity
                )
            )

            house_profile_data_dict = {
                "timestamps": getattr(house_profile, "timestamps", []),
                "imported_intervals": getattr(
                    house_profile, "imported_units", []
                ),
                "exported_intervals": getattr(
                    house_profile, "exported_units", []
                ),
            }

            (
                start_of_billing_month_dt,
                end_of_billing_month_dt,
            ) = get_billing_period_datetimes(
                billing_year,
                billing_month,
            )

            e_summary = self._energy_service.get_house_energy_sum_for_period(
                house_entity,
                start_of_billing_month_dt,
                end_of_billing_month_dt,
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
                bill_details["house_name"] = house_entity.name
            except Exception as e:
                logger.error(
                    f"Error calculating bill components for house:"
                    f"{house_node_id} using {policy_type}: {e}"
                )
                continue  # Skip this house

            # 5. Store Bill Results using Strategy
            try:
                strategy.store_bill_details(
                    run_id=run_id,
                    house_node_id=house_node_id,
                    bill_details=bill_details,
                    house_bill_service=self._house_bill_service,
                )
            except Exception as e:
                logger.error(
                    f"  Error storing bill for house {house_node_id}"
                    f"via strategy {policy_type}: {e}"
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
