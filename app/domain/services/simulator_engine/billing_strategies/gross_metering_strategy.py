"""
Concrete strategy for Gross Metering policy.
"""

from typing import Any, Dict
from uuid import UUID

from app.data.interfaces.i_repository import IRepository
from app.domain.interfaces.i_service import IService
from app.domain.interfaces.simulator_engine.i_policy_strategy import (
    IBillingPolicyStrategy,
)
from app.utils.logger import logger


class GrossMeteringStrategy(IBillingPolicyStrategy):
    """
    Implements billing calculations for Gross Metering.
    """

    def __init__(
        self,
        gross_metering_policy_repo: IRepository,
        selected_policy_repository: IRepository,
    ):
        """
        Initializes the GrossMeteringStrategy.
        """
        self._gross_metering_policy_repo = gross_metering_policy_repo
        self._selected_policy_repository = selected_policy_repository

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

    def get_policy_config(
        self,
        simulation_run_id: UUID,
        common_params: Dict[str, Any],
    ) -> Dict[str, Any]:
        """
        Fetches and constructs the policy-specific configuration for Gross Metering.
        """
        logger.info(
            f"Fetching Gross Metering config for run {simulation_run_id}"
        )
        # gross_metering_policy_repo is now an instance variable
        if not self._gross_metering_policy_repo:
            logger.error(
                "GrossMeteringPolicy repository not initialized in GrossMeteringStrategy."
            )
            return common_params

        params = self._gross_metering_policy_repo.read_or_none(
            simulation_run_id
        )
        if not params:
            logger.warning(
                f"GrossMeteringPolicy for run {simulation_run_id} not found."
            )
            return common_params

        policy_specific_params = {
            "import_retail_price_kwh": params.import_retail_price_per_kwh,
            "exp_whole_price_kwh": params.export_wholesale_price_per_kwh,
            "fixed_charge_per_kw": params.fixed_charge_tariff_rate_per_kw,
        }
        policy_specific_params.update(common_params)
        logger.info(
            f"Constructed Gross Metering config: {policy_specific_params}"
        )
        return policy_specific_params

    def store_bill_details(
        self,
        run_id: UUID,
        house_node_id: str,
        bill_details: Dict[str, Any],
        house_bill_service: IService,
    ) -> None:
        """
        Stores the calculated bill details for Gross Metering.
        """
        logger.info(
            f"Storing bill for house {house_node_id} under run {run_id}"
        )
        if not house_bill_service:
            logger.error(
                "house_bill_service not provided to GrossMeteringStrategy store_bill_details"
            )
            raise ValueError(
                "house_bill_service is required for storing bill details."
            )

        actual_total_imported = bill_details.get("total_imported_kwh", 0.0)
        actual_total_exported = bill_details.get("total_exported_kwh", 0.0)

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

        try:
            house_bill_service.create(user_id=None, **house_bill_record)
            logger.info(
                f"  Successfully stored bill for house {house_node_id} via GrossMeteringStrategy."
            )
        except Exception as e:
            logger.error(
                f"  Error storing bill for house {house_node_id} via GrossMeteringStrategy: {e}"
            )
            raise
