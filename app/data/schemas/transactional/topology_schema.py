import datetime
import uuid
from peewee import UUIDField, BooleanField, DateTimeField, CharField, ForeignKeyField, DecimalField, TextField
from app.data.schemas.schema_base import BaseModel, InfDateTimeField


class Account(BaseModel):
    id = UUIDField(primary_key=True, default=uuid.uuid4)
    active = BooleanField()
    created_on = DateTimeField(default=datetime.datetime.utcnow)
    modified_on = DateTimeField(default=datetime.datetime.utcnow)
    validity_start = InfDateTimeField()
    validity_end = InfDateTimeField()
    record_id = UUIDField()
    alias_name = CharField(max_length=50, null=True)
    created_by = ForeignKeyField('self', null=True, backref='created_accounts')
    modified_by = ForeignKeyField('self', null=True, backref='modified_accounts')
    type = CharField(max_length=50, null=True)
    phone_number = CharField(max_length=12, default='8429020287')


class Locality(BaseModel):
    id = UUIDField(primary_key=True, default=uuid.uuid4)
    name = CharField(max_length=100)
    created_on = DateTimeField(default=datetime.datetime.utcnow)
    modified_on = DateTimeField(default=datetime.datetime.utcnow)
    created_by = ForeignKeyField(Account, null=True, backref='created_localities')
    modified_by = ForeignKeyField(Account, null=True, backref='modified_localities')
    active = BooleanField(default=True)


class Substation(BaseModel):
    id = UUIDField(primary_key=True, default=uuid.uuid4)
    locality = ForeignKeyField(Locality, backref='substations')
    name = CharField(max_length=100)
    created_on = DateTimeField(default=datetime.datetime.utcnow)
    modified_on = DateTimeField(default=datetime.datetime.utcnow)
    created_by = ForeignKeyField(Account, null=True, backref='created_substations')
    modified_by = ForeignKeyField(Account, null=True, backref='modified_substations')
    active = BooleanField(default=True)


class Transformer(BaseModel):
    id = UUIDField(primary_key=True, default=uuid.uuid4)
    substation = ForeignKeyField(Substation, backref='transformers')
    max_capacity_kw = DecimalField(max_digits=10, decimal_places=2)
    export_efficiency = DecimalField(max_digits=5, decimal_places=2, null=True)
    allow_export = BooleanField(default=False)
    created_on = DateTimeField(default=datetime.datetime.utcnow)
    modified_on = DateTimeField(default=datetime.datetime.utcnow)
    created_by = ForeignKeyField(Account, null=True, backref='created_transformers')
    modified_by = ForeignKeyField(Account, null=True, backref='modified_transformers')
    active = BooleanField(default=True)


class House(BaseModel):
    id = UUIDField(primary_key=True, default=uuid.uuid4)
    transformer = ForeignKeyField(Transformer, backref='houses')
    load_profile = TextField(null=True)
    has_solar = BooleanField(default=False)
    solar_kw = DecimalField(max_digits=10, decimal_places=2, null=True)
    house_type = CharField(max_length=50, null=True)
    connection_kw = DecimalField(max_digits=10, decimal_places=2, null=True)
    has_battery = BooleanField(default=False)
    battery_type = CharField(max_length=50, null=True)
    battery_kind = CharField(max_length=50, null=True)
    battery_peak_charging_rate = DecimalField(max_digits=10, decimal_places=2, null=True)
    battery_peak_discharging_rate = DecimalField(max_digits=10, decimal_places=2, null=True)
    battery_total_kwh = DecimalField(max_digits=10, decimal_places=2, null=True)
    created_on = DateTimeField(default=datetime.datetime.utcnow)
    modified_on = DateTimeField(default=datetime.datetime.utcnow)
    created_by = ForeignKeyField(Account, null=True, backref='created_houses')
    modified_by = ForeignKeyField(Account, null=True, backref='modified_houses')
    active = BooleanField(default=True)
