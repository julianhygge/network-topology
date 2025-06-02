"""
Interface for billing policy strategies.
"""

from abc import ABC, abstractmethod
from typing import Any, Dict


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
        house_profile_data: Dict[
            str, Any
        ],  # For TOU, raw 15-min data might be needed
    ) -> Dict[str, Any]:
        """
        Calculates the bill components based on the specific policy.

        Args:
            policy_config: Configuration specific to the policy
                           (e.g., rates, fixed charges).
            energy_summary: A dictionary containing aggregated energy data like
                            "total_imported_units" and "total_exported_units"
                            for the billing period. For TOU, this might be less relevant
                            if calculations are done on raw intervals.
            sanctioned_load_kw: The sanctioned load for the house in kW.
            house_node_id: The ID of the house node.
            billing_month: The billing cycle month.
            billing_year: The billing cycle year.
            house_profile_data: Dictionary containing 'timestamps', 'imported_intervals',
                                'exported_intervals' for detailed TOU calculations.

        Returns:
            A dictionary containing detailed bill components.
            This dictionary should be comprehensive enough to be stored
            as "bill_details" in the HouseBill entity and include
            "total_bill_amount_calculated".
        """
        pass
