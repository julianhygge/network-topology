# Bill Simulation Engine Workflow

This document outlines the steps required to implement the bill simulation engine.

## Phase 0: Data Preparation and Foundational Setup

### 1. 15-Minute Interval Data Generation
   - **Description:** Generate a CSV per house with 15-minute interval data for a year: Load (kWh), Solar Generation (kWh). From this, calculate Net_Energy_Interval (kWh) = Load - Solar_Generation. Also calculate Import_Interval (kWh) = MAX(0, Net_Energy_Interval) and Export_Interval (kWh) = MAX(0, -Net_Energy_Interval). This data is the fundamental input for bill calculation.
   - **Status:**
     - [x] Partially Implemented.
   - **Comments/Questions:**
     - The `api/app/domain/services/simulator_engine/data_preparation_service.py` (`get_house_profile` method) already calculates these values:
       - `load_values` corresponds to Load (kWh).
       - `solar_values` corresponds to Solar Generation (kWh).
       - `net_usage` (in `HouseProfile`) corresponds to Net_Energy_Interval (Load - Solar).
       - `imported_units` corresponds to Import_Interval.
       - `exported_units` corresponds to Export_Interval.
     - The service can generate CSVs per house and a ZIP archive of these CSVs.
     - **TODO/Question:** The `_get_solar_by_house_id` method currently uses a hardcoded `site_id=2609522` for fetching solar reference data. This needs to be made dynamic based on house location or configuration for accurate solar generation data. **Status (User Feedback):** Pending - Continue with hardcoded value for now.

### 2. CRUD Operations (Coworker's Task)
   - **Description:** Your coworker creates APIs/services to:
     - Create/Read/Update/Delete `simulation_engine.simulation_runs`.
     - Create/Read/Update/Delete `simulation_engine.simulation_selected_policies` (when algorithm is Net Metering).
     - Create/Read/Update/Delete `simulation_engine.net_metering_policy_params`.
     - Create/Read/Update/Delete `simulation_engine.gross_metering_policy_params`.
     - Create/Read/Update/Delete `simulation_engine.tou_rate_policy_params` (allowing multiple entries per simulation run).
     - (CRUD for `simulation_engine.house_bills` will primarily be Create from your engine and Read for display).
   - **Status:**
     - [x] Dependencies Assumed: The `BillSimulationService` is implemented assuming these CRUD operations (or their interfaces/repositories) are available. The service code injects repositories for `simulation_runs`, `selected_policies`, `net_metering_policy_params`, and a service for `house_bills`.
   - **Comments/Questions:**
     - These services/repositories are essential for configuring simulations and storing their parameters.
     - The bill calculation engine relies on these to fetch configuration data and store results.
     - Entity models for these tables need to be defined and accessible.

## Phase 1: Implement Bill Calculation for "Simple Net Metering" Policy

   - **Input:** `simulation_run_id` for a run configured with 'SIMPLE_NET' policy.

### Net Metering Bill Examples:

```
Net Metering: A billing mechanism where the electricity imported from the grid is offset by the electricity exported to the grid. Consumers are billed only for their net usage: Imported Units - Exported Units. If exported units exceed imports, the consumer may receive a credit or payout.

Bill 1: Import < Export
Consumer Name: M M RAMANAND
Billing Period: 01-Apr-2025 to 01-May-2025
Sanctioned Load (kW): 15
Tariff Rate: 210
Imported Units: 142
Exported Units: 643
Net Usage: -501
Retail Rate (₹/unit): 6
Energy Charges: 0
Fixed Charges: 3150
FAC (Fuel Adjustment Charges): 0
Tax (on 9% of energy charge): 0
Arrears (Credit from previous month): 0
Total Bill Amount: 144

Bill 2: Import > Export
Consumer Name: M M RAMANAND
Billing Period: 01-May-2025 to 01-Jun-2025
Sanctioned Load (kW): 15
Tariff Rate: 210
Imported Units: 643
Exported Units: 142
Net Usage: 501
Retail Rate (₹/unit): 6
Energy Charges: 3006
Fixed Charges: 3150
FAC (Fuel Adjustment Charges): 0
Tax (on 9% of energy charge): 270.54
Arrears (Credit from previous month): 0
Total Bill Amount: 6426.54
```

