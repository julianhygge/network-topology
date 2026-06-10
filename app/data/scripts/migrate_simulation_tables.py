#!/usr/bin/env python3
"""
Database migration script for network-topology-int.
Creates missing simulation_engine tables and seeds master data.
Run this script inside the simulator-api container or with PYTHONPATH set.
"""

import os
import sys
import uuid

# Ensure the project root is in the path
PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if PROJECT_ROOT not in sys.path:
    sys.path.insert(0, PROJECT_ROOT)

from app.config.configuration import ApiConfiguration
from app.data.schemas.hygge_database import HyggeDatabase
from app.data.schemas.schema_base import BaseModel

# Simulation models
from app.data.schemas.simulation.simulation_container_schema import SimulationContainer
from app.data.schemas.simulation.simulation_runs_schema import SimulationRuns, SimulationSelectedPolicy
from app.data.schemas.simulation.metering_policy_schema import (
    GrossMeteringPolicy,
    NetMeteringPolicy,
    TimeOfUseRatePolicy,
)
from app.data.schemas.simulation.house_bill_schema import HouseBill

# Master models
from app.data.schemas.master.master_schema import SimulationAlgorithm, NetMeteringPolicyTypes


def create_schema(db, schema_name: str):
    """Create PostgreSQL schema if it does not exist."""
    db.execute_sql(f'CREATE SCHEMA IF NOT EXISTS "{schema_name}"')
    print(f"  Schema '{schema_name}' ensured.")


def create_tables(db, models: list):
    """Create tables using Peewee create_tables."""
    db.create_tables(models)
    for model in models:
        print(f"  Table created: {model._meta.schema}.{model._meta.table_name}")


def seed_master_data(db):
    """Insert seed data for master lookup tables."""
    print("\nSeeding master.simulation_algorithm_types ...")
    algorithms = [
        {"id": uuid.UUID("11111111-1111-1111-1111-111111111111"), "algorithm_code": "SIMPLE_NET", "display_name": "Simple Net Metering", "description": "Simple net metering policy", "active": True},
        {"id": uuid.UUID("22222222-2222-2222-2222-222222222222"), "algorithm_code": "GROSS_METERING", "display_name": "Gross Metering", "description": "Gross metering policy", "active": True},
        {"id": uuid.UUID("33333333-3333-3333-3333-333333333333"), "algorithm_code": "TOU", "display_name": "Time of Use", "description": "Time of Use metering policy", "active": True},
    ]
    for algo in algorithms:
        SimulationAlgorithm.insert(**algo).on_conflict_ignore().execute()
        print(f"  Seeded: {algo['algorithm_code']}")

    print("\nSeeding master.net_metering_policy_types ...")
    policy_types = [
        {"id": uuid.UUID("44444444-4444-4444-4444-444444444444"), "policy_code": "NET_SIMPLE", "display_name": "Simple Net", "description": "Simple net metering", "active": True},
        {"id": uuid.UUID("55555555-5555-5555-5555-555555555555"), "policy_code": "NET_ADVANCED", "display_name": "Advanced Net", "description": "Advanced net metering", "active": True},
    ]
    for pt in policy_types:
        NetMeteringPolicyTypes.insert(**pt).on_conflict_ignore().execute()
        print(f"  Seeded: {pt['policy_code']}")


def check_topology_tables(db):
    """Check if topology schema tables exist, create if missing."""
    print("\n--- TOPOLOGY schema check ---")
    topology_tables = [
        "localities",
        "substations",
        "nodes",
        "transformers",
        "houses",
        "house_flags",
    ]
    for table in topology_tables:
        cursor = db.execute_sql(
            "SELECT EXISTS (SELECT FROM information_schema.tables WHERE table_schema = 'topology' AND table_name = %s);",
            (table,)
        )
        exists = cursor.fetchone()[0]
        if not exists:
            print(f"  WARNING: topology.{table} is MISSING")
        else:
            print(f"  OK: topology.{table} exists")


def main():
    print("Starting database migration for network-topology-int ...")
    print(f"Using project root: {PROJECT_ROOT}")
    print()

    # Initialize configuration
    config = ApiConfiguration()
    HyggeDatabase.set_config(config.db)
    db = HyggeDatabase.get_instance()
    print(f"Connected to database: {config.db.database}")
    print()

    # 1. Create schemas
    print("Creating schemas ...")
    create_schema(db, "simulation_engine")
    create_schema(db, "topology")
    print()

    # 2. Create/ensure master tables FIRST (FK dependencies)
    print("Creating master tables ...")
    master_models = [SimulationAlgorithm, NetMeteringPolicyTypes]
    create_tables(db, master_models)
    print()

    # 3. Create simulation_engine tables
    print("Creating simulation_engine tables ...")
    simulation_models = [
        SimulationContainer,
        SimulationRuns,
        SimulationSelectedPolicy,
        GrossMeteringPolicy,
        NetMeteringPolicy,
        TimeOfUseRatePolicy,
        HouseBill,
    ]
    create_tables(db, simulation_models)
    print()

    # 4. Seed master data
    seed_master_data(db)
    print()

    # 5. Check topology tables
    check_topology_tables(db)
    print()

    # 6. Verify permissions for simulation resource
    print("Checking permissions ...")
    try:
        from app.data.schemas.auth.auth_schema import Permissions
        from app.data.schemas.auth.auth_schema import Roles
        from app.data.schemas.auth.auth_schema import RolePermissionRel

        sim_permissions = [
            {"name": "retrieve-simulation", "description": "Can retrieve simulation containers/runs", "resource_name": "simulation", "can_retrieve": True},
            {"name": "create-simulation",   "description": "Can create simulation containers/runs", "resource_name": "simulation", "can_create": True},
            {"name": "update-simulation",   "description": "Can update simulation containers/runs", "resource_name": "simulation", "can_update": True},
            {"name": "delete-simulation",   "description": "Can delete simulation containers/runs", "resource_name": "simulation", "can_delete": True},
            {"name": "search-simulation",   "description": "Can search simulation containers/runs", "resource_name": "simulation", "can_search": True},
        ]
        for perm in sim_permissions:
            Permissions.insert(**perm).on_conflict_ignore().execute()
            print(f"  Permission ensured: {perm['name']}")

        # Ensure the 'User' role gets retrieve-simulation
        user_role = Roles.select().where(Roles.name == "User").first()
        if user_role:
            retrieve_sim = Permissions.select().where(Permissions.name == "retrieve-simulation").first()
            if retrieve_sim:
                RolePermissionRel.insert(role=user_role, permission=retrieve_sim).on_conflict_ignore().execute()
                print(f"  Role 'User' linked to 'retrieve-simulation'")
    except Exception as e:
        print(f"  WARNING: Could not fully configure permissions: {e}")
    print()

    print("Migration completed successfully.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
