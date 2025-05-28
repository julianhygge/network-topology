# Bill Simulation Engine Workflow

This document outlines the steps required to implement the bill simulation engine.

## Phase 0: Data Preparation and Foundational Setup

### 1. 15-Minute Interval Data Generation
   - **Description:** Generate a CSV per house with 15-minute interval data for a year: Load (kWh), Solar Generation (kWh). From this, calculate Net_Energy_Interval (kWh) = Load - Solar_Generation. Also calculate Import_Interval (kWh) = MAX(0, Net_Energy_Interval) and Export_Interval (kWh) = MAX(0, -Net_Energy_Interval). This data is the fundamental input for bill calculation.
   - **Status:** Partially Implemented.
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
   - **Status:** To Be Implemented by Coworker.
   - **Comments/Questions:**
     - These services will be essential for configuring simulations and storing their parameters.
     - The bill calculation engine will rely on these services to fetch configuration data.
     - Entity models for these tables need to be defined in `api/app/domain/entities/` before the bill calculation service can effectively use them.

## Phase 1: Implement Bill Calculation for "Simple Net Metering" Policy

   - **Input:** `simulation_run_id` for a run configured with 'SIMPLE_NET' policy.

### 1. Fetch Simulation Configuration
   - **Description:** Given `simulation_run_id`:
     - Read the `simulation_runs` record. Get `billing_cycle_month`, `billing_cycle_year`, `topology_root_node_id`.
     - Read the `simulation_selected_policies` record. Get `net_metering_policy_type_id`, `fixed_charge_tariff_rate_per_kw`, `fac_charge_per_kwh_imported`, `tax_rate_on_energy_charges`.
     - Confirm `net_metering_policy_type_id` corresponds to 'SIMPLE_NET' in `master.net_metering_policy_types`.
     - Read the `net_metering_policy_params` record. Get `retail_price_per_kwh`.
   - **Status:** Not Started.
   - **Comments/Questions:**
     - Depends on CRUD services from Phase 0.
     - Mock data or direct DB access can be used for initial development if CRUD services are not ready.

### 2. Iterate Through Houses in the Topology
   - **Description:** Identify all `transactional.houses` that belong to the `topology_root_node_id`. For each `house_node_id`:
     - Fetch `Sanctioned_Load_kW` for the house (from `transactional.houses.connection_kw`).
   - **Status:** Not Started.
   - **Comments/Questions:**
     - The `DataPreparationService` already has `get_houses_profile_by_substation_id` which uses `_topology_service.get_houses_by_substation_id`. This can be adapted.
     - Need to confirm how `Sanctioned_Load_kW` is reliably fetched. `transactional.houses.connection_kw` seems correct.

### 3. Aggregate Energy Data for the Billing Cycle for Each House
   - **Description:** For the current house and the `billing_cycle_month/year`:
     - `Total_Imported_Units` (kWh) = Sum of `Import_Interval` over all 15-min intervals in the billing cycle.
     - `Total_Exported_Units` (kWh) = Sum of `Export_Interval` over all 15-min intervals in the billing cycle.
   - **Status:** Not Started.
   - **Comments/Questions:**
     - The 15-minute interval data from Phase 0 (`HouseProfile` object from `DataPreparationService`) will be the input here.
     - Logic will be needed to filter/sum data for the specific `billing_cycle_month` and `billing_cycle_year`.

