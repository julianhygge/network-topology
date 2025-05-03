import datetime

from peewee import (BooleanField, CharField, DateTimeField, ForeignKeyField,
                    UUIDField)

from app.data.schemas.schema_base import BaseModel, InfDateTimeField


class Account(BaseModel):
    id = UUIDField(primary_key=True)
    active = BooleanField(default=True)
    alias_name = CharField(max_length=50, null=True)
    phone_number = CharField(max_length=12)
    type = CharField(max_length=50)
    validity_start = DateTimeField(default=datetime.datetime.utcnow)
    validity_end = InfDateTimeField(default=datetime.datetime.max)
    record_id = ForeignKeyField('self', lazy_load=False, backref='accounts', column_name='record_id')
    created_on = DateTimeField(default=datetime.datetime.utcnow)
    modified_on = DateTimeField(default=datetime.datetime.utcnow)
    created_by = ForeignKeyField('self', backref='created', on_delete='SET NULL', lazy_load=False,
                                 column_name='created_by')
    modified_by = ForeignKeyField('self', backref='modified', on_delete='SET NULL', lazy_load=False,
                                  column_name='modified_by')

    class Meta:
        table_name = 'accounts'
        schema = 'transactional'


class User(BaseModel):
    id = UUIDField(primary_key=True)
    active = BooleanField(default=True)
    phone_number = CharField(max_length=12)
    user_name = CharField(max_length=50)
    name = CharField(max_length=50)
    last_name = CharField(max_length=50)
    validity_start = DateTimeField(default=datetime.datetime.utcnow)
    validity_end = InfDateTimeField(default=datetime.datetime.max)
    locality = CharField(max_length=50)
    country_code = CharField(max_length=50)
    state = CharField(max_length=50)
    email = CharField(max_length=50)
    address = CharField(max_length=50, null=True)
    record_id = ForeignKeyField('self', lazy_load=False, backref='accounts', column_name='record_id')
    created_on = DateTimeField(default=datetime.datetime.utcnow)
    modified_on = DateTimeField(default=datetime.datetime.utcnow)
    created_by = ForeignKeyField('self', backref='created', on_delete='SET NULL', lazy_load=False,
                                 column_name='created_by')
    modified_by = ForeignKeyField('self', backref='modified', on_delete='SET NULL', lazy_load=False,
                                  column_name='modified_by')
    meter_number = CharField(max_length=50)
    connection_number = CharField(max_length=50)
    utility_id = UUIDField()
    pin_code = CharField(max_length=8)

    class Meta:
        table_name = 'users'
        schema = 'transactional'
