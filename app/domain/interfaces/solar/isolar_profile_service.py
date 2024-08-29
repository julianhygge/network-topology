from abc import ABC, abstractmethod


class ISolarProfileService(ABC):

    @abstractmethod
    def create(self, user_id, **data):
        """Create Solar Profile"""

    @abstractmethod
    def get_solar_profile_by_house_id(self, house_id):
        """Get Solar Profile"""

    @abstractmethod
    def delete_solar_profile_by_house_id(self, house_id):
        """Delete solar Profile"""

    @abstractmethod
    def update_solar_profile(self, user_id, house_id, **data):
        """Update Solar Profile"""