### 4. Calculate Bill Components for "Simple Net Metering" for Each House
   - **Description:**
     - `Net_Usage` (kWh) = `Total_Imported_Units` - `Total_Exported_Units`.
     - `Retail_Rate` = `retail_price_per_kwh`.
     - `Energy_Charges` (₹):
       - If `Net_Usage` > 0, then `Energy_Charges` = `Net_Usage` * `Retail_Rate`.
       - If `Net_Usage` <= 0, then `Energy_Charges` = 0.
     - `Credit_Amount_calc` (₹): If `Net_Usage` < 0, `Credit_Amount_calc` = `abs(Net_Usage)` * `Retail_Rate`. (This part is pending for future iteration).
     - `Fixed_Charges` (₹) = `fixed_charge_tariff_rate_per_kw` * `Sanctioned_Load_kW`.
     - `FAC_Charges` (₹) = `Total_Imported_Units` * `fac_charge_per_kwh_imported`.
     - `Tax_Amount` (₹): If `Energy_Charges` > 0, `Tax_Amount` = `Energy_Charges` * `tax_rate_on_energy_charges`. Else, `Tax_Amount` = 0.
     - `Arrears` (₹): Assume 0 for now (Skipped for now as per user feedback).
     - `Total_Bill_Amount` (₹) = `Energy_Charges` + `Fixed_Charges` + `FAC_Charges` + `Tax_Amount` - `Arrears`. *(Initial implementation will not subtract `Credit_Amount_calc` from the total bill)*.
       *(Revised based on "Crucial Check for Bill 1" and user feedback)*
   - **Status:** Not Started.
   - **Comments/Questions:**
     - **Credit Handling (User Feedback):** Pending for future iteration. The initial implementation will not include `Credit_Amount_calc` or its application to reduce other charges. Energy Charges will be 0 if Net Usage <= 0.
     - If `Net_Usage` <= 0, `Energy_Charges` are 0, and `Tax_Amount` on energy charges is 0.

### 5. Store Bill Results for Each House
   - **Description:** For each house, create a record in `simulation_engine.house_bills`:
     - `simulation_run_id`
     - `house_node_id`
     - `total_energy_imported_kwh` = `Total_Imported_Units`
     - `total_energy_exported_kwh` = `Total_Exported_Units`
     - `net_energy_balance_kwh` = `Net_Usage`
     - `calculated_bill_amount` = `Total_Bill_Amount`
     - `bill_details` (JSONB): Store all intermediate calculated values as specified.
   - **Status:** Not Started.
   - **Comments/Questions:**
     - Depends on CRUD service for `house_bills`.
     - The JSONB structure for `bill_details` needs to be finalized to ensure it captures all necessary information for display and debugging. The example provided is a good start.

### 6. Update `simulation_runs` Status
   - **Description:** Set status to 'COMPLETED' (or 'FAILED' if errors occur). Set `simulation_end_timestamp`.
   - **Status:** Not Started.
   - **Comments/Questions:**
     - Depends on CRUD service for `simulation_runs`.

## Phase 2: Implement Bill Calculation for "Gross Metering" Policy

   - **Input:** `simulation_run_id` for a run configured with 'GROSS_METERING' policy.

### 1. Fetch Simulation Configuration
   - **Description:** Similar to Simple Net Metering, but:
     - Confirm policy is 'GROSS_METERING'.
     - Read `gross_metering_policy_params`. Get `import_retail_price_per_kwh` and `export_wholesale_price_per_kwh`.
     - Fetch `fixed_charge_tariff_rate_per_kw`, `fac_charge_per_kwh_imported`, `tax_rate_on_energy_charges` from `simulation_selected_policies`.
   - **Status:** Not Started.
   - **Comments/Questions:**
     - Depends on CRUD services.

### 2. Iterate Through Houses & Aggregate Energy Data
   - **Description:** Same as step 2 & 3 in Phase 1.
     - Identify houses, fetch `Sanctioned_Load_kW`.
     - Aggregate `Total_Imported_Units` and `Total_Exported_Units` for the billing cycle.
   - **Status:** Not Started (but logic can be reused from Phase 1).

### 3. Calculate Bill Components for "Gross Metering" for Each House
   - **Description:**
     - `Import_Retail_Rate` = `import_retail_price_per_kwh`.
     - `Export_Wholesale_Rate` = `export_wholesale_price_per_kwh`.
     - `Cost_of_Import` (₹) = `Total_Imported_Units` * `Import_Retail_Rate`.
     - `Revenue_from_Export` (₹) = `Total_Exported_Units` * `Export_Wholesale_Rate`.
     - `Fixed_Charges` (₹) = `fixed_charge_tariff_rate_per_kw` * `Sanctioned_Load_kW`.
     - `FAC_Charges` (₹) = `Total_Imported_Units` * `fac_charge_per_kwh_imported`.
     - `Tax_Amount` (₹) = `Cost_of_Import` * `tax_rate_on_energy_charges`.
     - `Arrears` (₹): Assume 0 for now.
     - `Total_Bill_Amount` (₹) = `Cost_of_Import` + `Fixed_Charges` + `FAC_Charges` + `Tax_Amount` - `Revenue_from_Export` - `Arrears`.
   - **Status:** Not Started.

