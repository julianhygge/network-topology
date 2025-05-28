import uuid

from peewee import UUIDField, ForeignKeyField, DoubleField
from playhouse.postgres_ext import JSONField, BinaryJSONField  # type: ignore[import]

from app.data.schemas.schema_base import BaseModel
from app.data.schemas.simulation.simulation_runs_schema import SimulationRuns
from app.data.schemas.transactional.topology_schema import House


class HouseBill(BaseModel):
    id = UUIDField(primary_key=True, default=uuid.uuid4)
    simulation_run_id = ForeignKeyField(
        SimulationRuns,
        backref="simulation_policy",
        column_name="simulation_run_id"
    )
    house_node_id = ForeignKeyField(
        House,
        backref="house_bill",
        column_name="house_node_id"
    )
    total_energy_imported_kwh = DoubleField()
    total_energy_exported_kwh = DoubleField()
    net_energy_balance_kwh = DoubleField()
    calculated_bill_amount = DoubleField()
    bill_details = BinaryJSONField()

    class Meta:
        schema = "simulation_engine"
        table_name = "house_bills"

