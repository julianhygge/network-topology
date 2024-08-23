import os
from pathlib import Path
import dynaconf
from app.domain.interfaces.enums.load_profile_strategy_enum import LoadProfileStrategy
from logging import getLogger


class Singleton(type):
    _instances = {}

    def __call__(cls, *args, **kwargs):
        app_env = kwargs.get("app_env", None)
        key = (cls, app_env)

        if key not in cls._instances:
            cls._instances[key] = super(Singleton, cls).__call__(*args, **kwargs)
        return cls._instances[key]


class ApiConfiguration(metaclass=Singleton):

    def __init__(self, app_env=None):
        if app_env is None:
            app_env = os.environ.get("APP_ENV") or "local"
        base_dir = Path(__file__).resolve().parent.parent
        config_file_path = base_dir / "config" / "{}.ini".format(app_env)

        self.settings = dynaconf.Dynaconf(
            envvar_prefix="DYNACONF", settings_files=[config_file_path]
        )

    @property
    def db(self):
        return self._get_postgres_config()

    @property
    def logging(self):
        return self.get("logging")

    @property
    def session_secret(self):
        return self.get("session")

    @property
    def otp(self):
        return self._get_otp_config()

    @property
    def sms(self):
        return self.get("sms")

    @property
    def mqtt(self):
        return self.get("mqtt")

    @property
    def simulation(self):
        return self._get_simulation_config()

    @property
    def cors(self):
        return self.get("cors")

    @property
    def load_profile(self):
        return self._get_load_profile_config()

    def get(self, setting, default=None):
        return self.settings.get(setting, default)

    def _get_load_profile_config(self):
        load_profile_config = self.get("load_profile")
        load_profile_config["interpolation_strategy"] = LoadProfileStrategy(
            load_profile_config.interpolation_strategy
        )
        load_profile_config["max_interval_length"] = int(
            load_profile_config.max_interval_length
        )
        load_profile_config["min_days"] = int(load_profile_config.min_days)
        return load_profile_config

    def _get_postgres_config(self):
        db_config = self.get("postgres")
        db_config["port"] = int(db_config.port)
        return db_config

    def _get_otp_config(self):
        otp_config = self.get("otp")
        otp_config["max_otp_verification_attempts"] = int(
            otp_config.max_otp_verification_attempts
        )
        otp_config["max_resend_otp_attempts"] = int(otp_config.max_resend_otp_attempts)
        otp_config["max_resend_otp_attempt_window_in_min"] = int(
            otp_config.max_resend_otp_attempt_window_in_min
        )
        otp_config["otp_validity_in_secs"] = int(otp_config.otp_validity_in_secs)
        otp_config["master_otp_admin"] = int(otp_config.master_otp_admin)
        otp_config["master_otp_user"] = int(otp_config.master_otp_user)
        return otp_config

    def _get_simulation_config(self):
        data = self.get("simulation")
        data["initial_battery_soc"] = float(data["initial_battery_soc"])
        data["solar_peak_percentage_for_charging"] = float(
            data["solar_peak_percentage_for_charging"]
        )
        data["load_peak_percentage_for_discharging"] = float(
            data["load_peak_percentage_for_discharging"]
        )
        data["charge_battery_efficiency"] = float(data["charge_battery_efficiency"])
        data["discharge_battery_efficiency"] = float(
            data["discharge_battery_efficiency"]
        )
        data["default_panel_capacity"] = float(data["default_panel_capacity"])
        data["default_battery_capacity_required"] = float(
            data["default_battery_capacity_required"]
        )
        data["battery_dynamic_allocation"] = float(
            data["battery_dynamic_percentage_allocation"]
        )
        data["battery_base_allocation"] = float(
            data["battery_base_percentage_allocation"]
        )
        return data
