# Hygge Power Trading Simulator - Backend API

## Description

This is the backend API for the Hygge Power Trading Simulator. The simulator is designed to model and analyze the behavior of local energy communities (microgrids). It simulates energy generation, consumption, and sharing within these communities over time to understand energy flows, optimize distribution, assess configurations, and evaluate potential benefits.

This API provides endpoints for managing the microgrid topology (Grids, Transformers, Houses), configuring energy profiles (Load, Solar, etc.), managing users and authentication, and potentially running simulations (based on the BRD, simulation logic resides within the backend services).

## Technology Stack

*   **Language:** Python 3.x
*   **Framework:** FastAPI
*   **Database:** PostgreSQL
*   **ORM:** Peewee
*   **Configuration:** Dynaconf (.toml files, .env)
*   **Authentication:** JWT (PyJWT)
*   **Data Validation:** Pydantic
*   **Async Server:** Uvicorn
*   **Other Key Libraries:** MQTT (paho-mqtt), Pandas, Scipy, Dependency Injector

## Project Structure

The backend follows a 3-layer architecture:

*   **`app/api/`:** Handles incoming HTTP requests, routing, request/response models (Pydantic), and middleware (CORS, Auth, DB Session, Logging). Contains API resources organized by feature (e.g., `auth`, `topology`, `load_profile`).
*   **`app/domain/`:** Contains the core business logic, services, and interfaces defining the application's capabilities.
*   **`app/data/`:** Manages data persistence, including database schemas (Peewee models), repositories for data access, and interfaces for repositories.
*   **`app/config/`:** Handles application configuration loading using Dynaconf.
*   **`app/exceptions/`:** Defines custom exceptions and exception handlers.
*   **`app/utils/`:** Contains utility functions (logging, datetime, etc.).

## Configuration

Configuration is managed using Dynaconf.

1.  **Environment Files:** Settings specific to environments (local, dev, test, int, prod) are defined in `.toml` files within `app/config/` (e.g., `local.toml`, `dev.toml`).
2.  **Secrets/Environment Variables:** Sensitive information like database credentials, JWT secrets, etc., should be managed via environment variables. An example file is provided at `app/config/example.env`. Copy this to `.env` in the `api/` directory and fill in the required values. The application loads these variables automatically.

    ```bash
    # In the api/ directory
    cp app/config/example.env .env
    # Edit .env with your specific settings
    ```

## Setup and Installation

1.  **Clone the repository:**
    ```bash
    # Assuming you are in the main project directory
    # git clone <repository_url> # If applicable
    ```

2.  **Navigate to the API directory:**
    ```bash
    cd api
    ```

3.  **Create and activate a virtual environment (Recommended):**
    ```bash
    python -m venv venv
    source venv/bin/activate # On Linux/macOS
    # venv\Scripts\activate # On Windows
    ```

4.  **Install dependencies:**
    ```bash
    pip install -r requirements.txt
    ```

5.  **Set up PostgreSQL Database:**
    *   Ensure you have a running PostgreSQL instance.
    *   Create a database for the application (e.g., `hygge_p2p_db`).
    *   Create a user and grant privileges to the database.

6.  **Configure Environment Variables:**
    *   Copy `app/config/example.env` to `.env` in the `api/` directory (if you haven't already).
    *   Update `.env` with your database connection details (user, password, host, port, database name) and other required secrets (like `JWT_SECRET_KEY`).

## Running the Application

To run the FastAPI application locally for development:

```bash
# Ensure your virtual environment is activated and you are in the api/ directory
# The --reload flag enables auto-reloading on code changes.
# Adjust --port if needed.
uvicorn app.main:app --reload --host 0.0.0.0 --port 8022
```

The API will be available at `http://localhost:8022`.

## API Endpoints & Documentation

The API follows RESTful principles.

*   **Base Path:** All API endpoints are served under the `/net-topology-api` root path.
*   **Versioning:** API version 1 endpoints are prefixed with `/v1/`.
    *   Example: `http://localhost:8000/net-topology-api/v1/users`
*   **Interactive Documentation:** FastAPI automatically generates interactive API documentation using Swagger UI and ReDoc.
    *   **Swagger UI:** `http://localhost:8000/net-topology-api/docs`
    *   **ReDoc:** `http://localhost:8000/net-topology-api/redoc`

Use these interfaces to explore available endpoints, view request/response schemas, and test the API directly from your browser.

