from peewee import ForeignKeyField, DoubleField, UUIDField, CharField, TimeField
import uuid
from app.data.schemas.schema_base import BaseModel
from app.data.schemas.simulation.simulation_runs_schema import SimulationRuns


class GrossMeteringPolicy(BaseModel):
    simulation_run_id = ForeignKeyField(
        SimulationRuns,
        backref="gross",
        column_name="simulation_run_id",
        primary_key=True
    )
    import_retail_price_per_kwh = DoubleField()
    export_wholesale_price_per_kwh = DoubleField()

    class Meta:
        schema = "simulation_engine"
        table_name = "gross_metering_policy_params"

class NetMeteringPolicy(BaseModel):
    simulation_run_id = ForeignKeyField(
        SimulationRuns,
        backref="net_metering",
        column_name="simulation_run_id",
        primary_key=True
    )
    retail_price_per_kwh = DoubleField()

    class Meta:
        schema = "simulation_engine"
        table_name = "net_metering_policy_params"

class TimeOfUseRatePolicy(BaseModel):
    id = UUIDField(primary_key=True, default=uuid.uuid4)
    simulation_run_id = ForeignKeyField(
        SimulationRuns,
        backref="tou",
        column_name="simulation_run_id"
    )
    time_period_label = CharField()
    start_time = TimeField()
    end_time = TimeField()
    import_retail_rate_per_kwh = DoubleField()
    export_wholesale_rate_per_kwh = DoubleField()

    class Meta:
        schema = "simulation_engine"
        table_name = "tou_rate_policy_params"
