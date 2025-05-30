import jwt
from jwt import ExpiredSignatureError

from app.api.authorization.enums import Permission
from app.config.i_configuration import IConfiguration
from app.data.interfaces.i_group_repository import IGroupRepository
from app.data.interfaces.i_repository import IRepository
from app.domain.interfaces.auth.i_token_service import ITokenService
from app.utils.datetime_util import (
    after_now,
    current_time_millis,
    utc_now,
    utc_now_iso,
)
from app.utils.json_util import UUIDEncoder
from app.utils.logger import logger


class TokenService(ITokenService):
    def __init__(
        self,
        configuration: IConfiguration,
        account_repo: IRepository,
        group_repo: IGroupRepository,
    ):
        self._session_token_secret = configuration.session.session_token_secret
        self._session_validity_in_hours = int(
            configuration.session.session_validity_in_hours
        )
        self._session_validity_in_hours_refresh_token = int(
            configuration.session.session_validity_in_hours_refresh_token
        )
        self._account_repo = account_repo
        self._group_repo = group_repo

    def issue_new_token(self, session_user, txn_id):
        query = self._group_repo.fetch_roles_and_permissions_by_groups(
            session_user=session_user, now=utc_now_iso()
        )
        roles = set([])
        permissions = set([])
        for rec in query:
            roles.add(rec.group_role_rel.role.name.value)
            permissions.update(
                self._resolve_permission(
                    rec.group_role_rel.role.role_permission_rel.permission
                )
            )

        payload = {
            "iat": utc_now(),  # issued_at
            "jti": txn_id,  # unique_identifier
            "exp": after_now(
                hours=self._session_validity_in_hours
            ),  # expiration_time
            "user": str(session_user),
            "role": list(roles),
            "permissions": list(permissions),
        }
        return jwt.encode(
            payload,
            self._session_token_secret,
            algorithm="HS256",
            json_encoder=UUIDEncoder,
        )

    def decode_token(self, jwt_token, verify_expiry=True):
        return jwt.decode(
            (jwt_token + "=" * (-len(jwt_token) % 4)),
            self._session_token_secret,
            algorithms=["HS256"],
            options={"verify_exp": verify_expiry},
        )

    def issue_refresh_token(self, user_id):
        user_record = self._account_repo.read(user_id)
        payload = {
            "iat": utc_now_iso(),  # issued_at
            "exp": after_now(
                hours=self._session_validity_in_hours_refresh_token
            ),  # expiration_time
            "user": user_record.id,
            "phoneNumber": user_record.phone_number,
        }
        return jwt.encode(
            payload,
            self._session_token_secret,
            algorithm="HS256",
            json_encoder=UUIDEncoder,
        )

    @staticmethod
    def validate_token_claims(claims):
        if claims is None:
            raise ExpiredSignatureError()

        logger.debug("claims time " + str(claims.get("exp")))
        logger.debug("current time " + str(current_time_millis()))
        if (
            claims.get("user") is None
            or current_time_millis() > claims.get("exp") * 1000
        ):
            raise ExpiredSignatureError()

    @staticmethod
    def _resolve_permission(permission):
        permissions = []
        if permission.can_create:
            permissions.append(
                Permission.CREATE.value + "-" + permission.resource_name
            )
        if permission.can_retrieve:
            permissions.append(
                Permission.RETRIEVE.value + "-" + permission.resource_name
            )
        if permission.can_update:
            permissions.append(
                Permission.UPDATE.value + "-" + permission.resource_name
            )
        if permission.can_delete:
            permissions.append(
                Permission.DELETE.value + "-" + permission.resource_name
            )
        if permission.can_search:
            permissions.append(
                Permission.SEARCH.value + "-" + permission.resource_name
            )
        return permissions
