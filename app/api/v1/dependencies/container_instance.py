"""
Provides FastAPI dependency functions to get instances from the container.

This module initializes the dependency injection container and defines
functions that can be used with `fastapi Depends` to inject configured
service instances into route handlers.
"""

from app.api.v1.dependencies.dependencies_container import Container
from app.config.configuration import ApiConfiguration
from app.data.interfaces.topology.i_topology_simulator import (
    ITopologySimulator,
)
from app.data.schemas.transactional.topology_schema import HouseFlag
from app.domain.interfaces.auth.i_auth_service import IAuthService
from app.domain.interfaces.auth.i_token_service import ITokenService
from app.domain.interfaces.communication.i_mqtt_service import IMqttService
from app.domain.interfaces.communication.i_sms_service import ISmsService
from app.domain.interfaces.i_node_service import INodeService
from app.domain.interfaces.i_service import IService
from app.domain.interfaces.net_topology.i_net_topology_service import (
    INetTopologyService,
)
from app.domain.interfaces.simulator_engine.i_data_preparation_service import (
    IDataPreparationService,
)
from app.domain.interfaces.solar.i_load_profile_service import (
    ILoadProfileService,
)
from app.domain.services.base_service import BaseService
from app.domain.services.simulator_engine.bill_simulation_service import (
    BillSimulationService,
)
from app.domain.services.solar.load_profile_builder_service import (
    LoadProfileBuilderService,
)
from app.domain.services.solar.load_profile_engine_service import (
    LoadProfileEngineService,
)
from app.domain.services.solar.load_profile_file_service import (
    LoadProfileFileService,
)
from app.domain.services.solar.load_profile_template_service import (
    LoadProfileTemplateService,
)

c = Container()


def get_configuration() -> ApiConfiguration:
    """Get the application configuration instance."""
    return c.configuration()


def get_token_service() -> ITokenService:
    """Get the token service instance."""
    return c.token_service()


def get_sms_service() -> ISmsService:
    """Get the SMS service instance."""
    return c.sms_service()


def get_auth_service() -> IAuthService:
    """Get the authentication service instance."""
    return c.auth_service()


def get_user_service() -> IService:
    """Get the user service instance."""
    return c.user_service()


def get_net_topology_service() -> INetTopologyService:
    """Get the network topology service instance."""
    return c.net_topology_service()


def get_data_preparation_service() -> IDataPreparationService:
    """Get the data preparation service instance."""
    return c.data_preparations_service()


def get_topology_simulator() -> ITopologySimulator:
    """Get the topology simulator instance."""
    return c.topology_simulator()


def get_substation_service() -> IService:
    """Get the substation service instance."""
    return c.substation_service()


def get_transformer_service() -> IService:
    """Get the transformer service instance."""
    return c.transformer_service()


def get_house_service() -> IService:
    """Get the house service instance."""
    return c.house_service()


def get_node_service() -> INodeService:
    """Get the node service instance."""
    return c.node_service()


def get_electrical_appliances_service() -> IService:
    """Get the electrical appliances service instance."""
    return c.electrical_appliances_service()


def get_solar_profile_service() -> IService:
    """Get the solar profile service instance."""
    return c.solar_profile_service()


def get_solar_installation_service() -> IService:
    """Get the solar profile service instance."""
    return c.solar_installation_service()


def get_load_profile_service() -> ILoadProfileService:
    """Get the load profile service instance."""
    return c.load_profile_service()


def get_load_profile_file_service() -> LoadProfileFileService:
    """Get the load profile file service instance."""
    return c._load_profile_file_service()


def get_load_profile_builder_service() -> LoadProfileBuilderService:
    """Get the load profile builder service instance."""
    return c._load_profile_builder_service()


def get_load_profile_engine_service() -> LoadProfileEngineService:
    """Get the load profile engine service instance."""
    return c._load_profile_engine_service()


def get_load_profile_template_service() -> LoadProfileTemplateService:
    """Get the load profile template service instance."""
    return c._load_profile_template_service()


def get_predefined_template_service() -> IService:
    """Get the predefined template service instance."""
    return c.predefined_template_service()


def get_mqtt_service() -> IMqttService:
    """Get the MQTT service instance."""
    return c.mqtt_service()


def get_flag_service() -> BaseService[HouseFlag]:
    """Get the flag service instance."""
    return c.flag_service()


def get_simulation_algorithm_service() -> IService:
    """Get Simulation Algorithm instance"""
    return c.simulation_algorithm_service()


def get_net_metering_algorithm_service() -> IService:
    """Get Net Metering Algorithm instance"""
    return c.net_metering_algorithm_service()


def get_simulation_runs_service() -> IService:
    """Get Net Metering Algorithm instance"""
    return c.simulation_runs_service()


def get_net_metering_policy_service() -> IService:
    """Get Net Metering policy instance"""
    return c.net_metering_policy_service()


def get_gross_metering_policy_service() -> IService:
    """Get Net Metering policy instance"""
    return c.gross_metering_policy_service()


def get_tou_rate_policy_service() -> IService:
    """Get time of use rate policy instance"""
    return c.tou_rate_policy_service()


def get_simulation_selected_policy_service() -> IService:
    """Get time of use rate policy instance"""
    return c.simulation_selected_policy_service()


def get_house_bill_service() -> IService:
    """Get time of use rate policy instance"""
    return c.house_bill_service()


def get_bill_simulation_service() -> BillSimulationService:
    """Get Bill Simulation Service instance"""
    return c.bill_simulation_service()
