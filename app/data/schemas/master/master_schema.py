import datetime

from peewee import (
    BooleanField,
    CharField,
    DateTimeField,
    DoubleField,
    ForeignKeyField,
    PrimaryKeyField,
)

from app.data.schemas.schema_base import BaseModel
from app.data.schemas.transactional.user_schema import User


class ElectricalAppliances(BaseModel):
    id = PrimaryKeyField()
    name = CharField(max_length=50)
    active = BooleanField(default=True)
    created_on = DateTimeField(default=datetime.datetime.utcnow)
    modified_on = DateTimeField(default=datetime.datetime.utcnow)
    created_by = ForeignKeyField(
        User,
        backref="created",
        on_delete="SET NULL",
        lazy_load=False,
        column_name="created_by",
    )
    modified_by = ForeignKeyField(
        User,
        backref="modified",
        on_delete="SET NULL",
        lazy_load=False,
        column_name="modified_by",
    )

    class Meta:
        schema = "master"
        table_name = "electrical_appliances"


class PredefinedTemplates(BaseModel):
    id = PrimaryKeyField()
    name = CharField(max_length=50)
    active = BooleanField(default=True)
    created_by = ForeignKeyField(
        User,
        backref="created",
        on_delete="SET NULL",
        lazy_load=False,
        column_name="created_by",
    )
    modified_by = ForeignKeyField(
        User,
        backref="modified",
        on_delete="SET NULL",
        lazy_load=False,
        column_name="modified_by",
    )
    created_on = DateTimeField(default=datetime.datetime.utcnow)
    modified_on = DateTimeField(default=datetime.datetime.utcnow)
    power_kw = DoubleField(null=True)

    class Meta:
        schema = "master"
        table_name = "predefined_templates"
