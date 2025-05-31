"""
Module for simulating bills based on energy consumption and generation data.
"""

from typing import Any, Dict, List
from uuid import UUID

from app.data.interfaces.i_repository import IRepository
from app.domain.entities.house_profile import (
    HouseProfile,  # For 15-min interval data
)
from app.domain.entities.node import Node
from app.domain.interfaces.i_service import IService
from app.domain.interfaces.net_topology.i_net_topology_service import (
    INetTopologyService,
)
from app.domain.interfaces.simulator_engine.i_data_preparation_service import (
    IDataPreparationService,
)
from app.utils.datetime_util import utc_now_iso
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
        self._house_bill_service = house_bill_service
        self._net_topology_service = net_topology_service
        self._data_preparation_service = data_preparation_service

    def _fetch_simulation_configuration(
        self,
        simulation_run_id: UUID,
    ) -> Dict[str, Any] | None:
        """
        Fetches the configuration for a given simulation run for Net Metering.

        Args:
            simulation_run_id: The ID of the simulation run.

        Returns:
            A dictionary containing the simulation configuration
            or None if not found or not a Net Metering policy.
        """

        sim_run = self._sim_runs_repo.read_or_none(simulation_run_id)
        if not sim_run:
            logger.warning(
                f"SimulationRun with id {simulation_run_id} not found."
            )
            return None

        policy = self._selected_policy_repository.read(simulation_run_id)

        if not policy:
            logger.warning(f"Policy for run {simulation_run_id} not found.")
            return None

        if policy.net_metering_policy_type_id.policy_code == "SIMPLE_NET":
            params = self._net_metering_policy_repo.read_or_none(
                simulation_run_id
            )

            if not params:
                logger.warning(
                    f"NetMeteringPolicy (params) with id"
                    f"{policy.net_metering_policy_type_id} not found."
                )
                return None

            return {
                "simulation_run_id": sim_run.id,
                "billing_cycle_month": sim_run.billing_cycle_month,
                "billing_cycle_year": sim_run.billing_cycle_year,
                "topology_root_node_id": sim_run.topology_root_node_id_id,
                "policy_type": "SIMPLE_NET",
                "fixed_charge_per_kw": params.fixed_charge_tariff_rate_per_kw,
                "fac_charge_per_kwh": policy.fac_charge_per_kwh_imported,
                "tax_rate": policy.tax_rate_on_energy_charges,
                "retail_price_per_kwh": params.retail_price_per_kwh,
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
            # Update simulation_runs status to 'FAILED'
            # (when CRUD is available)
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
            billing_year = config["billing_cycle_year"]

            logger.info(
                f"  Fetching 15-min interval data for house {house_node_id} "
                f"for {billing_month}/{billing_year}..."
            )

            try:
                house_profile: HouseProfile | None = (
                    self._data_preparation_service.get_house_profile(
                        house=house_entity
                    )  # Pass the House entity
                )
            except Exception as e:
                logger.error(
                    f"  Error getting profile for house {house_node_id}: {e}"
                )
                # TODO: Log this error and decide if to continue
                # or fail the run
                continue

            if not house_profile:
                logger.error(
                    f"  Error getting HouseProfile for house {house_node_id}."
                )
                # TODO: Decide how to handle this error for the specific house.
                # Maybe log and continue to the next house
                # or mark this house's bill as failed.
                continue

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
                    f"  Error: Mismatch in lengths for house {house_node_id}."
                )
                continue

            # here I need to add the year when Shashwat responds
            for i, ts in enumerate(timestamps):
                if ts.month == billing_month:
                    total_imported_units += imported_intervals[i]
                    total_exported_units += exported_intervals[i]

            logger.info(
                f"  Aggregated for {billing_month}/{billing_year} - "
                f"Total Imported: {total_imported_units:.2f} kWh, "
                f"Total Exported: {total_exported_units:.2f} kWh"
            )

            # 4. Calculate Bill Components (logic will depend on policy_type)
            # 4. Calculate Bill Components for "Simple Net Metering"
            bill_details: Dict[str, Any] = {}

            if config.get("policy_type") == "SIMPLE_NET":
                logger.info(f"  Calculating bill for house {house_node_id}...")

                net_usage_kwh = total_imported_units - total_exported_units
                retail_rate = config["retail_price_per_kwh"]

                energy_charges = 0.0
                if net_usage_kwh > 0:
                    energy_charges = net_usage_kwh * retail_rate

                # Credit_Amount_calc is pending for future iteration.
                # credit_amount_calc = 0.0
                # if net_usage_kwh < 0:
                # credit_amount_calc = abs(net_usage_kwh) * retail_rate

                fixed_charges = (
                    config["fixed_charge_per_kw"] * sanctioned_load_kw
                )
                fac_charges = (
                    total_imported_units * config["fac_charge_per_kwh"]
                )

                tax_amount = 0.0
                if energy_charges > 0:
                    tax_amount = energy_charges * config["tax_rate"]

                arrears = 0.0  # Assume 0 for now for this phase

                total_bill_amount = (
                    energy_charges
                    + fixed_charges
                    + fac_charges
                    + tax_amount
                    - arrears
                )
                # Initial implementation does not subtract Credit_Amount_calc

                bill_details = {
                    "house_node_id": house_node_id,
                    "billing_cycle_month": billing_month,
                    "billing_cycle_year": billing_year,
                    "policy_type": "SIMPLE_NET",
                    "total_imported_kwh": round(total_imported_units, 2),
                    "total_exported_kwh": round(total_exported_units, 2),
                    "net_usage_kwh": round(net_usage_kwh, 2),
                    "retail_rate_per_kwh": retail_rate,
                    "energy_charges": round(energy_charges, 2),
                    # "credit_amount_calculated": round(credit_amount_calc, 2),
                    "fixed_charge_per_kw": config["fixed_charge_per_kw"],
                    "sanctioned_load_kw": sanctioned_load_kw,
                    "fixed_charges": round(fixed_charges, 2),
                    "fac_charge_per_kwh": config["fac_charge_per_kwh"],
                    "fac_charges": round(fac_charges, 2),
                    "tax_rate": config["tax_rate"],
                    "tax_amount_on_energy": round(tax_amount, 2),
                    "arrears": round(arrears, 2),
                    "total_bill_amount_calculated": round(
                        total_bill_amount, 2
                    ),
                }
                logger.info(f"  Calculated Bill Details: {bill_details}")

            else:
                logger.warning(
                    f"  Policy {config.get('policy_type')} not yet supported "
                    f"for house {house_node_id}."
                )
                continue  # or handle error

            try:
                house_bill_record = {
                    "simulation_run_id": run_id,
                    "house_node_id": house_node_id,
                    "total_energy_imported_kwh": bill_details[
                        "total_imported_kwh"
                    ],
                    "total_energy_exported_kwh": bill_details[
                        "total_exported_kwh"
                    ],
                    "net_energy_balance_kwh": bill_details["net_usage_kwh"],
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


"""
TODO:
- Implement detailed bill calculation logic for "Simple Net Metering"
  (Phase 1, Step 4).
- Implement logic to store bill results (Phase 1, Step 5).
- Implement logic to update simulation_runs status (Phase 1, Step 6).
- Add comprehensive error handling and logging.
- Add unit tests.
"""
