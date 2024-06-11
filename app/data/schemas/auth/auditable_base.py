import datetime
from peewee import DateTimeField, ForeignKeyField
from app.data.schemas.schema_base import BaseModel
from app.data.schemas.transactional.user_schema import User

class AuditableBase(BaseModel):
    created_on = DateTimeField(default=datetime.datetime.utcnow)
    modified_on = DateTimeField(default=datetime.datetime.utcnow)
    created_by = ForeignKeyField(User, null=True, backref='created', on_delete='SET NULL', column_name='created_by')
    modified_by = ForeignKeyField(User, null=True, backref='modified', on_delete='SET NULL', column_name='modified_by')

    class Meta:
        abstract = True
