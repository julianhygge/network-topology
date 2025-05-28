"""
Module for simulating bills based on energy consumption and generation data.
"""

from typing import Any, Dict, List

# Placeholder for actual data models/entities when CRUDs are available
# from app.domain.entities.simulation_run import SimulationRun
# from app.domain.entities.net_metering_policy_params import (
#    NetMeteringPolicyParams
# )
# from app.domain.entities.house import House


class BillSimulationService:
    """
    Service responsible for calculating bills for a given simulation run.
    """

    # Hardcoded value as per requirement
    DEFAULT_SANCTIONED_LOAD_KW: float = 5.0

    def __init__(self):
        """
        Initializes the BillSimulationService.
        Dependencies like topology service, data preparation service,
        and repositories for simulation configurations would be injected here.
        """
        # In a real scenario, these would be injected:
        # self._topology_service = topology_service
        # self._data_preparation_service = data_preparation_service
        # self._simulation_run_repository = simulation_run_repository
        # ... and other repositories
        pass

    def _fetch_simulation_configuration(
        self, simulation_run_id: int
    ) -> Dict[str, Any]:
        """
        Fetches the configuration for a given simulation run.
        This is a MOCKED implementation as CRUD services are not yet available.

        Args:
            simulation_run_id: The ID of the simulation run.

        Returns:
            A dictionary containing the simulation configuration.
        """
        # Mocked data based on bill_simulation_workflow.md
        # Phase 1: Simple Net Metering
        print(
            f"Fetching mocked configuration for s_run_id: {simulation_run_id}"
        )
        return {
            "simulation_run_id": simulation_run_id,
            "billing_cycle_month": 1,  # January
            "billing_cycle_year": 2023,
            "topology_root_node_id": "substation_1",  # Example ID
            "policy_type": "SIMPLE_NET",  # Assuming this is derived or stored
            # Example
            "net_metering_policy_type_id": "SIMPLE_NET_POLICY_ID_1",
            # Example rate in currency/kW
            "fixed_charge_tariff_rate_per_kw": 100.0,
            # Example rate in currency/kWh
            "fac_charge_per_kwh_imported": 0.5,
            "tax_rate_on_energy_charges": 0.18,  # Example 18%
            "retail_price_per_kwh": 7.5,  # Example currency/kWh
        }

    def _get_houses_in_topology(
        self, topology_root_node_id: str
    ) -> List[Dict[str, Any]]:
        """
        Identifies all houses belonging to the given topology root node.
        This is a MOCKED implementation.

        Args:
            topology_root_node_id: The root node ID of the topology
                                   (e.g., substation ID).

        Returns:
            A list of dictionaries, where each dictionary represents a house
            and includes its 'house_node_id' and 'sanctioned_load_kw'.
        """
        # Mocked data
        # In a real scenario, this would use a topology service to get house IDs
        # and then fetch sanctioned load for each house.
        print(
            f"Fetching mocked houses for topology_root_node_id: {topology_root_node_id}"
        )
        houses_data = [
            {"house_node_id": "house_1", "connection_kw": 4.0},
            {"house_node_id": "house_2", "connection_kw": 6.0},
            # Test case for missing connection_kw
            {"house_node_id": "house_3"},
        ]

        processed_houses = []
        for house_data in houses_data:
            sanctioned_load = house_data.get(
                "connection_kw", self.DEFAULT_SANCTIONED_LOAD_KW
            )
            processed_houses.append(
                {
                    "house_node_id": house_data["house_node_id"],
                    "sanctioned_load_kw": sanctioned_load,
                }
            )
        return processed_houses

    def calculate_bills_for_simulation_run(
        self, simulation_run_id: int
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
        for house in houses:
            house_node_id = house["house_node_id"]
            sanctioned_load_kw = house["sanctioned_load_kw"]
            print(
                f"Processing house: {house_node_id} with Sanctioned Load: {sanctioned_load_kw} kW"
            )

            # 3. Aggregate Energy Data for the Billing Cycle for Each House
            #    - This will involve using DataPreparationService or similar
            #      to get 15-min interval data for the house.
            #    - Then, sum Import_Interval and Export_Interval for the
            #      billing month/year.
            #    - Mocking this for now.
            total_imported_units = 150.0  # kWh, example
            total_exported_units = 20.0  # kWh, example
            print(
                f"  Mocked Total Imported: {total_imported_units} kWh, "
                f"Mocked Total Exported: {total_exported_units} kWh"
            )

            # 4. Calculate Bill Components (logic will depend on policy_type from config)
            #    - This will be implemented in subsequent steps.
            #    - For now, just a placeholder.
            if config.get("policy_type") == "SIMPLE_NET":
                print(
                    f"  Calculating bill for SIMPLE_NET policy for house {house_node_id}..."
                )
                # ... detailed calculation logic here ...
                bill_amount = 0  # Placeholder
                bill_details = {}  # Placeholder
            else:
                print(
                    f"  Policy type {config.get('policy_type')} not yet supported "
                    f"for house {house_node_id}."
                )
                continue  # or handle error

            # 5. Store Bill Results for Each House
            #    - Create a record in simulation_engine.house_bills.
            #    - Mocking this for now.
            print(
                f"  Storing bill for house {house_node_id}: Amount={bill_amount}, "
                f"Details={bill_details}"
            )

        # 6. Update simulation_runs Status
        #    - Set status to 'COMPLETED' (or 'FAILED').
        #    - Mocking this for now.
        print(
            f"Bill calculation completed for simulation_run_id: {simulation_run_id}. "
            f"Updating status (mocked)."
        )


if __name__ == "__main__":
    # Example usage (for testing purposes)
    service = BillSimulationService()
    service.calculate_bills_for_simulation_run(simulation_run_id=1)


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
