"""Interfaces for configuration settings."""

from abc import ABC, abstractmethod
from dataclasses import dataclass
from typing import Any, List, Optional

from app.domain.interfaces.enums.load_profile_strategy_enum import (
    LoadProfileStrategy,
)


@dataclass(frozen=True)
class DbConfig:
    """Database configuration settings."""

    max_connections: int
    stale_timeout: int
    host: str
    port: int
    database: str
    user: str
    password: str
    options: Optional[str]


@dataclass(frozen=True)
class LoggingConfig:
    """Logging configuration settings."""

    level: str
    log_directory: str
    system_user_id: str


@dataclass(frozen=True)
class SessionConfig:
    """Session configuration settings."""

    session_token_secret: str
    session_validity_in_hours: int
    session_validity_in_hours_refresh_token: int


@dataclass(frozen=True)
class OTPConfig:
    """OTP configuration settings."""

    max_otp_verification_attempts: int
    max_resend_otp_attempts: int
    max_resend_otp_attempt_window_in_min: int
    otp_validity_in_secs: int
    master_otp_admin: int
    master_otp_user: int
    admin_number: int
    user_number: int


@dataclass(frozen=True)
class SMSConfig:
    """SMS configuration settings."""

    sms_provider_server: str
    api_key: str
    otp_sms_template_name: str
    default_number: str
    topic: str


@dataclass(frozen=True)
class MqttConfig:
    """MQTT configuration settings."""

    id: str
    broken_url: str
    application_name: str
    host: str
    port: int
    username: str
    password: str


@dataclass(frozen=True)
class SimulationConfig:
    """Simulation configuration settings."""

    initial_battery_soc: float
    solar_peak_percentage_for_charging: float
    load_peak_percentage_for_discharging: float
    charge_battery_efficiency: float
    discharge_battery_efficiency: float
    default_panel_capacity: float
    default_battery_capacity_required: float
    battery_dynamic_percentage_allocation: float
    battery_base_percentage_allocation: float
    battery_dynamic_allocation: Optional[float] = None
    battery_base_allocation: Optional[float] = None


@dataclass(frozen=True)
class CorsConfig:
    """CORS configuration settings."""

    origins: List[str]
    methods: List[str]
    headers: List[str]
    allow_credentials: bool


@dataclass(frozen=True)
class LoadProfileConfig:
    """Load profile configuration settings."""

    interpolation_strategy: LoadProfileStrategy
    max_interval_length: int
    min_days: int
    time_formats: Optional[str]


@dataclass(frozen=True)
class TopicConfig:
    """Topic configuration settings."""

    topics: List[str]


class IConfiguration(ABC):
    """Abstract base class for application configuration."""

    @property
    @abstractmethod
    def db(self) -> DbConfig:
        """Database configuration"""

    @property
    @abstractmethod
    def simulation(self) -> SimulationConfig:
        """Simulation configuration"""

    @property
    @abstractmethod
    def logging(self) -> LoggingConfig:
        """Logging configuration"""

    @property
    @abstractmethod
    def session(self) -> SessionConfig:
        """Session configuration"""

    @property
    @abstractmethod
    def otp(self) -> OTPConfig:
        """OTP configuration"""

    @property
    @abstractmethod
    def sms(self) -> SMSConfig:
        """SMS configuration"""

    @property
    @abstractmethod
    def mqtt(self) -> MqttConfig:
        """MQTT configuration"""

    @property
    @abstractmethod
    def cors(self) -> CorsConfig:
        """CORS configuration"""

    @property
    @abstractmethod
    def load_profile(self) -> LoadProfileConfig:
        """Load profile configuration"""

    @property
    @abstractmethod
    def topic(self) -> Optional[TopicConfig]:
        """Topic configuration"""

    @abstractmethod
    def get(self, setting: str, default: Any = None) -> Any:
        """Method to get a setting value with an optional default"""
