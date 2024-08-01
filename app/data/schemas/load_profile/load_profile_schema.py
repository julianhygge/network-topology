from peewee import ForeignKeyField, CharField, BooleanField, IntegerField, DateTimeField, DoubleField, BlobField, \
    DecimalField
from app.data.schemas.auth.auditable_base import AuditableBase
from app.data.schemas.master.master_schema import ElectricalAppliances, PredefinedTemplates
from app.data.schemas.schema_base import BaseModel
from app.data.schemas.transactional.topology_schema import Node
from app.data.schemas.transactional.user_schema import User


class LoadProfileAuditableBase(AuditableBase):
    active = BooleanField()

    class Meta:
        schema = 'load'
        abstract = True


class LoadProfileBase(BaseModel):
    class Meta:
        schema = 'load'
        abstract = True


class LoadProfiles(LoadProfileAuditableBase):
    id = IntegerField(primary_key=True)
    user_id = ForeignKeyField(User, backref='load_profiles')
    house_id = ForeignKeyField(Node, backref='load_profiles', on_delete='CASCADE')
    profile_name = CharField(max_length=50)
    source = CharField(max_length=50)
    public = BooleanField()

    class Meta:
        table_name = 'load_profiles'


class LoadProfileDetails(LoadProfileBase):
    id = IntegerField(primary_key=True)
    profile_id = ForeignKeyField(LoadProfiles, backref='details')
    timestamp = DateTimeField()
    consumption_kwh = DoubleField()

    class Meta:
        table_name = 'load_profile_details'


class LoadProfileFiles(LoadProfileBase):
    id = IntegerField(primary_key=True)
    profile_id = ForeignKeyField(LoadProfiles, backref='files', on_delete='CASCADE')
    filename = CharField(max_length=255)
    content = BlobField()

    class Meta:
        table_name = 'load_profile_files'


class LoadProfileBuilderItems(LoadProfileAuditableBase):
    id = IntegerField(primary_key=True)
    profile_id = ForeignKeyField(LoadProfiles, backref='builder_items', on_delete='CASCADE')
    electrical_device_id = ForeignKeyField(ElectricalAppliances, backref='builder_items', on_delete='CASCADE')
    rating_watts = IntegerField()
    quantity = IntegerField()
    hours = IntegerField()

    class Meta:
        table_name = 'load_profile_builder_items'


class LoadGenerationEngine(AuditableBase):
    id = IntegerField(primary_key=True)
    user_id = ForeignKeyField(User, backref='load_generation_engines')
    profile_id = ForeignKeyField(LoadProfiles, backref='load_generation_engines')
    type = CharField(max_length=7)
    average_kwh = DecimalField()
    average_monthly_bill = DecimalField()
    max_demand_kw = DecimalField()

    class Meta:
        table_name = 'load_generation_engine'
        schema = 'load'


class LoadPredefinedTemplates(LoadProfileBase):
    id = IntegerField(primary_key=True)
    profile_id = ForeignKeyField(LoadProfiles, backref='predefined_templates')
    template_id = ForeignKeyField(PredefinedTemplates, backref='load_templates')

    class Meta:
        table_name = 'load_predefined_templates'
        schema = 'load'
