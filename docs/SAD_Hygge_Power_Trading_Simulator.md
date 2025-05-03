# Software Architecture Document (SAD)
## Hygge Power Trading Simulator

**Version:** 0.1
**Date:** 20/July/2024

# 1. Introduction

This document describes the proposed software architecture for the Hygge Power Trading Simulator. It outlines the major components, their interactions, the data model, technology stack, and deployment strategy, guided by the requirements specified in the BRD. The goal is to create a scalable, maintainable, and performant system.

# 2. Architectural Goals & Constraints

**Goals:** Modularity, Scalability (handle many nodes & long simulations), Maintainability (clear separation of concerns), Testability, Performance (efficient simulation execution), Usability (responsive UI).

**Constraints:** Must use Angular or React for Frontend, Python/FastAPI for Backend API, Peewee ORM, PostgreSQL database. Must implement a 3-layer backend architecture. Must support deployment across DEV, TEST, INT, PROD environments.

# 3. Logical Architecture

## 3.1. Layered View (Backend)

### API Layer (FastAPI):
**Responsibilities:**
*   Handles HTTP requests (RESTful endpoints),
*   Authentication & Authorization (using JWT),
*   Request Validation (using Pydantic models),
*   Data Serialization/Deserialization (JSON),
*   Delegates business logic to the Service Layer.
*   Provides interface for the Frontend.

### Service Layer (Python Classes/Modules):
**Responsibilities:**
*   Contains the core business logic.
*   Orchestrates operations like topology management, profile processing, simulation setup, running the simulation engine, applying allocation algorithms, calculating results.
*   Interacts with the Data Layer to fetch/persist data.
*   Stateless where possible to aid scalability.

### Data Layer (Python Modules with Peewee/Repository Pattern):
**Responsibilities:**
*   Abstracts database interactions.
*   Implements Repository pattern for data access (TopologyRepository, ProfileRepository, ResultsRepository).
*   Defines Peewee models mapping to database tables.
*   Handles all CRUD operations and complex queries.
*   Ensures data integrity.

## 3.2. Component View

### Frontend Application (React):
*   UI Components (Topology viewer/editor, Configuration forms, Profile managers, Simulation setup, Results dashboards/charts).
*   State Management.
*   API Client Service (Handles communication with Backend API).
*   Build/Development Tools (React App).

### Backend Application (FastAPI):
*   **Web Server (Uvicorn/Gunicorn):** Runs the FastAPI application.
*   **API Endpoints Module:** Defines routes and request handlers for topology, configuration, profiles, simulation, results, auth.
*   **Authentication Service:** Handles user login, token generation/validation.
*   **Topology Service:** Logic for managing grids, transformers, houses.
*   **Profile Service:** Logic for processing, generating, storing various profiles.
*   **Simulation Service:** Orchestrates simulation runs, manages state, calls the engine.
*   **Simulation Engine Module:** Core algorithm performing the 15-minute step-by-step calculation, including allocation logic and battery management. Consider if this should run synchronously within a request or asynchronously as a background task for longer simulations.
*   **Results Service:** Logic for querying, aggregating, and formatting simulation results.
*   **Repository Modules (Data Layer):** Handles DB interactions via Peewee models.

### Database (PostgreSQL):
*   Stores all persistent data (topology, config, profiles, results, users).

# 4. Data Architecture

**Database:** PostgreSQL relational database.
**ORM:** Peewee.

