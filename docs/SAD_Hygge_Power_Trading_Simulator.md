# Business Requirements Document (BRD)
## Hygge Power Trading Simulator

**Version:** 0.1
**Date:** 29/April/2025 *(Note: Date seems inconsistent with SAD date, using as provided)*

# 1. Introduction

This document outlines the business requirements for the Hygge Power Trading Simulator. The simulator is designed to model and analyze the behavior of local energy communities (microgrids) comprising consumers, prosumers (with solar, batteries, etc.), and potentially other distributed energy resources like EVs. The primary purpose is to simulate energy generation, consumption, and sharing within these communities over time to understand energy flows, optimize distribution based on configurable priorities, assess the impact of different configurations, and evaluate potential benefits like increased self-consumption or cost savings (in future iterations).

# 2. Business Goals & Objectives

**Goal 1:** Provide a tool to accurately simulate energy flows within defined microgrid topologies.
*   **Objective 1.1:** Model energy consumption (load profiles) for various node types.
*   **Objective 1.2:** Model energy generation from solar PV.
*   **Objective 1.3:** Model energy storage and retrieval from battery systems.
*   **Objective 1.4:** Model energy demand from EV charging.

**Goal 2:** Enable analysis of different energy allocation and sharing strategies.
*   **Objective 2.1:** Implement configurable priority-based energy allocation logic for excess energy.
*   **Objective 2.2:** Simulate energy sharing within the same transformer community and between different communities within a grid.
*   **Objective 2.3:** Model energy losses during distribution/transformation.
*   **Objective 2.4:** Model interaction (import/export) with the main utility grid.

**Goal 3:** Facilitate comparison of different system configurations and scenarios.
*   **Objective 3.1:** Allow users to define and save complex topologies and node configurations.
*   **Objective 3.2:** Enable running multiple simulations with varying parameters on the same topology.
*   **Objective 3.3:** Provide clear visualization and reporting of simulation results.
*   **Objective 3.4:** Calculate key performance indicators (KPIs) like self-consumption, peak load reduction, and internal energy sharing volumes.

# 3. Scope

**In Scope:**

*   User authentication and role-based access control (Administrator, Modeler, Analyst).
*   Graphical User Interface (GUI) for topology creation and management (Grids, Transformers, Houses).
*   Configuration of parameters for Grids (name), Transformers (name, capacity, losses, efficiency, service years, ampacity, export flag), and Houses (type, prioritization flags).
*   Configuration and management of profiles for Houses: Load, Solar, Battery, EV, Wind (using various methods: CSV upload, Load Builder, Generation Engine, Templates, Parameter input).
*   Definition and configuration of the energy allocation prioritization list (user-defined flags).
*   Configuration of simulation parameters (duration - up to 1 year, time step - 15 mins, allocation scope - intra-transformer/intra-grid).
*   Execution of the simulation engine based on the configured topology, profiles, and parameters.
*   Modeling of peer-to-peer energy allocation based on priorities, available excess, and demand.
*   Modeling of battery charging/discharging logic based on configuration (self-consumption priority, community support, programmable schedules).
*   Modeling of energy import/export with the utility grid.
*   Storage and retrieval of simulation configurations and results.
*   Visualization and reporting of key simulation outputs and KPIs.
*   Export/Import of topology configurations (e.g., via JSON).
*   Export of simulation results (e.g., via CSV).

**Out of Scope (for v1 unless specified otherwise):**

*   Real-time simulation or control of physical assets.
*   Direct financial transactions or billing simulation (focus is on energy flows).
*   Advanced grid stability analysis (voltage/frequency...).
*   Automated optimization algorithms to find the best configuration (focus is on simulating user-defined configurations).
*   Integration with external real-time data sources (like live weather, live market prices).
*   Detailed modeling of the utility grid beyond simple import/export points and potentially tariffs (for savings calculation if added).

# 4. Functional Requirements

