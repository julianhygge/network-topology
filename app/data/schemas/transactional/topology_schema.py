"""Defines the Peewee ORM models for transactional topology data."""

import uuid

from peewee import (
    AutoField,
    BooleanField,
    CharField,
    DecimalField,
    ForeignKeyField,
    IntegerField,
    TextField,
    UUIDField,
)

from app.data.schemas.auth.auditable_base import AuditableBase
from app.data.schemas.schema_base import InfDateTimeField


class Transactional(AuditableBase):
    """
    Base model for transactional tables in the 'transactional' schema.
    Inherits auditable fields and includes a UUID primary key and an
    active status.
    """

    id = UUIDField(primary_key=True, default=uuid.uuid4)
    active = BooleanField()

    class Meta:
        schema = "transactional"


class Account(Transactional):
    """
    Represents an account in the system, linked to a record_id.
    Includes validity period, alias, type, and phone number.
    """

    validity_start = InfDateTimeField()
    validity_end = InfDateTimeField()
    record_id = UUIDField()
    alias_name = CharField(max_length=50, null=True)
    type = CharField(max_length=50, null=True)
    phone_number = CharField(max_length=12, default="8429020287")

    class Meta:
        table_name = "accounts"


class Locality(Transactional):
    """Represents a geographical locality."""

    name = CharField(max_length=100)
    id = UUIDField(primary_key=True, default=uuid.uuid4)

    class Meta:
        table_name = "localities"


class Substation(Transactional):
    """Represents a substation, linked to a locality."""

    id = UUIDField(primary_key=True, default=uuid.uuid4)
    locality = ForeignKeyField(Locality, backref="substations")
    name = CharField(max_length=100)

    class Meta:
        table_name = "substations"


class Node(Transactional):
    """
    Represents a node in the network topology.
    Nodes can be hierarchical (parent-child) and are associated with a type
    (substation', 'transformer', 'house') and optionally a substation.
    """

    parent = ForeignKeyField("self", backref="children", null=True)
    node_type = CharField(
        max_length=50
    )  # 'substation', 'transformer', or 'house'
    name = CharField(max_length=50, null=True)  # Optional name for substations
    nomenclature = CharField(
        max_length=50, null=True
    )  # Optional name for substations
    substation = ForeignKeyField(Substation, backref="nodes", null=True)

    class Meta:
        table_name = "nodes"


class Transformer(Transactional):
    """
    Represents a transformer in the network topology.
    Linked to a node and includes electrical characteristics and
    operational data.
    """

    node = ForeignKeyField(Node, backref="transformers", null=True)
    max_capacity_kw = DecimalField(max_digits=10, decimal_places=2)
    allow_export = BooleanField(default=False)
    name = CharField(max_length=255, null=True)
    backward_efficiency = DecimalField(
        max_digits=5, decimal_places=2, null=True
    )
    primary_ampacity = DecimalField(max_digits=5, decimal_places=2, null=True)
    secondary_ampacity = DecimalField(
        max_digits=5, decimal_places=2, null=True
    )
    years_of_service = IntegerField(null=True)
    forward_efficiency = DecimalField(
        max_digits=5, decimal_places=2, null=True
    )
    digital_twin_model = BooleanField(default=False)

    class Meta:
        table_name = "transformers"


class House(Transactional):
    """
    Represents a house in the network topology.
    Linked to a node and includes details about its load profile, solar
    generation capacity, battery storage, and connection parameters.
    """

    node = ForeignKeyField(
        Node, backref="houses", null=True, on_delete="CASCADE"
    )
    load_profile = TextField(null=True)
    has_solar = BooleanField(default=False)
    solar_kw = DecimalField(max_digits=10, decimal_places=2, null=True)
    house_type = CharField(max_length=50, null=True)
    connection_kw = DecimalField(max_digits=10, decimal_places=2, null=True)
    has_battery = BooleanField(default=False)
    battery_type = CharField(max_length=50, null=True)
    voluntary_storage = BooleanField()
    battery_peak_charging_rate = DecimalField(
        max_digits=10, decimal_places=2, null=True
    )
    battery_peak_discharging_rate = DecimalField(
        max_digits=10, decimal_places=2, null=True
    )
    battery_total_kwh = DecimalField(
        max_digits=10, decimal_places=2, null=True
    )

    class Meta:
        table_name = "houses"


class HouseFlag(Transactional):
    """
    Represents specific flags or attributes associated with a house.
    Each flag has a type and a value.
    """

    id = AutoField()
    house = ForeignKeyField(
        House, backref="flags", null=True, on_delete="CASCADE"
    )
    flag_type = CharField(max_length=50, null=True)
    flag_value = CharField(max_length=50, null=True)

    class Meta:
        schema = "transactional"
        table_name = "house_flags"