### 1. Fetch Simulation Configuration
   - **Description:** Given `simulation_run_id`:
     - Read the `simulation_runs` record. Get `billing_cycle_month`, `billing_cycle_year`, `topology_root_node_id`.
     - Read the `simulation_selected_policies` record. Get `net_metering_policy_type_id`, `fixed_charge_tariff_rate_per_kw`, `fac_charge_per_kwh_imported`, `tax_rate_on_energy_charges`.
     - Confirm `net_metering_policy_type_id` corresponds to 'SIMPLE_NET' in `master.net_metering_policy_types`.
     - Read the `net_metering_policy_params` record. Get `retail_price_per_kwh`.
   - **Status:**
     - [x] Implemented in `BillSimulationService._fetch_simulation_configuration()`.
   - **Comments/Questions:**
     - The service method fetches and structures this data, including policy-specific parameters under a `policy_config` key.
     - Mock data or direct DB access can be used for initial development if CRUD services are not ready.

### 2. Iterate Through Houses in the Topology
   - **Description:** Identify all `transactional.houses` that belong to the `topology_root_node_id`. For each `house_node_id`:
     - Fetch `Sanctioned_Load_kW` for the house (from `transactional.houses.connection_kw`).
   - **Status:**
     - [x] Implemented in `BillSimulationService._get_houses_in_topology()` and usage in `calculate_bills_for_simulation_run()`.
   - **Comments/Questions:**
     - The service fetches houses and then accesses `connection_kw` or a default.
     - The `DataPreparationService` already has `get_houses_profile_by_substation_id` which uses `_topology_service.get_houses_by_substation_id`. This can be adapted.
     - Need to confirm how `Sanctioned_Load_kW` is reliably fetched. `transactional.houses.connection_kw` seems correct.

### 3. Aggregate Energy Data for the Billing Cycle for Each House
   - **Description:** For the current house and the `billing_cycle_month/year`:
     - `Total_Imported_Units` (kWh) = Sum of `Import_Interval` over all 15-min intervals in the billing cycle.
     - `Total_Exported_Units` (kWh) = Sum of `Export_Interval` over all 15-min intervals in the billing cycle.
     - **Important Note on Data Year and Timezone Handling:** The `_get_house_energy_summary_for_period` method in `BillSimulationService` currently uses `start_datetime.replace(year=2023)` and `end_datetime.replace(year=2023)`. This means that regardless of the `billing_cycle_year` set in the simulation run, the actual energy data for aggregation is always fetched from the year 2023. This is a critical assumption for interpreting simulation results. All datetime comparisons within this service (e.g., `start_dt_processed <= ts_datetime_val < end_dt_processed`) are performed using timezone-naive datetime objects, treating all datetimes as local time to avoid "can't compare offset-naive and offset-aware datetimes" errors.
     - For TOU policy, raw 15-minute interval data (`timestamps`, `imported_intervals`, `exported_intervals`) is also passed to its strategy, which then filters by the actual `billing_cycle_month` and `billing_cycle_year` from the simulation configuration.
   - **Status:**
     - [x] Implemented in `BillSimulationService.calculate_bills_for_simulation_run()` and `_get_house_energy_summary_for_period()`. The TOU strategy handles its own interval filtering.
   - **Comments/Questions:**
     - The 15-minute interval data from Phase 0 (`HouseProfile` object from `DataPreparationService`) is used as input.
     - The hardcoded year 2023 for data aggregation in `_get_house_energy_summary_for_period` is a deliberate choice based on current data availability.

