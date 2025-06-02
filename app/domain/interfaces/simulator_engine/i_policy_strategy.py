"""
Interface for billing policy strategies.
"""

from abc import ABC, abstractmethod
from typing import Any, Dict
from uuid import UUID


class IBillingPolicyStrategy(ABC):
    """
    Interface for different billing policy calculation strategies.
    """

    @abstractmethod
    def calculate_bill_components(
        self,
        policy_config: Dict[str, Any],
        energy_summary: Dict[str, float],
        sanctioned_load_kw: float,
        house_node_id: str,  # Added for logging/context if needed by strategy
        billing_month: int,  # Added for context
        billing_year: int,  # Added for context
        house_profile_data: Dict[str, Any],
    ) -> Dict[str, Any]:
        """
        Calculates the bill components based on the specific policy.

        Args:
            policy_config: Configuration specific to the policy
                           (e.g., rates, fixed charges).
            energy_summary: A dictionary containing aggregated energy data like
                            "total_imported_units" and "total_exported_units"
                            for the billing period.
                            if calculations are done on raw intervals.
            sanctioned_load_kw: The sanctioned load for the house in kW.
            house_node_id: The ID of the house node.
            billing_month: The billing cycle month.
            billing_year: The billing cycle year.
            house_profile_data: Dictionary containing 'timestamps',
            'imported_intervals','exported_intervals' for detailed TOU.

        Returns:
            A dictionary containing detailed bill components.
            This dictionary should be comprehensive enough to be stored
            as "bill_details" in the HouseBill entity and include
            "total_bill_amount_calculated".
        """
        pass

    @abstractmethod
    def get_policy_config(
        self,
        simulation_run_id: UUID,
        common_params: Dict[str, Any],
        # Used to pass repositories:
        # net_metering_policy_repo, gross_metering_policy_repo,
        # tou_rate_policy_params_repo
        **kwargs: Any,
    ) -> Dict[str, Any]:
        """
        Fetches and constructs the policy-specific configuration.

        Args:
            simulation_run_id: The ID of the simulation run.
            common_params: A dictionary of common parameters already fetched
                           (e.g., fac_charge, tax_rate).
            **kwargs: For passing necessary repositories or other dependencies.

        Returns:
            A dictionary containing the fully constructed policy_config.
            This will be passed to calculate_bill_components.
        """
        pass

    @abstractmethod
    def store_bill_details(
        self,
        run_id: UUID,
        house_node_id: str,
        bill_details: Dict[str, Any],
        # Used to pass house_bill_service
        **kwargs: Any,
    ) -> None:
        """
        Stores the calculated bill details into the database.

        Args:
            run_id: The ID of the simulation run.
            house_node_id: The ID of the house for which the bill.
            bill_details: The dictionary of bill components returned by
                          calculate_bill_components.
            **kwargs: For passing necessary services (house_bill_service).
        """
        pass
