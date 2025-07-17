import datetime
import uuid

from peewee import (
    CharField,
    DateTimeField,
    DoubleField,
    ForeignKeyField,
    IntegerField,
    UUIDField,
)

from app.data.schemas.master.master_schema import (
    NetMeteringPolicyTypes,
    SimulationAlgorithm,
)
from app.data.schemas.schema_base import BaseModel
from app.data.schemas.simulation.simulation_container_schema import SimulationContainer
from app.data.schemas.transactional.topology_schema import Node, Locality
from app.data.schemas.transactional.user_schema import User


class SimulationRuns(BaseModel):
    id = UUIDField(primary_key=True, default=uuid.uuid4)
    run_name = CharField()
    topology_root_node_id = ForeignKeyField(
        Node, backref="simulation", column_name="topology_root_node_id"
    )
    # simulation_algorithm_type_id = ForeignKeyField(
    #     SimulationAlgorithm,
    #     backref="simulation_algo",
    #     column_name="simulation_algorithm_type_id")
    simulation_algorithm_type_id = UUIDField()
    billing_cycle_month = IntegerField()
    billing_cycle_year = IntegerField()
    status = CharField()
    created_by = ForeignKeyField(
        User,
        backref="created",
        on_delete="SET NULL",
        lazy_load=False,
        column_name="created_by",
    )
    created_on = DateTimeField(default=datetime.datetime.utcnow)
    modified_on = DateTimeField(default=datetime.datetime.utcnow)
    simulation_start_timestamp = DateTimeField()
    simulation_end_timestamp = DateTimeField()
    locality_id = ForeignKeyField(
        Locality,
        backref="simulation",
        column_name="locality_id"
    )
    simulation_container_id = ForeignKeyField(
        SimulationContainer,
        on_delete="CASCADE",
        column_name="simulation_container_id"
    )
    description = CharField()
    run_sequence_identifier = CharField()

    class Meta:
        schema = "simulation_engine"
        table_name = "simulation_runs"


class SimulationSelectedPolicy(BaseModel):
    simulation_run_id = ForeignKeyField(
        SimulationRuns,
        backref="simulation_policy",
        column_name="simulation_run_id",
        primary_key=True,
    )
    net_metering_policy_type_id = ForeignKeyField(
        NetMeteringPolicyTypes,
        backref="simulation_policy",
        column_name="net_metering_policy_type_id",
    )
    fac_charge_per_kwh_imported = DoubleField()
    tax_rate_on_energy_charges = DoubleField()

    class Meta:
        schema = "simulation_engine"
        table_name = "simulation_selected_policies"