### 4. Calculate Bill Components using Strategy Pattern
   - **Description:** The `BillSimulationService` now uses a Strategy pattern.
     - An `IBillingPolicyStrategy` interface defines `calculate_bill_components`.
     - Concrete strategies (`SimpleNetMeteringStrategy`, `GrossMeteringStrategy`, `TimeOfUseRateStrategy`) implement this interface.
     - `BillSimulationService` selects the appropriate strategy based on `policy_type` from the configuration.
     - The selected strategy calculates all bill components (Energy Charges, Fixed Charges, FAC, Tax, Total Bill).
     - **Simple Net Metering Calculation (handled by `SimpleNetMeteringStrategy`):**
       - `Net_Usage` (kWh) = `Total_Imported_Units` - `Total_Exported_Units`.
       - `Retail_Rate` = `policy_config["retail_price_per_kwh"]`.
       - `Energy_Charges` (₹): If `Net_Usage` > 0, then `Energy_Charges` = `Net_Usage` * `Retail_Rate`. Else 0.
       - `Fixed_Charges` (₹) = `policy_config["fixed_charge_per_kw"]` * `Sanctioned_Load_kW`.
       - `FAC_Charges` (₹) = `Total_Imported_Units` * `policy_config["fac_charge_per_kwh"]`.
       - `Tax_Amount` (₹): If `Energy_Charges` > 0, `Tax_Amount` = `Energy_Charges` * `policy_config["tax_rate"]`. Else 0.
       - `Arrears` (₹): Assume 0.
       - `Total_Bill_Amount` (₹) = `Energy_Charges` + `Fixed_Charges` + `FAC_Charges` + `Tax_Amount` - `Arrears`.
   - **Status:**
     - [x] Refactored to use Strategy Pattern. Calculation logic moved to respective strategy classes.
   - **Comments/Questions:**
     - **Credit Handling (User Feedback):** Remains pending for future iteration within strategies.
     - The `policy_config` dictionary passed to strategies contains all necessary rates and parameters.

### 5. Store Bill Results for Each House
   - **Description:** For each house, create a record in `simulation_engine.house_bills`:
     - `simulation_run_id`
     - `house_node_id`
     - `total_energy_imported_kwh` = Value from `bill_details` (e.g., `overall_total_imported_kwh` for TOU, `total_imported_kwh` for others).
     - `total_energy_exported_kwh` = Value from `bill_details`.
     - `net_energy_balance_kwh` = Calculated as `actual_total_imported - actual_total_exported`.
     - `calculated_bill_amount` = `bill_details["total_bill_amount_calculated"]`.
     - `bill_details` (JSONB): The complete dictionary returned by the billing strategy.
   - **Status:**
     - [x] Implemented in `BillSimulationService.calculate_bills_for_simulation_run()`. The service now correctly populates these fields using the `bill_details` from the strategy.
   - **Comments/Questions:**
     - The service calls `self._house_bill_service.create()` with the calculated bill record.
     - The `bill_details` dictionary returned by the strategy is stored directly.
     - The JSONB structure for `bill_details` is now determined by each strategy, ensuring all relevant calculation steps are captured.

### 6. Update `simulation_runs` Status
   - **Description:** Set status to 'COMPLETED' (or 'FAILED' if errors occur). Set `simulation_end_timestamp`.
   - **Status:**
     - [x] Implemented in `BillSimulationService.calculate_bills_for_simulation_run()`.
   - **Comments/Questions:**
     - The service updates the `simulation_runs` repository with a status (currently defaults to 'COMPLETED' with a TODO for better error state handling) and timestamps.

## Phase 2: Implement Bill Calculation for "Gross Metering" Policy

   - **Input:** `simulation_run_id` for a run configured with 'GROSS_METERING' policy.

### Gross Metering Bill Examples:

```
Gross Metering: A billing mechanism where the electricity imported from the grid and the electricity exported to the grid are treated as separate transactions. Consumers are billed for the total imported units at the retail rate, and are separately credited for all exported units at a fixed feed-in tariff. There is no offsetting between import and export. If export earnings are less than import charges, the consumer pays the difference.

Bill 1: Import < Export
Consumer Name: M M RAMANAND
Billing Period: 01-Apr-2025 to 01-May-2025
Sanctioned Load (kW): 15
Tariff Rate: 210
Imported Units: 500
Exported Units: 600
Retail Rate (₹/unit): 6
Feed-in Tariff (₹/unit): 3
Cost of Import (Retail): 3000
Revenue from Export (Wholesale): 1800
Fixed Charges: 3150
Tax (on 9% of Import Cost): 270
FAC: 0
Arrears: 0
Total Bill Amount: 4620

Bill 1: Import > Export
Consumer Name: M M RAMANAND
Billing Period: 01-May-2025 to 01-Jun-2025
Sanctioned Load (kW): 15
Tariff Rate: 210
Imported Units: 700
Exported Units: 400
Retail Rate (₹/unit): 6
Feed-in Tariff (₹/unit): 3
Cost of Import (Retail): 4200
Revenue from Export (Wholesale): 1200
Fixed Charges: 3150
Tax (on 9% of Import Cost): 378
FAC: 0
Arrears: 0
Total Bill Amount: 6528
```

