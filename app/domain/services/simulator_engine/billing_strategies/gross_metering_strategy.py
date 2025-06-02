"""
Concrete strategy for Gross Metering policy.
"""

from typing import Any, Dict

from app.domain.services.simulator_engine.billing_strategies.i_billing_policy_strategy import (
    IBillingPolicyStrategy,
)
from app.utils.logger import logger


class GrossMeteringStrategy(IBillingPolicyStrategy):
    """
    Implements billing calculations for Gross Metering.
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
        Calculates bill components for Gross Metering.
        """
        logger.info(
            f"  Calculating bill for house {house_node_id} using GrossMeteringStrategy..."
        )

        total_imported_units = energy_summary.get("total_imported_units", 0.0)
        total_exported_units = energy_summary.get("total_exported_units", 0.0)

        import_retail_price = policy_config["import_retail_price_kwh"]
        export_wholesale_price = policy_config["exp_whole_price_kwh"]

        imported_energy_charges = total_imported_units * import_retail_price
        exported_energy_credit = total_exported_units * export_wholesale_price

        fixed_charges = 0.0
        if policy_config.get("fixed_charge_per_kw") is not None:
            fixed_charges = (
                policy_config["fixed_charge_per_kw"] * sanctioned_load_kw
            )

        fac_charges = (
            total_imported_units * policy_config["fac_charge_per_kwh"]
        )

        tax_amount = 0.0
        # Assuming tax on imported energy charges for gross metering
        if imported_energy_charges > 0:
            tax_amount = imported_energy_charges * policy_config["tax_rate"]

        arrears = 0.0  # Assume 0 for now

        total_bill_amount = (
            imported_energy_charges
            + fixed_charges
            + fac_charges
            + tax_amount
            - exported_energy_credit
        )

        bill_details = {
            "house_node_id": house_node_id,
            "billing_cycle_month": billing_month,
            "billing_cycle_year": billing_year,
            "policy_type": "GROSS_METERING",
            "total_imported_kwh": round(total_imported_units, 2),
            "total_exported_kwh": round(total_exported_units, 2),
            "import_retail_price_per_kwh": import_retail_price,
            "exp_whole_price_kwh": export_wholesale_price,
            "imported_energy_charges": round(imported_energy_charges, 2),
            "exported_energy_credit": round(exported_energy_credit, 2),
            "fixed_charge_per_kw": policy_config.get("fixed_charge_per_kw"),
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
            f"  Calculated Gross Metering Bill Details: {bill_details}"
        )
        return bill_details
