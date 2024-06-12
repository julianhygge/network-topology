from abc import ABC, abstractmethod


class IAuthService(ABC):

    @abstractmethod
    def get_registered_user(self, phone_number):
        """ Get the Registered user """

    @abstractmethod
    def request_otp(self, user, country_code):
        """Request OTP"""

    @abstractmethod
    def verify_otp(self, req_body, txn_id):
        """Verify Otp"""