### 1. Fetch Simulation Configuration
   - **Description:** Similar to Simple Net Metering, but:
     - Confirm policy is 'GROSS_METERING'.
     - Read `gross_metering_policy_params`. Get `import_retail_price_per_kwh` and `export_wholesale_price_per_kwh`.
     - Fetch `fixed_charge_tariff_rate_per_kw` (from `gross_metering_policy_params` via `policy_config`), `fac_charge_per_kwh_imported`, `tax_rate_on_energy_charges` (from `simulation_selected_policies` via `policy_config`).
   - **Status:**
     - [x] Implemented in `BillSimulationService._fetch_simulation_configuration()`.
   - **Comments/Questions:**
     - The method handles "GROSS_METERING" policy type and structures parameters into `policy_config`.

### 2. Iterate Through Houses & Aggregate Energy Data
   - **Description:** Same as step 2 & 3 in Phase 1.
     - Identify houses, fetch `Sanctioned_Load_kW`.
     - Aggregate `Total_Imported_Units` and `Total_Exported_Units` for the billing cycle (using 2023 data as noted above).
   - **Status:**
     - [x] Implemented (Logic reused from Phase 1 within `BillSimulationService.calculate_bills_for_simulation_run()`).

### 3. Calculate Bill Components for "Gross Metering" for Each House (Handled by `GrossMeteringStrategy`)
   - **Description:**
     - `Import_Retail_Rate` = `policy_config["import_retail_price_kwh"]`.
     - `Export_Wholesale_Rate` = `policy_config["exp_whole_price_kwh"]`.
     - `Imported_Energy_Charges` (₹) = `Total_Imported_Units` * `Import_Retail_Rate`.
     - `Exported_Energy_Credit` (₹) = `Total_Exported_Units` * `Export_Wholesale_Rate`.
     - `Fixed_Charges` (₹): Calculated if `policy_config["fixed_charge_per_kw"]` is available, as `policy_config["fixed_charge_per_kw"]` * `Sanctioned_Load_kW`.
     - `FAC_Charges` (₹) = `Total_Imported_Units` * `policy_config["fac_charge_per_kwh"]`.
     - `Tax_Amount` (₹): Calculated on `Imported_Energy_Charges` if > 0, as `Imported_Energy_Charges` * `policy_config["tax_rate"]`.
     - `Arrears` (₹): Assume 0.
     - `Total_Bill_Amount` (₹) = `Imported_Energy_Charges` + `Fixed_Charges` + `FAC_Charges` + `Tax_Amount` - `Exported_Energy_Credit` - `Arrears`.
   - **Status:**
     - [x] Implemented in `GrossMeteringStrategy.calculate_bill_components()`.
   - **Comments/Questions:**
     - The calculation logic is now encapsulated in the `GrossMeteringStrategy`.

### 4. Store Bill Results for Each House
   - **Description:** Create a record in `simulation_engine.house_bills`.
     - `bill_details` (JSONB): The dictionary returned by `GrossMeteringStrategy`.
   - **Status:**
     - [x] Implemented in `BillSimulationService.calculate_bills_for_simulation_run()`.
   - **Comments/Questions:**
     - The `bill_details` dictionary from the strategy is stored.
     - `net_energy_balance_kwh` in `house_bills` is populated as `actual_total_imported - actual_total_exported`.

### 5. Update `simulation_runs` Status
   - **Description:** Same as Phase 1.
   - **Status:**
     - [x] Implemented (Logic reused from Phase 1).

## Phase 3: Implement Bill Calculation for "Time of Use (TOU) Rate Metering" Policy

   - **Input:** `simulation_run_id` for a run configured with 'TOU_RATE' policy.
   - **Status:** [x] Implemented (Refactored to use `TimeOfUseRateStrategy`)

### Time-of-Use (TOU) Metering Bill Examples:

