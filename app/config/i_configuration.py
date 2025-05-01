from abc import ABC, abstractmethod


class IConfiguration(ABC):

    @property
    @abstractmethod
    def db(self):
        """Database configuration"""
        pass

    @property
    @abstractmethod
    def simulation(self):
        """Simulation configuration"""
        pass

    @property
    @abstractmethod
    def logging(self):
        """Logging configuration"""
        pass

    @property
    @abstractmethod
    def session_secret(self):
        """Token configuration"""
        pass

    @property
    @abstractmethod
    def otp(self):
        """OTP configuration"""
        pass

    @property
    @abstractmethod
    def sms(self):
        """SMS configuration"""
        pass

    @property
    @abstractmethod
    def mqtt(self):
        """MQTT configuration"""
        pass

    @property
    @abstractmethod
    def cors(self):
        """CORS configuration"""
        pass

    @abstractmethod
    def get(self, setting, default=None):
        """Method to get a setting value with an optional default"""
        pass

    @property
    @abstractmethod
    def load_profile(self):
        """Load profile configuration"""
        pass
