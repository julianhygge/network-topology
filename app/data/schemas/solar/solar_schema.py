"""Solar profile schema."""

from peewee import (
    AutoField,
    BooleanField,
    CharField,
    DateTimeField,
    DoubleField,
    ForeignKeyField,
    IntegerField,
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
    installed_capacity_kw = DoubleField()
    tilt_type = CharField(max_length=12)
    years_since_installation = DoubleField()
    simulate_using_different_capacity = BooleanField(null=True)
    capacity_for_simulation_kw = DoubleField()
    available_space_sqft = DoubleField()
    simulated_available_space_sqft = DoubleField()

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


class SolarInstallation(BaseModel):
    site_id = IntegerField(primary_key=True)
    name = CharField()
    status = CharField()
    peak_power = DoubleField()
    type = CharField()
    zip_code = CharField()
    country = CharField()
    address = CharField()
    state = CharField()
    city = CharField()
    installation_date = CharField()
    last_reporting_time = CharField()
    location = CharField()
    secondary_address = CharField()
    uploaded_on = DateTimeField()
    profile_updated_on = DateTimeField()
    updated_on = DateTimeField()
    has_csv = BooleanField()

    class Meta:
        table_name = "solar_installations"
        schema = "solar"


class SiteRefYearProduction(BaseModel):
    """
    Schema for storing reference year production data for solar installations.
    """

    id = AutoField()
    site = ForeignKeyField(
        SolarInstallation,
        backref="reference_year_productions",
        on_delete="CASCADE",
        column_name="site_id",
    )
    timestamp = DateTimeField()
    per_kw_generation = DoubleField()

    class Meta:
        """Metaclass for SiteReferenceYearProduction."""

        table_name = "site_reference_year_production"
        schema = "solar"
        indexes = ((("site", "reference_timestamp"), True),)
