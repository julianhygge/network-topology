from app.api.v1.dependencies.dependencies_container import Container
from app.domain.interfaces.iservice import IService
from app.domain.services.user_service import UserService

c = Container()


def get_simulation_service():
    return c.simulation_service()


def get_configuration():
    return c.configuration()


def get_battery_service():
    return c.battery_service()


def get_token_service():
    return c.token_service()


def get_sms_service():
    return c.sms_service()


def get_auth_service():
    return c.auth_service()


def get_user_service() -> IService:
    return c.user_service()


def get_pricing_service():
    return c.pricing_service()


def get_load_profile_service():
    return c.load_profile_service()


def get_appliance_service():
    return c.appliance_service()


def get_solar_service():
    return c.solar_service()


def get_panels_service():
    return c.panels_service()


def get_utilities_service():
    return c.utilities_service()
