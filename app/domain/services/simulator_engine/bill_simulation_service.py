"""
Module for simulating bills based on energy consumption and generation data.
"""

import datetime
from datetime import date
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
from app.exceptions.hygge_exceptions import NotFoundException
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
        gross_metering_policy_repo: IRepository,
        tou_rate_policy_params_repository: IRepository,
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
        self._gross_metering_policy_repo = gross_metering_policy_repo
        self._tou_rate_policy_params_repo = tou_rate_policy_params_repository
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
        elif (
            policy.net_metering_policy_type_id.policy_code == "GROSS_METERING"
        ):
            params = self._gross_metering_policy_repo.read_or_none(
                simulation_run_id
            )

            if not params:
                logger.warning(
                    f"GrossMeteringPolicy (params) for run id "
                    f"{simulation_run_id} not found."
                )
                return None

            return {
                "simulation_run_id": sim_run.id,
                "billing_cycle_month": sim_run.billing_cycle_month,
                "billing_cycle_year": sim_run.billing_cycle_year,
                "topology_root_node_id": sim_run.topology_root_node_id_id,
                "policy_type": "GROSS_METERING",
                "import_retail_price_kwh": params.import_retail_price_per_kwh,
                "exp_whole_price_kwh": params.export_wholesale_price_per_kwh,
                "fixed_charge_per_kw": params.fixed_charge_tariff_rate_per_kw,
                "fac_charge_per_kwh": policy.fac_charge_per_kwh_imported,
                "tax_rate": policy.tax_rate_on_energy_charges,
            }
        elif policy.net_metering_policy_type_id.policy_code == "TOU_RATE":
            # Fetch all TOU periods for this simulation run
            tou_params_list = self._tou_rate_policy_params_repo.filter(
                simulation_run_id=simulation_run_id
            )

            if not tou_params_list:
                logger.warning(
                    f"TimeOfUseRatePolicy (params) for run id "
                    f"{simulation_run_id} not found."
                )
                return None

            tou_periods_config = [
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
            fixed_charge_per_kw = (
                0.0  # todo pending we dont have it from designs
            )
            return {
                "simulation_run_id": sim_run.id,
                "billing_cycle_month": sim_run.billing_cycle_month,
                "billing_cycle_year": sim_run.billing_cycle_year,
                "topology_root_node_id": sim_run.topology_root_node_id_id,
                "policy_type": "TOU_RATE",
                "tou_periods": tou_periods_config,
                "fixed_charge_per_kw": fixed_charge_per_kw,
                "fac_charge_per_kwh": policy.fac_charge_per_kwh_imported,
                "tax_rate": policy.tax_rate_on_energy_charges,
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

            try:
                start_of_billing_month = datetime.date(
                    billing_year, billing_month, 1
                )
                if billing_month == 12:
                    end_of_billing_month = datetime.date(
                        billing_year, billing_month, 31
                    )
                else:
                    end_of_billing_month = datetime.date(
                        billing_year, billing_month + 1, 1
                    ) - datetime.timedelta(days=1)
            except ValueError as ve:
                logger.error(
                    f"Invalid billing_month/billing_year: {billing_month}/{billing_year}. Error: {ve}"
                )
                continue  # Skip this house if date is invalid

            energy_summary = self._get_house_energy_summary_for_period(
                house_entity, start_of_billing_month, end_of_billing_month
            )
            total_imported_units = energy_summary["total_imported_units"]
            total_exported_units = energy_summary["total_exported_units"]

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

            elif config.get("policy_type") == "GROSS_METERING":
                logger.info(
                    f"  Calculating bill for house {house_node_id} "
                    f"under GROSS_METERING policy..."
                )

                import_retail_price = config["import_retail_price_kwh"]
                export_wholesale_price = config["exp_whole_price_kwh"]

                imported_energy_charges = (
                    total_imported_units * import_retail_price
                )
                exported_energy_credit = (
                    total_exported_units * export_wholesale_price
                )

                fixed_charges = 0.0
                if config.get("fixed_charge_per_kw") is not None:
                    fixed_charges = (
                        config["fixed_charge_per_kw"] * sanctioned_load_kw
                    )

                fac_charges = (
                    total_imported_units * config["fac_charge_per_kwh"]
                )

                tax_amount = 0.0
                # Tax is typically on net positive energy charges
                # or total imported
                # Assuming tax on imported energy charges for gross metering
                if imported_energy_charges > 0:
                    tax_amount = imported_energy_charges * config["tax_rate"]

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
                    "imported_energy_charges": round(
                        imported_energy_charges, 2
                    ),
                    "exported_energy_credit": round(exported_energy_credit, 2),
                    "fixed_charge_per_kw": config.get("fixed_charge_per_kw"),
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

            elif config.get("policy_type") == "TOU_RATE":
                logger.info(
                    f"  Calculating bill for house {house_node_id} "
                    f"under TOU_RATE policy..."
                )

                tou_periods_config = config["tou_periods"]
                overall_total_imported_units = 0.0
                overall_total_exported_units = 0.0
                tou_energy_data_details = []  # For bill_details

                total_energy_charges_tou = 0.0
                total_export_credit_tou = 0.0

                for period_config in tou_periods_config:
                    period_label = period_config["time_period_label"]
                    start_time: datetime.time = period_config["start_time"]
                    end_time: datetime.time = period_config["end_time"]
                    import_rate = period_config["import_retail_rate_per_kwh"]
                    export_rate = period_config["exp_whole_rate_per_kwh"]

                    current_period_imported_kwh = 0.0
                    current_period_exported_kwh = 0.0

                    for i, ts in enumerate(timestamps):
                        # Ensure we are in the correct billing month and year
                        # skipping year validation until Shashwat responds
                        if not (ts.month == billing_month):
                            continue

                        interval_time = ts.time()
                    # Handle overnight periods (e.g., 22:00 to 06:00)
                    if (
                        start_time <= end_time
                    ):  # Normal period (e.g. 08:00 to 17:00)
                        if start_time <= interval_time < end_time:
                            current_period_imported_kwh += imported_intervals[
                                i
                            ]
                            current_period_exported_kwh += exported_intervals[
                                i
                            ]
                    else:  # Overnight period (e.g. 22:00 to 06:00)
                        if (
                            interval_time >= start_time
                            or interval_time < end_time
                        ):
                            current_period_imported_kwh += imported_intervals[
                                i
                            ]
                            current_period_exported_kwh += exported_intervals[
                                i
                            ]

                    overall_total_imported_units += current_period_imported_kwh
                    overall_total_exported_units += current_period_exported_kwh

                    import_cost_period = (
                        current_period_imported_kwh * import_rate
                    )
                    export_credit_period = (
                        current_period_exported_kwh * export_rate
                    )

                    total_energy_charges_tou += import_cost_period
                    total_export_credit_tou += export_credit_period

                    tou_energy_data_details.append(
                        {
                            "period_label": period_label,
                            "start_time": start_time.isoformat(),
                            "end_time": end_time.isoformat(),
                            "imported_kwh": round(
                                current_period_imported_kwh, 2
                            ),
                            "exported_kwh": round(
                                current_period_exported_kwh, 2
                            ),
                            "import_rate_per_kwh": import_rate,
                            "export_rate_per_kwh": export_rate,
                            "import_cost_period": round(import_cost_period, 2),
                            "export_credit_period": round(
                                export_credit_period, 2
                            ),
                        }
                    )

                fixed_charges = 0.0
                if config.get("fixed_charge_per_kw") is not None:
                    fixed_charges = (
                        config["fixed_charge_per_kw"] * sanctioned_load_kw
                    )
                else:  # PENDING: Hardcode if not available,
                    logger.warning(
                        "fixed_charge_per_kw not in config for TOU. Using 0.0"
                    )

                fac_charges = (
                    overall_total_imported_units * config["fac_charge_per_kwh"]
                )

                tax_amount = 0.0
                if total_energy_charges_tou > 0:
                    tax_amount = total_energy_charges_tou * config["tax_rate"]

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
                    "fixed_charge_per_kw": config.get(
                        "fixed_charge_per_kw"
                    ),  # PENDING: May be None
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
                logger.info(f"  Calculated TOU Bill Details: {bill_details}")

            else:
                logger.warning(
                    f"  Policy {config.get('policy_type')} not yet supported "
                    f"for house {house_node_id}."
                )
                continue

            try:
                # Common structure for house_bill_record
                # For TOU, use overall imported/exported
                net_balance_kwh_val = 0.0  # Initialize with a float
                if config.get("policy_type") == "TOU_RATE":
                    net_balance_kwh_val = round(
                        overall_total_imported_units
                        - overall_total_exported_units,
                        2,  # type: ignore
                    )
                else:  # For SIMPLE_NET and GROSS_METERING
                    net_balance_kwh_val = round(
                        total_imported_units - total_exported_units, 2
                    )

                house_bill_record = {
                    "simulation_run_id": run_id,
                    "house_node_id": house_node_id,
                    "total_energy_imported_kwh": (
                        bill_details.get("total_imported_kwh")
                        if config.get("policy_type") != "TOU_RATE"
                        else bill_details.get("overall_total_imported_kwh")
                    ),
                    "total_energy_exported_kwh": (
                        bill_details.get("total_exported_kwh")
                        if config.get("policy_type") != "TOU_RATE"
                        else bill_details.get("overall_total_exported_kwh")
                    ),
                    "net_energy_balance_kwh": net_balance_kwh_val,
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

    def _get_house_energy_summary_for_period(
        self,
        house_entity: Node,
        start_date: date,
        end_date: date,
    ) -> Dict[str, float]:
        """
        Aggregates total imported and exported energy for a specific house
        over a given date range.

        Args:
            house_entity: The Node object representing the house.
            start_date: The start date of the period (inclusive).
            end_date: The end date of the period (inclusive).

        Returns:
            A dictionary with "total_imported_units" and
            "total_exported_units".
            Returns {"total_imported_units": 0.0, "total_exported_units": 0.0}
            if data is not found or an error occurs.
        """
        start_date = start_date.replace(year=2023)
        end_date = end_date.replace(year=2023)
        house_node_id = str(house_entity.id)
        logger.debug(
            f"Fetching 15-min interval data for house {house_node_id} "
            f"for period {start_date} to {end_date}..."
        )

        try:
            house_profile: HouseProfile | None = (
                self._data_preparation_service.get_house_profile(
                    house=house_entity
                )
            )
        except Exception as e:
            logger.error(
                f"Error getting profile for house {house_node_id}: {e}"
            )
            return {
                "total_imported_units": 0.0,
                "total_exported_units": 0.0,
            }

        if not house_profile:
            logger.error(
                f"Error getting HouseProfile for house {house_node_id}."
            )
            return {
                "total_imported_units": 0.0,
                "total_exported_units": 0.0,
            }

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
                f"Data mismatch in lengths for house {house_node_id}."
            )
            return {
                "total_imported_units": 0.0,
                "total_exported_units": 0.0,
            }

        for i, ts_datetime in enumerate(timestamps):
            ts_date = (
                ts_datetime.date()
            )  # Convert timestamp to date for comparison
            if start_date <= ts_date < end_date:
                total_imported_units += imported_intervals[i]
                total_exported_units += exported_intervals[i]

        logger.debug(
            f"Aggregated for period {start_date} to {end_date} for house {house_node_id} - "
            f"Total Imported: {total_imported_units:.2f} kWh, "
            f"Total Exported: {total_exported_units:.2f} kWh"
        )
        return {
            "total_imported_units": round(total_imported_units, 2),
            "total_exported_units": round(total_exported_units, 2),
        }

    def get_house_energy_summary(
        self, house_id: UUID, start_date: date, end_date: date
    ) -> Dict[str, float]:
        """
        Provides total imported and exported units for a specific house
        for a given date range.

        Args:
            house_id: The UUID of the house.
            start_date: The start date of the period.
            end_date: The end date of the period.

        Returns:
            A dictionary with "total_imported_units" and
            "total_exported_units".

        Raises:
            NotFoundException: If the house is not found.
        """
        logger.info(
            f"Getting energy summary for house {house_id} "
            f"for period {start_date} to {end_date}."
        )
        house_entity = self._net_topology_service.get_node_by_id(house_id)
        if not house_entity or house_entity.node_type != "HOUSE":
            raise NotFoundException(f"House with id {house_id} not found.")

        return self._get_house_energy_summary_for_period(
            house_entity, start_date, end_date
        )

    def get_node_energy_summary(
        self, node_id: UUID, start_date: date, end_date: date
    ) -> Dict[str, float]:
        """
        Provides total imported and exported units for all houses under a
        specific node (e.g., transformer, substation, or a house itself)
        for a given date range.

        Args:
            node_id: The UUID of the node.
            start_date: The start date of the period.
            end_date: The end date of the period.

        Returns:
            A dictionary with "total_imported_units" and
            "total_exported_units" aggregated for all houses under the node.

        Raises:
            NotFoundException: If the node is not found.
        """
        logger.info(
            f"Getting energy summary for node {node_id} and its children "
            f"for period {start_date} to {end_date}."
        )
        node_entity = self._net_topology_service.get_node_by_id(node_id)
        if not node_entity:
            raise NotFoundException(f"Node with id {node_id} not found.")

        total_imported_for_node = 0.0
        total_exported_for_node = 0.0

        if node_entity.node_type == "HOUSE":
            summary = self._get_house_energy_summary_for_period(
                node_entity, start_date, end_date
            )
            total_imported_for_node = summary["total_imported_units"]
            total_exported_for_node = summary["total_exported_units"]
        else:
            # For transformers or substations, get all descendant houses
            houses_under_node: List[Node] = (
                self._net_topology_service.get_houses_by_parent_node_id(
                    node_id
                )
            )
            if (
                not houses_under_node
            ):  # if it's a substation, use the other method
                if node_entity.node_type == "SUBSTATION":
                    houses_under_node = (
                        self._net_topology_service.get_houses_by_substation_id(
                            node_id
                        )
                    )
                else:  # if not substation and no children houses, it might be an empty transformer
                    logger.warning(
                        f"No houses found under non-house node {node_id}"
                    )

            for house_entity in houses_under_node:
                summary = self._get_house_energy_summary_for_period(
                    house_entity, start_date, end_date
                )
                total_imported_for_node += summary["total_imported_units"]
                total_exported_for_node += summary["total_exported_units"]

        return {
            "total_imported_units": round(total_imported_for_node, 2),
            "total_exported_units": round(total_exported_for_node, 2),
        }


"""
TODO:
- Implement detailed bill calculation logic for "Simple Net Metering"
  (Phase 1, Step 4).
- Implement logic to store bill results (Phase 1, Step 5).
- Implement logic to update simulation_runs status (Phase 1, Step 6).
- Add comprehensive error handling and logging.
- Add unit tests.
- Verify/add `get_houses_by_parent_node_id` in INetTopologyService and its implementation.
"""