### 4. Store Bill Results for Each House
   - **Description:** Create a record in `simulation_engine.house_bills`.
     - `bill_details` (JSONB): Store intermediate values as specified for "GROSS_METERING".
   - **Status:** Not Started.
   - **Comments/Questions:**
     - JSONB structure for `bill_details` needs to be adapted for Gross Metering.

### 5. Update `simulation_runs` Status
   - **Description:** Same as Phase 1.
   - **Status:** Not Started.

## Phase 3: Implement Bill Calculation for "Time of Use (TOU) Rate Metering" Policy

   - **Input:** `simulation_run_id` for a run configured with 'TOU_RATE' policy.

### 1. Fetch Simulation Configuration
   - **Description:** Similar to other policies, but:
     - Confirm policy is 'TOU_RATE'.
     - Read all associated records from `tou_rate_policy_params` for this `simulation_run_id`. This gives a list of TOU periods (label, start_time, end_time, import_retail_rate_per_kwh, export_wholesale_rate_per_kwh).
     - Fetch `fixed_charge_tariff_rate_per_kw`, `fac_charge_per_kwh_imported`, `tax_rate_on_energy_charges` from `simulation_selected_policies`.
   - **Status:** Not Started.
   - **Comments/Questions:**
     - Handling multiple TOU periods per simulation run is key.

### 2. Iterate Through Houses
   - **Description:** Same as step 2 in Phase 1.
   - **Status:** Not Started (reuse logic).

### 3. Aggregate Energy Data Per TOU Period for the Billing Cycle for Each House
   - **Description:** For each house and for each defined TOU period:
     - Initialize `Total_Import_Period_X` (kWh) = 0, `Total_Export_Period_X` (kWh) = 0.
     - Iterate through all 15-minute intervals in the billing cycle.
     - Determine which TOU period each interval falls into.
     - Add interval's `Import_Interval` to `Total_Import_Period_X`.
     - Add interval's `Export_Interval` to `Total_Export_Period_X`.
     - Calculate `Overall_Total_Imported_Units` (kWh) for FAC calculation.
   - **Status:** Not Started.
   - **Comments/Questions:**
     - This is the most complex aggregation step. Requires careful mapping of 15-min interval timestamps to TOU periods.
     - **Timestamp Handling (User Feedback):** TOU `start_time` and `end_time` are local times for the grid/location zone. Interval data timestamps (from `DataPreparationService`) should be treated as local time for comparison. Ensure consistency in handling these local times.

### 4. Calculate Bill Components for "TOU Rate Metering" for Each House
   - **Description:**
     - `Total_Energy_Charges` (₹) = 0.
     - `Total_Export_Credit` (₹) = 0.
     - For each TOU period X:
       - `Import_Cost_Period_X` (₹) = `Total_Import_Period_X` * `import_retail_rate_per_kwh_Period_X`.
       - `Export_Credit_Period_X` (₹) = `Total_Export_Period_X` * `export_wholesale_rate_per_kwh_Period_X`. (If applicable)
       - `Total_Energy_Charges` += `Import_Cost_Period_X`.
       - `Total_Export_Credit` += `Export_Credit_Period_X`. (If applicable)
     - `Fixed_Charges` (₹) = `fixed_charge_tariff_rate_per_kw` * `Sanctioned_Load_kW`.
     - `FAC_Charges` (₹) = `Overall_Total_Imported_Units` * `fac_charge_per_kwh_imported`.
     - `Tax_Amount` (₹) = `Total_Energy_Charges` * `tax_rate_on_energy_charges`.
     - `Arrears` (₹): Assume 0.
     - `Total_Bill_Amount` (₹) = `Total_Energy_Charges` + `Fixed_Charges` + `FAC_Charges` + `Tax_Amount` - `Total_Export_Credit` - `Arrears`.
   - **Status:** Not Started.
   - **Comments/Questions:**
     - **TOU Export Compensation (User Feedback):** Pending - Awaiting confirmation from supervisor. The `tou_rate_policy_params` table includes `export_wholesale_rate_per_kwh`. For now, proceed assuming it might be needed but await final confirmation before full implementation.

