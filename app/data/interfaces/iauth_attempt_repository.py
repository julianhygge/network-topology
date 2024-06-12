from abc import abstractmethod
from app.data.interfaces.irepository import IRepository, T


class IAuthAttemptRepository(IRepository[T]):
    @abstractmethod
    def fetch_all_previous_records_for_user(self, phone_number, records_after_time):
        """ Fetch all Previous otp attempts"""