**Key Tables (Illustrative):**
*   `users` (`user_id`, `username`, `password_hash`, `role_id`)
*   `roles` (`role_id`, `role_name`)
*   `grids` (`grid_id`, `name`, `created_by`, `created_at`)
*   `transformers` (`transformer_id`, `grid_id`, `name`, `capacity_kw`, ...)
*   `houses` (`house_id`, `transformer_id`, `name`, `house_type`, ...)
*   `house_flags` (`flag_id`, `house_id`, `flag_name`)
*   `profiles` (`profile_id`, `house_id`, `profile_type` (load/solar/...), `source_type` (upload/builder...), `config_details_json`, `data_storage_ref`) -> Time-series data might be stored efficiently, e.g., in related tables, JSONB, or potentially a dedicated time-series extension/DB if performance dictates.
*   `simulation_runs` (`run_id`, `topology_snapshot_json`, `parameters_json`, `user_id`, `start_time`, `end_time`, `status`)
*   `simulation_results` (`result_id`, `run_id`, `node_id`, `timestamp`, `load_kw`, `generation_kw`, `battery_soc`, `net_energy_kwh`, ...) -> This table can become very large. Consider partitioning or aggregation strategies.
*   `priority_lists` (`list_id`, `name`, `configuration_json`)

**Topology Storage:** While stored relationally, provide export/import functionality using JSON representation.

**Time-Series Data:** Needs careful consideration for storage and querying performance (indexing, partitioning).

# 5. Technology Stack

*   **Frontend:** React (latest LTS) OR Angular (as per constraints)
*   **Backend:** Python 3.11+, FastAPI
*   **ORM:** Peewee
*   **Database:** PostgreSQL 14+
*   **API Specification:** OpenAPI (auto-generated by FastAPI)
*   **Caching (Optional):** Redis (for caching results or session data if needed)

# 6. Deployment View

**Environments:** DEV, TEST, INT, PROD.

**Infrastructure:** Recommend containerization using Docker.
*   `docker-compose.yml` for local development (Frontend, Backend, DB).
*   TEST/INT/PROD environments. (Dockers)
*   PostgreSQL (AWS RDS).

**Deployment:**
*   CI/CD pipeline (GitLab CI, GitHub Actions) to automate testing, building Docker images, and deploying to respective environments.
*   Backend API and Frontend served as separate containers/services.

# 7. Non-Functional Requirements Implementation

*   **Performance:** Efficient database queries (indexing, optimized ORM usage), potentially asynchronous simulation execution for long runs, consider CPython extensions or libraries like NumPy/Pandas if numerical computation becomes a bottleneck. Profile generation logic optimized.
*   **Scalability:** Stateless backend services where possible allow horizontal scaling. Database scalability through managed services. Consider separating simulation engine workers if CPU-intensive.
*   **Usability:** Clean API design, responsive frontend framework, clear visual components for topology and results.
*   **Reliability:** Transaction management in DB operations, error handling and logging, repeatable simulation logic. Potential for saving simulation state periodically for long runs.
*   **Security:** JWT-based authentication, HTTPS enforcement, role-based authorization checks at the API layer, input validation.
*   **Maintainability:** Strict adherence to layered architecture, use of Repository pattern, code linting/formatting, unit/integration tests, comments/documentation.

# 8. Design Decisions & Trade-offs

**Synchronous vs. Asynchronous Simulation:**
*   **Sync:** Simpler implementation initially. Suitable for short simulations. Might lead to long HTTP request timeouts for yearly simulations.
*   **Async:** More complex (requires task queue like Celery). Better user experience for long simulations (request returns immediately, user notified on completion). Better resource management.
*   **Recommendation:** Start Sync, but design with Async in mind for future enhancement.

**Time-Series Data Storage:**
*   **Relational Table:** Standard, works with Peewee. Can become slow for large datasets/complex queries.
*   **JSONB:** Flexible, good for unstructured profile config. Querying inside JSON can be less performant.
*   **Dedicated TSDB (e.g., TimescaleDB extension for PostgreSQL, InfluxDB):** Optimized for time-series, best performance. Adds complexity.
*   **Recommendation:** Start with relational, optimize with indexing/partitioning. Evaluate TSDB if performance becomes an issue.

**Peewee ORM:**
*   Lightweight and simple, as requested. Less feature-rich than SQLAlchemy but likely sufficient.