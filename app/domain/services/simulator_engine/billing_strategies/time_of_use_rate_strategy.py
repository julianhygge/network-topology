"""
Concrete strategy for Time of Use (TOU) Rate policy.
"""

import datetime
from typing import Any, Dict, List
from uuid import UUID

from app.data.interfaces.i_repository import IRepository
from app.domain.interfaces.i_service import IService
from app.domain.interfaces.simulator_engine.i_policy_strategy import \
    IBillingPolicyStrategy

from app.utils.logger import logger


class TimeOfUseRateStrategy(IBillingPolicyStrategy):
    """
    Implements billing calculations for Time of Use (TOU) Rate.
    """

    def __init__(
        self,
        tou_rate_policy_params_repo: IRepository,
        selected_policy_repository: IRepository,
    ):
        """
        Initializes the TimeOfUseRateStrategy.
        """
        self._tou_rate_policy_params_repo = tou_rate_policy_params_repo
        self._selected_policy_repository = selected_policy_repository

    def calculate_bill_components(
        self,
        policy_config: Dict[str, Any],
        energy_summary: Dict[
            str, float
        ],  # Less relevant here, direct interval data used
        sanctioned_load_kw: float,
        house_node_id: str,
        billing_month: int,
        billing_year: int,
        house_profile_data: Dict[str, Any],
    ) -> Dict[str, Any]:
        """
        Calculates bill components for TOU Rate.
        """
        logger.info(
            f"  Calculating bill for house {house_node_id}"
            f"using TimeOfUseRateStrategy..."
        )

        tou_periods_config = policy_config["tou_periods"]
        overall_total_imported_units = 0.0
        overall_total_exported_units = 0.0
        tou_energy_data_details = []

        total_energy_charges_tou = 0.0
        total_export_credit_tou = 0.0

        timestamps: List[datetime.datetime] = house_profile_data.get(
            "timestamps", []
        )
        imported_intervals: List[float] = house_profile_data.get(
            "imported_intervals", []
        )
        exported_intervals: List[float] = house_profile_data.get(
            "exported_intervals", []
        )

        if not (
            len(timestamps)
            == len(imported_intervals)
            == len(exported_intervals)
        ):
            logger.error(
                f"  Error: Mismatch in TOU data lengths for house {house_node_id}."
            )
            # Return a bill with 0 amounts or raise an error
            # For now, returning a minimal bill structure indicating an error might be best
            return {
                "house_node_id": house_node_id,
                "billing_cycle_month": billing_month,
                "billing_cycle_year": billing_year,
                "policy_type": "TOU_RATE",
                "error": "Data mismatch in TOU intervals",
                "total_bill_amount_calculated": 0.0,
            }

        for period_config in tou_periods_config:
            period_label = period_config["time_period_label"]
            # Ensure start_time and end_time are datetime.time objects
            start_time_val = period_config["start_time"]
            end_time_val = period_config["end_time"]

            if isinstance(start_time_val, str):
                start_time = datetime.time.fromisoformat(start_time_val)
            elif isinstance(start_time_val, datetime.time):
                start_time = start_time_val
            else:
                logger.error(
                    f"Invalid start_time format for period {period_label}"
                )
                continue

            if isinstance(end_time_val, str):
                end_time = datetime.time.fromisoformat(end_time_val)
            elif isinstance(end_time_val, datetime.time):
                end_time = end_time_val
            else:
                logger.error(
                    f"Invalid end_time format for period {period_label}"
                )
                continue

            import_rate = period_config["import_retail_rate_per_kwh"]
            export_rate = period_config["exp_whole_rate_per_kwh"]

            current_period_imported_kwh = 0.0
            current_period_exported_kwh = 0.0

            for i, ts_datetime_val in enumerate(timestamps):
                # Ensure we are in the correct billing month and year (year is fixed to 2023 later)
                if not (
                    ts_datetime_val.month == billing_month
                    and ts_datetime_val.year == billing_year
                ):
                    continue

                interval_time = ts_datetime_val.time()

                if (
                    start_time <= end_time
                ):  # Normal period (e.g., 08:00 to 17:00)
                    if start_time <= interval_time < end_time:
                        current_period_imported_kwh += imported_intervals[i]
                        current_period_exported_kwh += exported_intervals[i]
                else:  # Overnight period (e.g., 22:00 to 06:00)
                    if interval_time >= start_time or interval_time < end_time:
                        current_period_imported_kwh += imported_intervals[i]
                        current_period_exported_kwh += exported_intervals[i]

            overall_total_imported_units += current_period_imported_kwh
            overall_total_exported_units += current_period_exported_kwh

            import_cost_period = current_period_imported_kwh * import_rate
            export_credit_period = current_period_exported_kwh * export_rate

            total_energy_charges_tou += import_cost_period
            total_export_credit_tou += export_credit_period

            tou_energy_data_details.append(
                {
                    "period_label": period_label,
                    "start_time": start_time.isoformat(),
                    "end_time": end_time.isoformat(),
                    "imported_kwh": round(current_period_imported_kwh, 2),
                    "exported_kwh": round(current_period_exported_kwh, 2),
                    "import_rate_per_kwh": import_rate,
                    "export_rate_per_kwh": export_rate,
                    "import_cost_period": round(import_cost_period, 2),
                    "export_credit_period": round(export_credit_period, 2),
                }
            )

        fixed_charges = 0.0
        if policy_config.get("fixed_charge_per_kw") is not None:
            fixed_charges = (
                policy_config["fixed_charge_per_kw"] * sanctioned_load_kw
            )
        else:
            logger.warning("fixed_charge_per_kw not in TOU config. Using 0.0")

        fac_charges = (
            overall_total_imported_units * policy_config["fac_charge_per_kwh"]
        )

        tax_amount = 0.0
        if total_energy_charges_tou > 0:
            tax_amount = total_energy_charges_tou * policy_config["tax_rate"]

        arrears = 0.0  # Assume 0 for now

        total_bill_amount = (
            total_energy_charges_tou
            + fixed_charges
            + fac_charges
            + tax_amount
            - total_export_credit_tou
            - arrears
        )

        bill_details = {
            "house_node_id": house_node_id,
            "billing_cycle_month": billing_month,
            "billing_cycle_year": billing_year,
            "policy_type": "TOU_RATE",
            "overall_total_imported_kwh": round(
                overall_total_imported_units, 2
            ),
            "overall_total_exported_kwh": round(
                overall_total_exported_units, 2
            ),
            "tou_period_details": tou_energy_data_details,
            "total_energy_charges": round(total_energy_charges_tou, 2),
            "total_export_credit": round(total_export_credit_tou, 2),
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
        logger.info(f"  Calculated TOU Bill Details: {bill_details}")
        return bill_details

    def get_policy_config(
        self,
        simulation_run_id: UUID,
        common_params: Dict[str, Any],
    ) -> Dict[str, Any]:
        """
        Fetches and constructs the policy-specific configuration for TOU Rate.
        """
        logger.info(f"Fetching TOU Rate config for run {simulation_run_id}")

        if (
            not self._tou_rate_policy_params_repo
            or not self._selected_policy_repository
        ):
            logger.error(
                "Required repositories not initialized in TimeOfUseRateStrategy."
            )
            return common_params

        policy_specific_params = {}
        tou_params_list = self._tou_rate_policy_params_repo.filter(
            simulation_run_id=simulation_run_id
        )

        if not tou_params_list:
            logger.warning(
                f"TimeOfUseRatePolicy params for run {simulation_run_id} not found."
            )
            # Depending on requirements, might return common_params or raise
            return common_params

        policy_specific_params["tou_periods"] = [
            {
                "id": str(p.id),
                "time_period_label": p.time_period_label,
                "start_time": p.start_time,
                "end_time": p.end_time,
                "import_retail_rate_per_kwh": p.import_retail_rate_per_kwh,
                "exp_whole_rate_per_kwh": p.export_wholesale_rate_per_kwh,
            }
            for p in tou_params_list
        ]

        # Get fixed_charge_per_kw from selected_policy table for TOU
        policy_details = self._selected_policy_repository.read_or_none(
            simulation_run_id
        )
        if policy_details:
            policy_specific_params["fixed_charge_per_kw"] = getattr(
                policy_details, "fixed_charge_tariff_rate_per_kw", 0.0
            )
        else:
            logger.warning(
                f"SelectedPolicy for run {simulation_run_id} not found when fetching fixed_charge for TOU. Defaulting to 0.0"
            )
            policy_specific_params["fixed_charge_per_kw"] = 0.0

        policy_specific_params.update(common_params)
        logger.info(f"Constructed TOU Rate config: {policy_specific_params}")
        return policy_specific_params

    def store_bill_details(
        self,
        run_id: UUID,
        house_node_id: str,
        bill_details: Dict[str, Any],
        house_bill_service: IService,
    ) -> None:
        """
        Stores the calculated bill details for TOU Rate.
        """
        logger.info(
            f"Storing TOU bill for house {house_node_id} under run {run_id}"
        )
        if not house_bill_service:
            logger.error(
                "house_bill_service not provided to TimeOfUseRateStrategy store_bill_details"
            )
            raise ValueError(
                "house_bill_service is required for storing bill details."
            )

        # For TOU, the main totals are named differently in bill_details
        actual_total_imported = bill_details.get(
            "overall_total_imported_kwh", 0.0
        )
        actual_total_exported = bill_details.get(
            "overall_total_exported_kwh", 0.0
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

        try:
            house_bill_service.create(user_id=None, **house_bill_record)
            logger.info(
                f"Successfully stored bill for house {house_node_id}"
                f" via TimeOfUseRateStrategy."
            )
        except Exception as e:
            logger.error(
                f"  Error storing bill for house {house_node_id}"
                f"via TimeOfUseRateStrategy: {e}"
            )
            raise
