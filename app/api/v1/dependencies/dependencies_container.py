from app.config.configuration import ApiConfiguration
from dependency_injector import containers, providers

from app.data.interfaces.ipricing_repository import IPanelPriceRepository, IBatteryPriceRepository
from app.data.repositories.auth_attempt_repository import AuthAttemptRepository
from app.data.repositories.battery_repository import BatterySpecificationsRepository, BatteryTypeRepository
from app.data.repositories.group_repository import GroupRepository
from app.data.repositories.load_profile_repository import LoadProfileDetailsRepository, LoadProfilesRepository, \
    LoadProfileAppliancesRepository
from app.data.repositories.pricing_repository import PanelPriceRepository, BatteryPriceRepository
from app.data.repositories.solar_profile_repository import SolarPanelRepository, LocationRepository, \
    SolarProductionRepository
from app.data.repositories.user_group_rel_repository import UserGroupRelRepository
from app.data.repositories.user_repository import UserRepository
from app.data.repositories.utility_repository import UtilityRepository, RateStructureTypeRepository, \
    RateTiersRepository, RateIntervalsRepository, RateFlatRepository
from app.data.schemas.hygge_database import HyggeDatabase
from app.domain.services.auth_service import AuthService
from app.domain.services.base_service import BaseService
from app.domain.services.battery_service import BatteryService
from app.domain.services.load_profile_service import LoadProfileService
from app.domain.services.mqtt_service import MQTTService
from app.domain.services.pricing_service import PricingService
from app.domain.services.simulation.simulation_service import SimulatorService
from app.domain.services.sms_service import SmsService
from app.domain.services.solar_service import SolarService
from app.domain.services.token_service import TokenService
from app.domain.services.user_service import UserService
from app.domain.services.utility_service import UtilityService


class Container(containers.DeclarativeContainer):
    configuration = providers.Singleton(ApiConfiguration)
    HyggeDatabase.set_config(configuration().db)
    _utility_repository = providers.Singleton(UtilityRepository)
    _solar_panel_repository = providers.Singleton(SolarPanelRepository)
    _user_repository = providers.Singleton(UserRepository)
    _rate_structure_type_repository = providers.Singleton(RateStructureTypeRepository)
    _rate_tiers_repository = providers.Singleton(RateTiersRepository)
    _rate_intervals_repository = providers.Singleton(RateIntervalsRepository)
    _rate_flat_repository = providers.Singleton(RateFlatRepository)
    _load_profile_details_repository = providers.Singleton(LoadProfileDetailsRepository)
    _battery_specifications_repository = providers.Singleton(BatterySpecificationsRepository)
    _panel_price_repository: IPanelPriceRepository = providers.Singleton(PanelPriceRepository)
    _battery_price_repository: IBatteryPriceRepository = providers.Singleton(BatteryPriceRepository)
    _auth_attempt_repository = providers.Singleton(AuthAttemptRepository)
    _group_repository = providers.Singleton(GroupRepository)
    _battery_type_repository = providers.Singleton(BatteryTypeRepository)
    _load_profiles_repository = providers.Singleton(LoadProfilesRepository)
    _appliance_repository = providers.Singleton(LoadProfileAppliancesRepository)
    _solar_production_repository = providers.Singleton(SolarProductionRepository)
    _location_repository = providers.Singleton(LocationRepository, _solar_panel_repository)
    _user_group_rel_repository = providers.Singleton(UserGroupRelRepository)

    token_service = providers.Factory(
        TokenService,
        configuration,
        _user_repository,
        _group_repository
    )

    mqtt_service = providers.Factory(
        MQTTService,
        configuration
    )

    sms_service = providers.Factory(
        SmsService,
        configuration,
        mqtt_service
    )

    auth_service = providers.Factory(
        AuthService,
        user_repository=_user_repository,
        user_group_rel_repository=_user_group_rel_repository,
        auth_attempt_repository=_auth_attempt_repository,
        token_service=token_service,
        sms_service=sms_service,
        configuration=configuration
    )

    pricing_service = providers.Factory(
        PricingService,
        panel_price_repository=_panel_price_repository,
        battery_price_repository=_battery_price_repository,
        configuration=configuration
    )

    simulation_service = providers.Factory(
        SimulatorService,
        pricing_service=pricing_service,
        location_repository=_location_repository,
        load_details_repository=_load_profile_details_repository,
        battery_repository=_battery_specifications_repository,
        configuration=configuration

    )

    battery_service = providers.Factory(
        BatteryService,
        battery_type_repository=_battery_type_repository,
        battery_specifications_repository=_battery_specifications_repository
    )

    load_profile_service = providers.Factory(
        LoadProfileService,
        repository=_load_profiles_repository(),
        appliance_repository=_appliance_repository,
        load_details_repository=_load_profile_details_repository
    )

    appliance_service = providers.Factory(
        BaseService,
        _appliance_repository
    )

    solar_service = providers.Factory(
        SolarService,
        _location_repository,
        _solar_production_repository,
        _solar_panel_repository,
        configuration
    )

    panels_service = providers.Factory(
        BaseService,
        _solar_panel_repository
    )

    utilities_service = providers.Factory(
        UtilityService,
        utility_repository=_utility_repository,
        rate_structure_type_repository=_rate_structure_type_repository,
        rate_tiers_repository=_rate_tiers_repository,
        rate_intervals_repository=_rate_intervals_repository,
        rate_flat_repository=_rate_flat_repository
    )

    user_service = providers.Factory(
        UserService,
        user_repository=_user_repository,
        user_group_repository=_user_group_rel_repository,
        group_repository=_group_repository
    )