```
Time-of-Use (TOU) Metering: A billing mechanism where electricity usage is charged based on the time of day it is consumed. Peak, mid-peak, and off-peak hours have different rates to reflect grid demand.  Consumers are incentivized to use electricity during off-peak times to reduce their bills.

Bill 1:
Consumer Name: M M RAMANAND
Billing Period: 01-Apr-2025 to 01-May-2025
Sanctioned Load (kW): 15
Tariff Rate: 210
Peak Usage (units @ ₹8/unit): 120 at 8 Rs.
Mid-Peak Usage (units @ ₹6/unit): 150 at 6 Rs.
Off-Peak Usage (units @ ₹4/unit): 230 at 4 Rs.
Energy Charges: 2780
Fixed Charges: 3150
Tax (on 9% of Energy Charges): 250.2
FAC: 0
Arrears: 0
Total Bill Amount: 6180.2
```

### 1. Fetch Simulation Configuration
   - **Description:** Similar to other policies, but:
     - Confirm policy is 'TOU_RATE'.
     - Read all associated records from `tou_rate_policy_params` for this `simulation_run_id`. This gives a list of TOU periods (label, start_time, end_time, import_retail_rate_per_kwh, export_wholesale_rate_per_kwh).
     - Fetch `fixed_charge_tariff_rate_per_kw`, `fac_charge_per_kwh_imported`, `tax_rate_on_energy_charges` from `simulation_selected_policies` (via `policy_config`).
   - **Status:**
     - [x] Implemented in `BillSimulationService._fetch_simulation_configuration()`.
   - **Comments/Questions:**
     - The method fetches all `tou_rate_policy_params` and common parameters into `policy_config`.

### 2. Iterate Through Houses
   - **Description:** Same as step 2 in Phase 1.
   - **Status:**
     - [x] Implemented (Logic reused from Phase 1 within `BillSimulationService.calculate_bills_for_simulation_run()`).

### 3. Aggregate Energy Data Per TOU Period for the Billing Cycle for Each House (Handled by `TimeOfUseRateStrategy`)
   - **Description:** The `TimeOfUseRateStrategy` receives raw 15-minute interval data (`timestamps`, `imported_intervals`, `exported_intervals`) via `house_profile_data`.
     - It iterates through these intervals.
     - For each interval, it determines which TOU period it falls into based on `start_time` and `end_time` from `policy_config["tou_periods"]`.
     - It aggregates `Import_Interval` and `Export_Interval` for each TOU period.
     - It calculates `Overall_Total_Imported_Units` and `Overall_Total_Exported_Units`.
     - **Important:** The strategy filters data based on the actual `billing_cycle_month` and `billing_cycle_year` from the simulation configuration, ensuring correct data for the specified billing period is used for TOU calculations. The underlying 15-minute data itself is still sourced based on the 2023 hardcoding in `DataPreparationService` if that's where `get_house_profile` gets its base data.
   - **Status:**
     - [x] Implemented in `TimeOfUseRateStrategy.calculate_bill_components()`.
   - **Comments/Questions:**
     - Mapping of 15-min intervals to TOU periods is handled within the strategy.
     - Handles normal and overnight TOU periods.

### 4. Calculate Bill Components for "TOU Rate Metering" for Each House (Handled by `TimeOfUseRateStrategy`)
   - **Description:**
     - `Total_Energy_Charges` (₹) = 0.
     - `Total_Export_Credit` (₹) = 0.
     - For each TOU period X (from `policy_config["tou_periods"]`):
       - `Import_Cost_Period_X` (₹) = `Total_Import_Period_X` * `import_retail_rate_per_kwh_Period_X`.
       - `Export_Credit_Period_X` (₹) = `Total_Export_Period_X` * `export_wholesale_rate_per_kwh_Period_X`.
       - `Total_Energy_Charges` += `Import_Cost_Period_X`.
       - `Total_Export_Credit` += `Export_Credit_Period_X`.
     - `Fixed_Charges` (₹) = `policy_config["fixed_charge_per_kw"]` * `Sanctioned_Load_kW`.
     - `FAC_Charges` (₹) = `Overall_Total_Imported_Units` * `policy_config["fac_charge_per_kwh"]`.
     - `Tax_Amount` (₹) = `Total_Energy_Charges` * `policy_config["tax_rate"]`.
     - `Arrears` (₹): Assume 0.
     - `Total_Bill_Amount` (₹) = `Total_Energy_Charges` + `Fixed_Charges` + `FAC_Charges` + `Tax_Amount` - `Total_Export_Credit` - `Arrears`.
   - **Status:**
     - [x] Implemented in `TimeOfUseRateStrategy.calculate_bill_components()`.
   - **Comments/Questions:**
     - TOU Export Compensation is handled by the strategy.
     - `fixed_charge_per_kw` is used from `policy_config`.