**Authentication & Authorization**
*   **FR-AUTH-01:** System shall allow users to register and log in.
*   **FR-AUTH-02:** System shall enforce role-based permissions (Admin, Modeler, Analyst, Integrator, *Shashwat has to define them...*). *(Note: Role definition pending)*

**Topology Management**
*   **FR-TOPO-01:** Modelers shall be able to create, view, edit, and delete Grids.
*   **FR-TOPO-02:** Modelers shall be able to add, view, edit, delete, and position Transformers within a Grid.
*   **FR-TOPO-03:** Modelers shall be able to add, view, edit, delete, and position Houses under a Transformer.
*   **FR-TOPO-04:** The system shall visually represent the hierarchical topology (Grid -> Transformer -> House).

**Configuration Management**
*   **FR-CONF-01:** Modelers shall be able to configure parameters for Transformers (Name, Max Capacity (kW), Years of Service, Forward Efficiency (%), Backward Efficiency (%), Primary Ampacity (A), Secondary Ampacity (A), Allow Export flag, Losses - *add field*). (*Digital Twin Model field noted - functionality TBD*).
*   **FR-CONF-02:** Modelers shall be able to configure parameters for Houses (Name, Type - e.g., Residential, Hospital, School, EV Charger, Configurable Flags for prioritization).

**Profile Management**
*   **FR-PROF-01:** Modelers shall be able to create/upload Load Profiles for Houses using: CSV upload (15-min data), Load Builder (appliance-based), Generation Engine (Avg kWh/Bill/Demand based), Predefined Templates.
*   **FR-PROF-02:** System shall convert Load Profile inputs (Builder, Engine, Templates) into a 15-minute interval time-series for the simulation duration.
*   **FR-PROF-03:** Modelers shall be able to create/upload Solar Profiles using: CSV upload (15-min generation data), parameter input (Capacity, Location, Efficiency - requires internal generation logic/weather data).
*   **FR-PROF-04:** Modelers shall be able to configure Battery Profiles (Capacity (kWh), Max Charge/Discharge Power (kW), Efficiency (%), DoD (%), Programmable behavior - e.g., prioritize self-consumption, support community, charge from solar only, time-based charging/discharging).
*   **FR-PROF-05:** Modelers shall be able to configure EV Profiles (using suggested parameters: energy need/schedule, charging power, smart charging flag).
*   **FR-PROF-06:** Modelers shall be able to configure Wind Profiles (using suggested parameters: turbine specs/location or uploaded generation data).
*   **FR-PROF-07:** Modelers shall be able to save profile configurations and apply them to multiple houses.

**Simulation Execution & Logic**
*   **FR-SIM-01:** Analysts shall be able to select a configured topology for simulation.
*   **FR-SIM-02:** Analysts shall be able to define simulation parameters: Start Date, Duration (e.g., 1 month, 1 year), Allocation Scope (Intra-transformer only, Intra-grid).
*   **FR-SIM-03:** Analysts shall be able to configure the ordered Priority List for excess energy allocation based on House flags.
*   **FR-SIM-04:** The system shall execute the simulation in 15-minute time steps for the specified duration.
*   **FR-SIM-05:** The simulation engine shall calculate load, generation, battery state, and net balance for each node at each time step.
*   **FR-SIM-06:** The simulation engine shall allocate excess energy from producing nodes to consuming nodes based on the defined allocation scope and priority list, accounting for transformer/distribution losses.
*   **FR-SIM-07:** The simulation engine shall manage battery charge/discharge according to configured rules and available energy/capacity.
*   **FR-SIM-08:** The simulation engine shall calculate energy import/export with the main utility grid based on the net balance after internal allocation.

