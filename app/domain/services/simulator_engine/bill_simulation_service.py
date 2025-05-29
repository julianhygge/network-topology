"""
Module for simulating bills based on energy consumption and generation data.
"""

import uuid
from datetime import datetime  # Keep this for simulation_end_timestamp
from typing import Any, Dict, List

from app.data.schemas.master.master_schema import NetMeteringAlgorithm
from app.data.schemas.simulation.metering_policy_schema import (
    NetMeteringPolicy,
    # GrossMeteringPolicy, # For future phases
    # TimeOfUseRatePolicy, # For future phases
)
from app.data.schemas.simulation.simulation_runs_schema import (
    SimulationRuns,
    SimulationSelectedPolicy,
)
from app.domain.entities.house_profile import (
    HouseProfile,  # For 15-min interval data
)

# Placeholder for actual data models/entities when CRUDs are available
# from app.domain.entities.simulation_run import SimulationRun # TODO: Check if this is the correct path
# from app.domain.entities.net_metering_policy_params import NetMeteringPolicyParams # TODO: Check
from app.domain.entities.node import Node  # For type hinting
from app.domain.services.base_service import BaseService
from app.domain.services.simulator_engine.data_preparation_service import (
    DataPreparationService,
)
from app.domain.services.topology.house_service import HouseService
from app.domain.services.topology.net_topology_service import (
    NetTopologyService,
)

# from app.data.schemas.simulation.house_bill_schema import HouseBill # Not directly used, repository handles creation


