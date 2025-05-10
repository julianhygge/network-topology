import datetime
import enum

from peewee import (
    BigAutoField,
    BooleanField,
    CharField,
    CompositeKey,
    DateTimeField,
    DeferredThroughModel,
    ForeignKeyField,
    IntegerField,
    ManyToManyField,
    UUIDField,
)
from playhouse.postgres_ext import BinaryJSONField

from app.data.schemas.enums.enums import EnumField, UserRoles
from app.data.schemas.schema_base import BaseModel, InfDateTimeField
from app.data.schemas.transactional.user_schema import User
from app.utils.datetime_util import utc_now_iso


class AuthBase(BaseModel):
    class Meta:
        schema = "communication"
        abstract = True


class Permissions(AuthBase):
    id = BigAutoField(primary_key=True)
    name = CharField(
        unique=True
    )  # format: can-create-resource, can-retrieve-update-big_resource
    description = CharField(null=True, max_length=100)
    resource_name = CharField(max_length=100)
    can_retrieve = BooleanField(default=False)
    can_search = BooleanField(default=False)
    can_create = BooleanField(default=False)
    can_update = BooleanField(default=False)
    can_delete = BooleanField(default=False)


RolePermissionRelDeferred = DeferredThroughModel()


class Roles(AuthBase):
    id = BigAutoField(primary_key=True)
    name = EnumField(unique=True, enum_class=UserRoles)
    description = CharField(null=True, max_length=100)
    permissions = ManyToManyField(
        Permissions, through_model=RolePermissionRelDeferred
    )

    class Meta:
        table_name = "roles"


class RolePermissionRel(AuthBase):
    role = ForeignKeyField(
        Roles, column_name="role_id", backref="permissions", lazy_load=False
    )
    permission = ForeignKeyField(
        Permissions, column_name="permission_id", lazy_load=False
    )

    class Meta:
        primary_key = CompositeKey("role", "permission")
        table_name = "role_permission_rel"


RolePermissionRelDeferred.set_model(RolePermissionRel)
RoleGroupRelDeferred = DeferredThroughModel()


class Groups(AuthBase):
    id = BigAutoField(primary_key=True)
    name = CharField(max_length=50)
    description = CharField(null=True, max_length=100)
    roles = ManyToManyField(Roles, through_model=RoleGroupRelDeferred)

    class Meta:
        table_name = "groups"


class GroupRoleRel(AuthBase):
    group = ForeignKeyField(
        Groups, column_name="group_id", backref="roles", lazy_load=False
    )
    role = ForeignKeyField(Roles, column_name="role_id", lazy_load=False)

    class Meta:
        primary_key = CompositeKey("group", "role")
        table_name = "group_role_rel"


RoleGroupRelDeferred.set_model(GroupRoleRel)


class UserGroupRel(AuthBase):
    id = BigAutoField(primary_key=True)
    record_id = UUIDField()
    active = BooleanField(default=True)
    user_record_id = UUIDField()
    group_id = IntegerField()
    validity_start = DateTimeField(default=utc_now_iso())
    validity_end = InfDateTimeField(default=utc_now_iso())
    created_on = DateTimeField(default=utc_now_iso())
    modified_on = DateTimeField(default=utc_now_iso())
    created_by = UUIDField()
    modified_by = UUIDField()

    class Meta:
        table_name = "user_group_rel"


class AuthenticationState(enum.Enum):
    Unauthorized = "UNAUTHENTICATED"
    OtpRequired = "OTP_REQUIRED"
    OtpFailed = "OTP_FAILED"
    OtpRestricted = "OTP_RESTRICTED"
    Restricted = "RESTRICTED"
    Discarded = "DISCARDED"
    RefreshFailed = "REFRESH_FAILED"
    Success = "SUCCESS"
    OtpSendFailed = "OTP_SEND_FAILED"


class AuthAttempts(AuthBase):
    txn_id = UUIDField(primary_key=True)
    phone_number = CharField(max_length=12)
    country_code = CharField(max_length=4, null=True)
    otp = CharField(max_length=6, null=True)
    state = EnumField(enum_class=AuthenticationState)
    state_desc = CharField(max_length=100)
    verification_attempt_count = IntegerField(default=0)
    gateway_send_otp_res_status = CharField(
        max_length=10, null=True
    )  # status code of sms gateway api call
    gateway_send_otp_res_body = (
        BinaryJSONField()
    )  # response of sms gateway api call
    claims_issued = CharField(
        null=True, max_length=100
    )  # todo: not sure what to put
    backing_txn_id = UUIDField(null=True)
    created_on = DateTimeField(default=datetime.datetime.utcnow)
    modified_on = DateTimeField(default=datetime.datetime.utcnow)
    created_by = ForeignKeyField(
        User, backref="created", on_delete="SET NULL", column_name="created_by"
    )
    modified_by = ForeignKeyField(
        User,
        backref="modified",
        on_delete="SET NULL",
        column_name="modified_by",
    )

    class Meta:
        table_name = "auth_attempts"


class AuthenticatedSessions(AuthBase):
    id = UUIDField(primary_key=True)
    record_id = ForeignKeyField(
        "self", column_name="record_id", lazy_load=False
    )
    user = ForeignKeyField(User, column_name="user_record_id", lazy_load=False)
    group_id = ForeignKeyField(Groups, column_name="group_id", lazy_load=False)
    relative_auth_attempt = ForeignKeyField(
        AuthAttempts, column_name="auth_attempt_id", lazy_load=False
    )
    validity_start = DateTimeField(default=datetime.datetime.utcnow)
    validity_end = InfDateTimeField(default=datetime.datetime.max)
