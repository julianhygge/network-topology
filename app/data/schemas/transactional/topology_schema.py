import uuid

from peewee import UUIDField, BooleanField, CharField, ForeignKeyField, DecimalField, TextField
from app.data.schemas.auth.auditable_base import AuditableBase
from app.data.schemas.schema_base import BaseModel, InfDateTimeField


class Transactional(AuditableBase):
    id = UUIDField(primary_key=True, default=uuid.uuid4)
    active = BooleanField()

    class Meta:
        schema = 'transactional'


class Account(Transactional):
    validity_start = InfDateTimeField()
    validity_end = InfDateTimeField()
    record_id = UUIDField()
    alias_name = CharField(max_length=50, null=True)
    type = CharField(max_length=50, null=True)
    phone_number = CharField(max_length=12, default='8429020287')

    class Meta:
        table_name = 'accounts'


class Locality(Transactional):
    name = CharField(max_length=100)

    class Meta:
        table_name = 'localities'


class Substation(Transactional):
    locality = ForeignKeyField(Locality, backref='substations')
    name = CharField(max_length=100)

    class Meta:
        table_name = 'substations'


class Transformer(Transactional):
    substation = ForeignKeyField(Substation, backref='transformers')
    max_capacity_kw = DecimalField(max_digits=10, decimal_places=2)
    export_efficiency = DecimalField(max_digits=5, decimal_places=2, null=True)
    allow_export = BooleanField(default=False)

    class Meta:
        table_name = 'transformers'


class House(Transactional):
    transformer = ForeignKeyField(Transformer, backref='houses', on_delete='CASCADE')
    load_profile = TextField(null=True)
    has_solar = BooleanField(default=False)
    solar_kw = DecimalField(max_digits=10, decimal_places=2, null=True)
    house_type = CharField(max_length=50, null=True)
    connection_kw = DecimalField(max_digits=10, decimal_places=2, null=True)
    has_battery = BooleanField(default=False)
    battery_type = CharField(max_length=50, null=True)
    voluntary_storage = BooleanField()
    battery_peak_charging_rate = DecimalField(max_digits=10, decimal_places=2, null=True)
    battery_peak_discharging_rate = DecimalField(max_digits=10, decimal_places=2, null=True)
    battery_total_kwh = DecimalField(max_digits=10, decimal_places=2, null=True)

    class Meta:
        table_name = 'houses'
