"""
Concrete strategy for Time of Use (TOU) Rate policy.
"""

import datetime
from typing import Any, Dict, List

from app.domain.services.simulator_engine.billing_strategies.i_billing_policy_strategy import (
    IBillingPolicyStrategy,
)
from app.utils.logger import logger


class TimeOfUseRateStrategy(IBillingPolicyStrategy):
    """
    Implements billing calculations for Time of Use (TOU) Rate.
    """

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
            f"  Calculating bill for house {house_node_id} using TimeOfUseRateStrategy..."
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
