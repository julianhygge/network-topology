"""
Concrete strategy for Simple Net Metering policy.
"""

from typing import Any, Dict

from app.domain.services.simulator_engine.billing_strategies.i_billing_policy_strategy import (
    IBillingPolicyStrategy,
)
from app.utils.logger import logger


class SimpleNetMeteringStrategy(IBillingPolicyStrategy):
    """
    Implements billing calculations for Simple Net Metering.
    """

    def calculate_bill_components(
        self,
        policy_config: Dict[str, Any],
        energy_summary: Dict[str, float],
        sanctioned_load_kw: float,
        house_node_id: str,
        billing_month: int,
        billing_year: int,
        house_profile_data: Dict[str, Any],  # Not used by this strategy
    ) -> Dict[str, Any]:
        """
        Calculates bill components for Simple Net Metering.
        """
        logger.info(
            f"  Calculating bill for house {house_node_id} using SimpleNetMeteringStrategy..."
        )

        total_imported_units = energy_summary.get("total_imported_units", 0.0)
        total_exported_units = energy_summary.get("total_exported_units", 0.0)

        net_usage_kwh = total_imported_units - total_exported_units
        retail_rate = policy_config["retail_price_per_kwh"]

        energy_charges = 0.0
        if net_usage_kwh > 0:
            energy_charges = net_usage_kwh * retail_rate

        # credit_amount_calc = 0.0 # Future scope
        # if net_usage_kwh < 0:
        # credit_amount_calc = abs(net_usage_kwh) * retail_rate

        fixed_charges = (
            policy_config["fixed_charge_per_kw"] * sanctioned_load_kw
        )
        fac_charges = (
            total_imported_units * policy_config["fac_charge_per_kwh"]
        )

        tax_amount = 0.0
        if energy_charges > 0:
            tax_amount = energy_charges * policy_config["tax_rate"]

        arrears = 0.0  # Assume 0 for now

        total_bill_amount = (
            energy_charges
            + fixed_charges
            + fac_charges
            + tax_amount
            - arrears  # Subtracting arrears, though it's 0 now
        )

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
            # "credit_amount_calculated": round(credit_amount_calc, 2), # Future
            "fixed_charge_per_kw": policy_config["fixed_charge_per_kw"],
            "sanctioned_load_kw": sanctioned_load_kw,
            "fixed_charges": round(fixed_charges, 2),
            "fac_charge_per_kwh": policy_config["fac_charge_per_kwh"],
            "fac_charges": round(fac_charges, 2),
            "tax_rate": policy_config["tax_rate"],
            "tax_amount_on_energy": round(tax_amount, 2),
            "arrears": round(arrears, 2),
            "total_bill_amount_calculated": round(total_bill_amount, 2),
        }
        logger.info(
            f"  Calculated Simple Net Metering Bill Details: {bill_details}"
        )
        return bill_details
