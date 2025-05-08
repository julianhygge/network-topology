"""Solar profile schema."""

from peewee import (
    AutoField,
    BooleanField,
    CharField,
    DateTimeField,
    DecimalField,
    DoubleField,
    ForeignKeyField,
    UUIDField,
)

from app.data.schemas.auth.auditable_base import AuditableBase
from app.data.schemas.schema_base import BaseModel
from app.data.schemas.transactional.topology_schema import Node


class SolarProfile(AuditableBase):
    """Solar profile schema."""

    id = UUIDField(primary_key=True)
    active = BooleanField(default=True)
    solar_available = BooleanField(null=True)
    house_id = ForeignKeyField(
        Node, backref="solar_profile", on_delete="CASCADE"
    )
    installed_capacity_kw = DecimalField(max_digits=4, decimal_places=2)
    tilt_type = CharField(max_length=12)
    years_since_installation = DecimalField(
        max_digits=4, decimal_places=2, null=True
    )
    simulate_using_different_capacity = BooleanField(null=True)
    capacity_for_simulation_kw = DecimalField(max_digits=4, decimal_places=2)
    available_space_sqft = DecimalField(
        max_digits=5, decimal_places=2, null=True
    )
    simulated_available_space_sqft = DecimalField(
        max_digits=4, decimal_places=2, null=True
    )

    class Meta:
        """Metaclass for SolarProfile."""

        schema = "solar"
        table_name = "solar_profile"


class SolarItemProfile(BaseModel):
    """
    Schema for representing a solar item profile.
    """

    id = AutoField()
    user_id = UUIDField()
    solar_profile = ForeignKeyField(
        SolarProfile, backref="solar_item_profile", on_delete="CASCADE"
    )
    production_kwh = DoubleField()
    timestamp = DateTimeField()
    voltage_v = DoubleField()
    current_amps = DoubleField()

    class Meta:
        """Metaclass for SolarItemProfile."""

        table_name = "solar_item_profile"
        schema = "solar"
