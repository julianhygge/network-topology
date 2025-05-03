"""Configuration for the API."""

import glob
import os
from typing import Any, Optional

from dynaconf import Dynaconf

from app.config.i_configuration import (CorsConfig, DbConfig, IConfiguration,
                                        LoadProfileConfig, LoadProfileStrategy,
                                        LoggingConfig, MQTTConfig, OTPConfig,
                                        SessionConfig, SimulationConfig,
                                        SMSConfig, TopicConfig)


class ApiConfiguration(IConfiguration):
    """
    Implementation of IConfiguration using Dynaconf for loading settings.
    """
    _settings: Dynaconf

    def __init__(self):
        current_dir = os.path.dirname(os.path.abspath(__file__))
        config_dir = os.path.dirname(current_dir)
        project_root = os.path.dirname(config_dir)
        config_files_path = os.path.join(project_root, "config", "*.toml")
        files = glob.glob(config_files_path)

        if not files:
            files = glob.glob(os.path.join(current_dir, "*.toml"))

        self._settings = Dynaconf(
            settings_files=files,
            envvar_prefix="HYGGE",
            default_env="local",
            merge_enabled=True,
            load_dotenv=True,
            env_switcher="ENV_FOR_DYNACONF",
            environments=True,
        )

    @property
    def db(self) -> DbConfig:
        s = self._settings
        return DbConfig(
            max_connections=int(s.get("db_max_connections")),
            stale_timeout=int(s.get("db_stale_timeout")),
            host=s.get("db_host"),
            port=int(s.get("db_port")),
            database=s.get("db_database"),
            user=s.get("db_user"),
            password=s.get("db_password"),
            options=s.get("db_options")
        )

    @property
    def logging(self) -> LoggingConfig:
        s = self._settings
        return LoggingConfig(
            level=s.get("logging_level"),
            log_directory=s.get("log_directory"),
            system_user_id=s.get("logging_system_user_id"),
        )

    @property
    def session(self) -> SessionConfig:
        s = self._settings
        secret = s.get("session_token_secret") or s.get("session.session_token_secret")
        return SessionConfig(
            session_token_secret=secret,
            session_validity_in_hours=int(s.get("session_validity_in_hours")),
            session_validity_in_hours_refresh_token=int(
                s.get("session_validity_in_hours_refresh_token")
            ),
        )

    @property
    def otp(self) -> OTPConfig:
        s = self._settings
        return OTPConfig(
            max_otp_verification_attempts=int(
                s.get("otp_max_otp_verification_attempts")
            ),
            max_resend_otp_attempts=int(s.get("otp_max_resend_otp_attempts")),
            max_resend_otp_attempt_window_in_min=int(
                s.get("otp_max_resend_otp_attempt_window_in_min")
            ),
            otp_validity_in_secs=int(s.get("otp_validity_in_secs")),
            master_otp_admin=int(s.get("otp_master_otp_admin")),
            master_otp_user=int(s.get("otp_master_otp_user")),
            admin_number=int(s.get("otp_admin_number")),
            user_number=int(s.get("otp_user_number")),
        )

    @property
    def sms(self) -> SMSConfig:
        s = self._settings
        return SMSConfig(
            sms_provider_server=s.get("sms_provider_server"),
            api_key=s.get("sms_api_key"),
            otp_sms_template_name=s.get("sms_otp_sms_template_name"),
            default_number=s.get("sms_default_number"),
            topic=s.get("sms_topic"),
        )

    @property
    def mqtt(self) -> MQTTConfig:
        s = self._settings
        return MQTTConfig(
            id=s.get("mqtt_id"),
            broken_url=s.get("mqtt_broken_url"),
            application_name=s.get("mqtt_application_name"),
            host=s.get("mqtt_host"),
            port=int(s.get("mqtt_port")),
            username=s.get("mqtt_username"),
            password=s.get("mqtt_password")
        )

    @property
    def simulation(self) -> SimulationConfig:
        s = self._settings
        dyn_alloc_old = s.get("simulation_battery_dynamic_allocation")
        base_alloc_old = s.get("simulation_battery_base_allocation")

        return SimulationConfig(
            initial_battery_soc=float(s.get("simulation_initial_battery_soc")),
            solar_peak_percentage_for_charging=float(
                s.get("simulation_solar_peak_percentage_for_charging")
            ),
            load_peak_percentage_for_discharging=float(
                s.get("simulation_load_peak_percentage_for_discharging")
            ),
            charge_battery_efficiency=float(
                s.get("simulation_charge_battery_efficiency")
            ),
            discharge_battery_efficiency=float(
                s.get("simulation_discharge_battery_efficiency")
            ),
            default_panel_capacity=float(s.get("simulation_default_panel_capacity")),
            default_battery_capacity_required=float(
                s.get("simulation_default_battery_capacity_required")
            ),
            battery_dynamic_percentage_allocation=float(
                s.get("simulation_battery_dynamic_percentage_allocation")
            ),
            battery_base_percentage_allocation=float(
                s.get("simulation_battery_base_percentage_allocation")
            ),
            battery_dynamic_allocation=float(dyn_alloc_old)
            if dyn_alloc_old is not None
            else None,
            battery_base_allocation=float(base_alloc_old)
            if base_alloc_old is not None
            else None,
        )

    @property
    def cors(self) -> CorsConfig:
        s = self._settings
        return CorsConfig(
            origins=s.cors_origins,
            methods=s.cors_methods,
            headers=s.cors_headers,
            allow_credentials=bool(s.cors_allow_credentials)
        )

    @property
    def load_profile(self) -> LoadProfileConfig:
        s = self._settings
        strategy_str = s.get("load_profile_interpolation_strategy")
        strategy_enum = LoadProfileStrategy.Linear

        if strategy_str:
            try:
                strategy_enum = LoadProfileStrategy(strategy_str)
            except ValueError:
                print(
                    "Warning: Invalid load_profile_interpolation_strategy "
                    f"'{strategy_str}'. Using default."
                )

        return LoadProfileConfig(
            interpolation_strategy=strategy_enum,
            max_interval_length=int(s.get("load_profile_max_interval_length")),
            min_days=int(s.get("load_profile_min_days")),
            time_formats=s.get("load_profile_time_formats")
        )

    @property
    def topic(self) -> Optional[TopicConfig]:
        s = self._settings
        topics_str = s.get("topic_topics")
        if topics_str is not None:
            topics_list = [t.strip() for t in topics_str.split(",")]
            return TopicConfig(topics=topics_list)
        return None

    def get(self, setting: str, default: Any = None) -> Any:
        return self._settings.get(setting, default)