### 5. Store Bill Results for Each House
   - **Description:** Create a record in `simulation_engine.house_bills`.
     - `total_energy_imported_kwh` = `Overall_Total_Imported_Units`.
     - `total_energy_exported_kwh` = Sum of exports across all periods.
     - `net_energy_balance_kwh` = `Overall_Total_Imported_Units` - Sum of exports.
     - `bill_details` (JSONB): Store intermediate values as specified for "TOU_RATE", including the breakdown per TOU period.
   - **Status:** Not Started.
   - **Comments/Questions:**
     - JSONB structure needs to accommodate the list of TOU period breakdowns.

### 6. Update `simulation_runs` Status
   - **Description:** Same as Phase 1.
   - **Status:** Not Started.

## General Implementation Notes:
- **Service Location:** The new bill calculation service will be created under `api/app/domain/services/simulator_engine/`.
- **Entity Models:** Define SQLAlchemy models for `simulation_engine.*` tables in `api/app/domain/entities/` (or a similar appropriate location for simulation-specific entities if they differ from general transactional/master entities).
- **Mocking:** For initial development, mock the CRUD operations for fetching simulation configurations if the actual services are not yet available.
- **Error Handling:** Implement robust error handling throughout the process. Update `simulation_runs.status` to 'FAILED' and log errors appropriately.
- **Database Transactions:** Ensure that storing multiple house bills and updating the simulation run status are handled within a database transaction for atomicity.
- **Configuration Management:** How will the bill calculation engine access database connection details and other configurations? (Presumably via the existing configuration setup in `app/config/`).
- **Testing:** Plan for unit tests for each policy calculation logic and integration tests for the end-to-end simulation run.

## Questions for Clarification:
1.  **Solar Site ID for `_get_solar_by_house_id` (User Feedback: Pending):** How should the correct `site_id` be determined dynamically for each house instead of the hardcoded `2609522`? (Continue with hardcoded value for now).
2.  **Timestamp/Time Zone Handling for TOU (User Feedback: Clarified):**
    - `tou_rate_policy_params` has `start_time` and `end_time` as `time without time zone` (local to grid zone).
    - Interval data from `DataPreparationService` (e.g., `load_patterns.timestamp`) should be treated as local time.
    - Ensure consistent handling of these local times for comparison.
3.  **TOU Export Compensation (User Feedback: Pending):** The `tou_rate_policy_params` table includes `export_wholesale_rate_per_kwh`. Should the TOU policy calculation include credits/revenue from exported energy? (Awaiting confirmation from supervisor).
4.  **Arrears (User Feedback: Skipped for now):** For now, arrears are assumed to be 0.
5.  **Definition of `transactional.houses.connection_kw` (Sanctioned Load) (User Feedback: Pending):** Is this field reliably populated? (To be hardcoded if necessary for now, awaiting confirmation from supervisor).
6.  **Net Metering Credit Application (User Feedback: Pending for future iteration):**
    - For the initial iteration, `Credit_Amount_calc` will not be implemented to reduce `Total_Bill_Amount`.
    - If `Net_Usage <= 0`: `Energy_Charges = 0`, `Tax_Amount_on_Energy = 0`.
    - `Total_Bill_Amount` (initial) = `Energy_Charges + Fixed_Charges + FAC_Charges + Tax_Amount - Arrears`.
    - The question of what happens if `Credit_Amount_calc > (Fixed_Charges + FAC_Charges)` (payout or carry-forward) is deferred.

This document should serve as a good starting point for tracking the development of the bill simulation engine.