### 5. Store Bill Results for Each House
   - **Description:** Create a record in `simulation_engine.house_bills`.
     - `total_energy_imported_kwh` = `bill_details["overall_total_imported_kwh"]`.
     - `total_energy_exported_kwh` = `bill_details["overall_total_exported_kwh"]`.
     - `net_energy_balance_kwh` = `actual_total_imported - actual_total_exported`.
     - `bill_details` (JSONB): The dictionary returned by `TimeOfUseRateStrategy`, including `tou_period_details`.
   - **Status:**
     - [x] Implemented in `BillSimulationService.calculate_bills_for_simulation_run()`.
   - **Comments/Questions:**
     - `bill_details` from the strategy is stored.

### 6. Update `simulation_runs` Status
   - **Description:** Same as Phase 1.
   - **Status:**
     - [x] Implemented (Logic reused from Phase 1).

## General Implementation Notes:
- [ ] **Service Location:** The new bill calculation service will be created under `api/app/domain/services/simulator_engine/`.
- [ ] **Entity Models:** Define SQLAlchemy models for `simulation_engine.*` tables in `api/app/domain/entities/` (or a similar appropriate location for simulation-specific entities if they differ from general transactional/master entities).
- [ ] **Mocking:** For initial development, mock the CRUD operations for fetching simulation configurations if the actual services are not yet available.
- [ ] **Error Handling:** Implement robust error handling throughout the process. Update `simulation_runs.status` to 'FAILED' and log errors appropriately.
- [ ] **Database Transactions:** Ensure that storing multiple house bills and updating the simulation run status are handled within a database transaction for atomicity.
- [ ] **Configuration Management:** How will the bill calculation engine access database connection details and other configurations? (Presumably via the existing configuration setup in `app/config/`).
- [ ] **Testing:** Plan for unit tests for each policy calculation logic and integration tests for the end-to-end simulation run.

## Questions for Clarification:
1.  - [ ] **Solar Site ID for `_get_solar_by_house_id` (User Feedback: Pending):** How should the correct `site_id` be determined dynamically for each house instead of the hardcoded `2609522`? (Continue with hardcoded value for now).
2.  - [x] **Timestamp/Time Zone Handling for TOU (User Feedback: Clarified and Implemented):**
    - `tou_rate_policy_params` has `start_time` and `end_time` as `time without time zone` (local to grid zone).
    - Interval data from `DataPreparationService` (e.g., `load_patterns.timestamp`) is treated as local time.
    - Consistent handling of these local times for comparison is ensured by converting all datetimes to timezone-naive objects before comparison in `EnergySummaryService`.
3.  - [ ] **TOU Export Compensation (User Feedback: Pending):** The `tou_rate_policy_params` table includes `export_wholesale_rate_per_kwh`. Should the TOU policy calculation include credits/revenue from exported energy? (Awaiting confirmation from supervisor).
4.  - [ ] **Arrears (User Feedback: Skipped for now):** For now, arrears are assumed to be 0.
5.  - [ ] **Definition of `transactional.houses.connection_kw` (Sanctioned Load) (User Feedback: Pending):** Is this field reliably populated? (To be hardcoded if necessary for now, awaiting confirmation from supervisor).
6.  - [ ] **Net Metering Credit Application (User Feedback: Pending for future iteration):**
    - For the initial iteration, `Credit_Amount_calc` will not be implemented to reduce `Total_Bill_Amount`.
    - If `Net_Usage <= 0`: `Energy_Charges = 0`, `Tax_Amount_on_Energy = 0`.
    - `Total_Bill_Amount` (initial) = `Energy_Charges + Fixed_Charges + FAC_Charges + Tax_Amount - Arrears`.
    - The question of what happens if `Credit_Amount_calc > (Fixed_Charges + FAC_Charges)` (payout or carry-forward) is deferred.

This document should serve as a good starting point for tracking the development of the bill simulation engine.
