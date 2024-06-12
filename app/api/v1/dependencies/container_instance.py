from app.api.v1.dependencies.dependencies_container import Container
from app.domain.interfaces.iservice import IService
from app.domain.interfaces.net_topology.inet_topology_service import INetTopologyService

c = Container()


def get_configuration():
    return c.configuration()


def get_token_service():
    return c.token_service()


def get_sms_service():
    return c.sms_service()


def get_auth_service():
    return c.auth_service()


def get_user_service() -> IService:
    return c.user_service()


def get_net_topology_service() -> INetTopologyService:
    return c.net_topology_service()


def get_substation_service() -> IService:
    return c.substation_service()


def get_transformer_service() -> IService:
    return c.transformer_service()


def get_house_service() -> IService:
    return c.house_service()