class BillSimulationService:
    """
    Service responsible for calculating bills for a given simulation run.
    """

    # Hardcoded value as per requirement
    DEFAULT_SANCTIONED_LOAD_KW: float = 5.0

    def __init__(
        self,
        simulation_runs_service: BaseService,  # type: ignore
        simulation_selected_policy_service: BaseService,  # type: ignore
        net_metering_policy_service: BaseService,  # type: ignore
        net_metering_algorithm_service: BaseService,  # type: ignore
        # gross_metering_policy_service: BaseService, # For future phases
        # tou_rate_policy_service: BaseService, # For future phases
        house_bill_service: BaseService,  # type: ignore
        net_topology_service: NetTopologyService,
        house_service: HouseService,
        data_preparation_service: DataPreparationService,
    ):
        """
        Initializes the BillSimulationService.
        """
        self._simulation_runs_service = simulation_runs_service
        self._simulation_selected_policy_service = (
            simulation_selected_policy_service
        )
        self._net_metering_policy_service = net_metering_policy_service
        self._net_metering_algorithm_service = net_metering_algorithm_service
        # self._gross_metering_policy_service = gross_metering_policy_service
        # self._tou_rate_policy_service = tou_rate_policy_service
        self._house_bill_service = house_bill_service
        self._net_topology_service = net_topology_service
        self._house_service = house_service
        self._data_preparation_service = data_preparation_service

    def _fetch_simulation_configuration(
        self,
        simulation_run_id: uuid.UUID,  # Changed from int to uuid.UUID
    ) -> Dict[str, Any] | None:
        """
        Fetches the configuration for a given simulation run for Simple Net Metering.

        Args:
            simulation_run_id: The ID of the simulation run.

        Returns:
            A dictionary containing the simulation configuration, or None if not found
            or not a Simple Net Metering policy.
        """
        print(
            f"Fetching configuration for simulation_run_id: {simulation_run_id}"
        )

        sim_run: SimulationRuns | None = (
            self._simulation_runs_service.repository.get(simulation_run_id)  # type: ignore
        )
        if not sim_run:
            print(f"SimulationRun with id {simulation_run_id} not found.")
            return None

        # TODO: Confirm how policy_type (e.g., 'SIMPLE_NET') is determined.
        # Assuming it's part of SimulationRuns or SimulationSelectedPolicy for now.
        # For this phase, we assume the caller ensures it's a SIMPLE_NET run.

        selected_policy: SimulationSelectedPolicy | None = (
            self._simulation_selected_policy_service.repository.query()  # type: ignore
            .filter_by(simulation_run_id=simulation_run_id)
            .first()
        )

        if not selected_policy:
            print(
                f"SimulationSelectedPolicy for simulation_run_id {simulation_run_id} not found."
            )
            return None

        # Assuming selected_policy.net_metering_policy_id refers to the id
        # in the net_metering_policy_params table (NetMeteringPolicy schema)
        # The workflow doc mentions `net_metering_policy_type_id` in `simulation_selected_policies`
        # which seems to be the FK to `net_metering_policy_params`.
        # Let's assume the field is `selected_policy.policy_parameters_id` or similar
        # and it points to the ID in the `net_metering_policy_params` table.
        # For now, using `selected_policy.net_metering_policy_id` as a placeholder name.

        # Check if it's a net metering policy first
        if not selected_policy.net_metering_policy_type_id:
            print(
                f"Selected policy for run {simulation_run_id} does not specify a net metering policy type."
            )
            return None

        # Confirm the policy type is 'SIMPLE_NET'
        metering_algorithm: NetMeteringAlgorithm | None = (
            self._net_metering_algorithm_service.repository.get(  # type: ignore
                selected_policy.net_metering_policy_type_id
            )
        )
        if not metering_algorithm:
            print(
                f"NetMeteringAlgorithm with id {selected_policy.net_metering_policy_type_id} not found."
            )
            return None

        # Assuming NetMeteringAlgorithm has a 'policy_code' field for 'SIMPLE_NET'
        if (
            getattr(metering_algorithm, "policy_code", "").upper()
            != "SIMPLE_NET"
        ):
            print(
                f"Policy type is {getattr(metering_algorithm, 'policy_code', '')}, not SIMPLE_NET."
            )
            return None

        # Fetch the parameters for this specific net metering policy type
        # The `selected_policy.net_metering_policy_type_id` is the ID of the algorithm/type.
        # The `NetMeteringPolicy` table stores parameters and should also be keyed by this ID
        # if `net_metering_policy_params` is indeed the `NetMeteringPolicy` table.
        # Workflow: "Read the net_metering_policy_params record."
        # This implies NetMeteringPolicy.id should match selected_policy.net_metering_policy_type_id.
        net_metering_params: NetMeteringPolicy | None = (
            self._net_metering_policy_service.repository.get(  # type: ignore
                selected_policy.net_metering_policy_type_id
            )
        )

        if not net_metering_params:
            print(
                f"NetMeteringPolicy (params) with id {selected_policy.net_metering_policy_type_id} not found."
            )
            return None

        return {
            "simulation_run_id": sim_run.id,
            "billing_cycle_month": sim_run.billing_cycle_month,
            "billing_cycle_year": sim_run.billing_cycle_year,
            "topology_root_node_id": str(
                sim_run.topology_root_node_id.id
            ),  # Access the id attribute of the Node object
            "policy_type": "SIMPLE_NET",  # Confirmed by check above
            "net_metering_policy_type_id": selected_policy.net_metering_policy_type_id,  # This is the ID of the NetMeteringAlgorithm
            "fixed_charge_tariff_rate_per_kw": selected_policy.fixed_charge_tariff_rate_per_kw,
            "fac_charge_per_kwh_imported": selected_policy.fac_charge_per_kwh_imported,
            "tax_rate_on_energy_charges": selected_policy.tax_rate_on_energy_charges,
            "retail_price_per_kwh": net_metering_params.retail_price_per_kwh,
        }

    def _get_houses_in_topology(
        self, topology_root_node_id: str
    ) -> List[Node]:  # Return list of Node (House) objects
        """
        Identifies all houses belonging to the given topology root node.
        Uses NetTopologyService to get houses.

        Args:
            topology_root_node_id: The root node ID of the topology
                                   (e.g., substation ID), as a string UUID.

        Returns:
            A list of Node (House) entity objects.
        """
        print(
            f"Fetching houses for topology_root_node_id: {topology_root_node_id}"
        )

        substation_uuid: uuid.UUID | None = None
        try:
            substation_uuid = uuid.UUID(topology_root_node_id)
        except ValueError:
            print(
                f"Invalid topology_root_node_id format: {topology_root_node_id}. Expected UUID."
            )
            return []

        try:
            # get_houses_by_substation_id returns List[House], and House is a subclass of Node.
            houses_in_substation: List[Node] = (
                self._net_topology_service.get_houses_by_substation_id(  # type: ignore
                    substation_id=substation_uuid  # type: ignore
                )
            )
        except Exception as e:
            print(
                f"Error fetching houses from NetTopologyService for substation_id {substation_uuid}: {e}"
            )
            return []

        if not houses_in_substation:
            print(
                f"No houses found by NetTopologyService for substation_id: {topology_root_node_id}"
            )
            return []

        print(
            f"Found {len(houses_in_substation)} houses for substation {topology_root_node_id}"
        )
        return houses_in_substation

    def calculate_bills_for_simulation_run(
        self,
        simulation_run_id: uuid.UUID,  # Changed from int to uuid.UUID
    ) -> None:
        """
        Calculates bills for all houses in a given simulation run.

        Args:
            simulation_run_id: The ID of the simulation run.
        """
        print(
            f"Starting bill calculation for simulation_run_id: {simulation_run_id}"
        )

        # 1. Fetch Simulation Configuration
        config = self._fetch_simulation_configuration(simulation_run_id)
        print(f"Configuration fetched: {config}")

        if not config:
            print(
                f"Error: Could not fetch configuration for simulation run {simulation_run_id}."
            )
            # Update simulation_runs status to 'FAILED' (when CRUD is available)
            return

        topology_root_node_id = config.get("topology_root_node_id")
        if not topology_root_node_id:
            print("Error: topology_root_node_id not found in configuration.")
            return

        # 2. Iterate Through Houses in the Topology
        houses = self._get_houses_in_topology(topology_root_node_id)
        print(f"Houses found in topology: {houses}")

        if not houses:
            print(
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
            print(
                f"Processing house: {house_node_id} with Sanctioned Load: {sanctioned_load_kw} kW"
            )

            # 3. Aggregate Energy Data for the Billing Cycle for Each House
            billing_month = config["billing_cycle_month"]
            billing_year = config["billing_cycle_year"]

            print(
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
                print(
                    f"  Error calling get_house_profile for house {house_node_id}: {e}"
                )
                # TODO: Log this error and decide if to continue or fail the run
                continue

            if not house_profile:
                print(
                    f"  Error: Could not get HouseProfile for house {house_node_id}."
                )
                # TODO: Decide how to handle this error for the specific house.
                # Maybe log and continue to the next house, or mark this house's bill as failed.
                continue

            total_imported_units = 0.0
            total_exported_units = 0.0

            # Assuming HouseProfile has these attributes as lists of numbers/timestamps
            timestamps = getattr(
                house_profile, "timestamps", []
            )  # List[datetime.datetime]
            imported_intervals = getattr(
                house_profile, "imported_units_intervals", []
            )  # List[float]
            exported_intervals = getattr(
                house_profile, "exported_units_intervals", []
            )  # List[float]

            if not (
                len(timestamps)
                == len(imported_intervals)
                == len(exported_intervals)
            ):
                print(
                    f"  Error: Mismatch in lengths of interval data arrays for house {house_node_id}."
                )
                continue

            for i, ts in enumerate(timestamps):
                if ts.year == billing_year and ts.month == billing_month:
                    total_imported_units += imported_intervals[i]
                    total_exported_units += exported_intervals[i]

            print(
                f"  Aggregated for {billing_month}/{billing_year} - "
                f"Total Imported: {total_imported_units:.2f} kWh, "
                f"Total Exported: {total_exported_units:.2f} kWh"
            )

            # 4. Calculate Bill Components (logic will depend on policy_type from config)
            # 4. Calculate Bill Components for "Simple Net Metering"
            bill_amount = 0.0
            bill_details: Dict[str, Any] = {}

            if config.get("policy_type") == "SIMPLE_NET":
                print(
                    f"  Calculating bill for SIMPLE_NET policy for house {house_node_id}..."
                )

                net_usage_kwh = total_imported_units - total_exported_units
                retail_rate = config["retail_price_per_kwh"]

                energy_charges = 0.0
                if net_usage_kwh > 0:
                    energy_charges = net_usage_kwh * retail_rate

                # Credit_Amount_calc is pending for future iteration as per workflow.
                # credit_amount_calc = 0.0
                # if net_usage_kwh < 0:
                # credit_amount_calc = abs(net_usage_kwh) * retail_rate

                fixed_charges = (
                    config["fixed_charge_tariff_rate_per_kw"]
                    * sanctioned_load_kw
                )
                fac_charges = (
                    total_imported_units
                    * config["fac_charge_per_kwh_imported"]
                )

                tax_amount = 0.0
                if energy_charges > 0:
                    tax_amount = (
                        energy_charges * config["tax_rate_on_energy_charges"]
                    )

                arrears = 0.0  # Assume 0 for now as per workflow

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
                    # "credit_amount_calculated": round(credit_amount_calc, 2), # Deferred
                    "fixed_charge_tariff_rate_per_kw": config[
                        "fixed_charge_tariff_rate_per_kw"
                    ],
                    "sanctioned_load_kw": sanctioned_load_kw,
                    "fixed_charges": round(fixed_charges, 2),
                    "fac_charge_per_kwh_imported": config[
                        "fac_charge_per_kwh_imported"
                    ],
                    "fac_charges": round(fac_charges, 2),
                    "tax_rate_on_energy_charges": config[
                        "tax_rate_on_energy_charges"
                    ],
                    "tax_amount_on_energy": round(tax_amount, 2),
                    "arrears": round(arrears, 2),
                    "total_bill_amount_calculated": round(
                        total_bill_amount, 2
                    ),
                }
                # bill_amount variable is redundant here as its value is in bill_details
                print(f"  Calculated Bill Details: {bill_details}")

            else:
                print(
                    f"  Policy type {config.get('policy_type')} not yet supported "
                    f"for house {house_node_id}."
                )
                continue  # or handle error

            # 5. Store Bill Results for Each House
            #    - Create a record in simulation_engine.house_bills.
            #    - Mocking this for now.
            # print(
            #     f"  Storing bill for house {house_node_id}: Amount={bill_amount}, "
            #     f"Details={bill_details}"
            # )
            try:
                # Ensure all values in bill_details are suitable for HouseBill schema
                # The `bill_details` dictionary already contains most of the fields.
                # We need to map them correctly to HouseBill fields.
                # HouseBill schema: simulation_run_id, house_node_id, total_energy_imported_kwh,
                # total_energy_exported_kwh, net_energy_balance_kwh, calculated_bill_amount, bill_details (JSONB)

                house_bill_record = {
                    "simulation_run_id": simulation_run_id,  # This should be the UUID of the sim_run
                    "house_node_id": house_node_id,  # This should be the UUID of the house
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
                    "bill_details": bill_details,  # Store the whole dict as JSON
                }

                # Convert UUID strings to UUID objects if necessary for the repository
                # Assuming sim_run.id is already a UUID from _fetch_simulation_configuration
                # and house_node_id is a string UUID.
                if isinstance(config.get("simulation_run_id"), uuid.UUID):
                    house_bill_record["simulation_run_id"] = config[
                        "simulation_run_id"
                    ]
                else:  # If it's a string from config, convert
                    try:
                        house_bill_record["simulation_run_id"] = uuid.UUID(
                            str(config["simulation_run_id"])
                        )
                    except ValueError:
                        print(
                            f"  Error: Invalid simulation_run_id format for HouseBill: {config.get('simulation_run_id')}"
                        )
                        continue  # Skip this bill record

                try:
                    house_bill_record["house_node_id"] = uuid.UUID(
                        house_node_id
                    )
                except ValueError:
                    print(
                        f"  Error: Invalid house_node_id format for HouseBill: {house_node_id}"
                    )
                    continue  # Skip this bill record

                self._house_bill_service.repository.create(**house_bill_record)  # type: ignore
                print(f"  Successfully stored bill for house {house_node_id}.")
            except Exception as e:
                print(f"  Error storing bill for house {house_node_id}: {e}")
                # TODO: Log error, potentially mark this house's bill as failed or roll back.

        # 6. Update simulation_runs Status
        #    - Set status to 'COMPLETED' (or 'FAILED').
        current_timestamp = datetime.utcnow()
        final_status = "COMPLETED"  # Assume success unless errors occurred and were handled

        # TODO: Implement more robust error tracking throughout the process.
        # If any house bill failed to store, or critical data was missing,
        # the status might be 'PARTIALLY_COMPLETED' or 'FAILED'.
        # For now, assuming if it reaches here without returning early, it's COMPLETED.

        try:
            sim_run_to_update: SimulationRuns | None = (
                self._simulation_runs_service.repository.get(simulation_run_id)  # type: ignore
            )
            if sim_run_to_update:
                sim_run_to_update.status = final_status  # type: ignore
                sim_run_to_update.simulation_end_timestamp = current_timestamp  # type: ignore
                sim_run_to_update.modified_on = current_timestamp  # type: ignore
                sim_run_to_update.save()  # Use the instance's save method
                print(
                    f"Simulation run {simulation_run_id} status updated to {final_status}."
                )
            else:
                print(
                    f"Error: Could not find simulation run {simulation_run_id} to update status."
                )
        except Exception as e:
            print(
                f"Error updating status for simulation run {simulation_run_id}: {e}"
            )
            # This error itself might warrant a different status or logging.

        print(
            f"Bill calculation process finished for simulation_run_id: {simulation_run_id}."
        )


# Removed __main__ block as it's not suitable with dependency injection


"""
TODO:
- Integrate with actual CRUD services for fetching simulation
  configurations.
- Integrate with TopologyService to get actual house data.
- Integrate with DataPreparationService to get 15-minute interval
  energy data.
- Implement detailed bill calculation logic for "Simple Net Metering"
  (Phase 1, Step 4).
- Implement logic to store bill results (Phase 1, Step 5).
- Implement logic to update simulation_runs status (Phase 1, Step 6).
- Add comprehensive error handling and logging.
- Add unit tests.
"""
