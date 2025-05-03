import uuid

from peewee import (BooleanField, CharField, DecimalField, ForeignKeyField,
                    UUIDField)

from app.data.schemas.auth.auditable_base import AuditableBase
from app.data.schemas.transactional.topology_schema import Node


class SolarProfile(AuditableBase):
    id = UUIDField(primary_key=True)
    active = BooleanField(default=True)
    solar_available = BooleanField(null=True)
    house_id = ForeignKeyField(Node, backref='solar_profile', on_delete='CASCADE')
    installed_capacity_kw = DecimalField(max_digits=4, decimal_places=2)
    tilt_type = CharField(max_length=12)
    years_since_installation = DecimalField(max_digits=4, decimal_places=2, null=True)
    simulate_using_different_capacity = BooleanField(null=True)
    capacity_for_simulation_kw = DecimalField(max_digits=4, decimal_places=2)
    available_space_sqft = DecimalField(max_digits=5, decimal_places=2, null=True)
    simulated_available_space_sqft = DecimalField(max_digits=4, decimal_places=2, null=True)

    class Meta:
        schema = 'solar'
        table_name = 'solar_profile'
