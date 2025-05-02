from abc import ABC, abstractmethod


class ITokenService(ABC):
    @abstractmethod
    def issue_new_token(self, session_user, txn_id):
        """"""

    @abstractmethod
    def decode_token(self, jwt_token, verify_expiry=True):
        """"""

    @abstractmethod
    def issue_refresh_token(self, user_id):
        """"""

    @staticmethod
    def validate_token_claims(claims):
        """"""