**Results & Reporting**
*   **FR-RSLT-01:** The system shall store the results of each simulation run, linked to the specific topology and parameters used.
*   **FR-RSLT-02:** Analysts shall be able to view simulation results through tables and charts (displaying suggested KPIs and outputs).
*   **FR-RSLT-03:** Analysts shall be able to compare results from multiple simulation runs side-by-side.
*   **FR-RSLT-04:** Analysts shall be able to export simulation results (e.g., summary KPIs, time-series data) in CSV format.

**Import/Export**
*   **FR-IO-01:** Users shall be able to export the full topology and configuration definition (e.g., JSON format).
*   **FR-IO-02:** Users shall be able to import a previously exported topology definition to create a new simulation setup.

# 5. Non-Functional Requirements

*   **NFR-PERF-01:** Simulation execution time should be reasonable (e.g., a 1-year simulation for a moderately sized topology of ~100 nodes should complete within minutes, not hours - Target to be refined).
*   **NFR-SCAL-01:** The system should be designed to handle topologies with potentially hundreds or thousands of nodes.
*   **NFR-USAB-01:** The user interface should be intuitive and provide clear visual feedback for topology creation and results analysis.
*   **NFR-RELI-01:** Simulation calculations must be accurate and repeatable.
*   **NFR-SECU-01:** Access to system features must be restricted based on user roles.
*   **NFR-MAIN-01:** The codebase should follow best practices for maintainability, including clear separation of concerns, comments, and potential documentation.

# 6. User Roles & Permissions (Proposed)

*   **Administrator:** Full CRUD access to Users, Roles, System Settings. All permissions of Modeler and Analyst.
*   **Modeler:** CRUD access to Grids, Transformers, Houses, Profiles, Configurations. Read-access to simulation results. Cannot manage users or system settings. Cannot run simulations (unless also given Analyst role).
*   **Analyst:** Selects topologies (Read-only). Configures and Runs Simulations. CRUD access to Simulation Runs and Results. Views/Exports results. Cannot modify topologies or manage users/settings.
*(Note: Integrator role mentioned in FR-AUTH-02 needs definition)*

# 7. Data Requirements

*   Topology Data (Grids, Transformers, Houses, connections).
*   Configuration Data (Node parameters, Profile settings).
*   Time-Series Profile Data (Load, Solar, Wind, EV - potentially large).
*   Simulation Parameters (Duration, priority list, etc.).
*   Simulation Results Data (Time-series node balances, aggregate KPIs - potentially very large).
*   User and Role Data.
*   Need for standard load/generation profile templates.
*   Potential need for integrated weather data source for solar/wind generation based on location.

# 8. Assumptions

*   The 15-minute interval is sufficient resolution for meaningful simulation.
*   Peer-to-peer energy transfer within the defined scopes (transformer/grid) is a valid abstraction for the simulation's purpose.
*   Configurable losses adequately represent real-world distribution inefficiencies.
*   Standard profile generation methods provide reasonable approximations when actual data is unavailable.

# 9. Constraints

*   **Technology stack:** Frontend (Angular/React), Backend (Python/FastAPI), ORM (Peewee), DB (PostgreSQL).
*   Development must follow a 3-layer architecture (API, Service, Data/Repository).
*   The initial version focuses on physical energy flows, not financial aspects.
*   **Deployment environments:** DEV, TEST, INT, PROD.

# 10. Glossary

*   **Grid:** Top-level container for a distinct energy community simulation.
*   **Transformer:** Represents a distribution transformer and the sub-community it serves. Can contain Houses or other Transformers (though latter seems less likely based on UI).
*   **House:** A leaf node representing an energy consumer or prosumer (e.g., residence, hospital, EV station).
*   **Prosumer:** A node that both consumes and produces energy (e.g., house with solar panels).
*   **Profile:** Time-series data representing energy consumption or generation (Load, Solar, Wind, EV).
*   **Allocation:** The process of distributing excess energy from producers to consumers within the simulation.
*   **Prioritization:** The user-defined order in which loads receive allocated excess energy.
*   **Self-Consumption:** The percentage of locally generated energy that is consumed locally (within the grid/community).