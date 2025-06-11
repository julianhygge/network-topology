from peewee import UUIDField, ForeignKeyField, CharField, IntegerField, DateTimeField, BooleanField
import uuid
import datetime
from app.data.schemas.schema_base import BaseModel
from app.data.schemas.transactional.user_schema import User

class SimulationContainer(BaseModel):
    id = UUIDField(primary_key=True, default=uuid.uuid4)
    created_by = ForeignKeyField(
        User,
        backref="user",
        on_delete="CASCADE",
        lazy_load=False,
        column_name="created_by",
    )
    name = CharField()
    description = CharField()
    location_name = CharField()
    time_step_min = IntegerField()
    algorithm_name = CharField()
    power_unit = CharField()
    created_on = DateTimeField(default=datetime.datetime.utcnow)
    modified_on = DateTimeField(default=datetime.datetime.utcnow)
    active = BooleanField(default=True)

    class Meta:
        schema = "simulation_engine"
        table_name = "simulation_containers"