from dependency_injector import containers, providers

from app.config.configuration import ApiConfiguration
from app.data.interfaces.irepository import IRepository
from app.data.repositories.authorization.auth_attempt_repository import AuthAttemptRepository
from app.data.repositories.authorization.group_repository import GroupRepository
from app.data.repositories.authorization.user_group_rel_repository import UserGroupRelRepository
from app.data.repositories.authorization.user_repository import UserRepository, AccountRepository
from app.data.repositories.load_profile.load_profile_repository import LoadProfilesRepository, \
    LoadProfileDetailsRepository, LoadProfileFilesRepository, LoadProfileBuilderItemsRepository, \
    LoadGenerationEngineRepository, PredefinedTemplatesRepository
from app.data.repositories.topology.topology_repository import SubstationRepository, TransformerRepository, \
    HouseRepository, NodeRepository
from app.data.repositories.topology.electrical_appliances_repository import ElectricalAppliancesRepository
from app.data.schemas.hygge_database import HyggeDatabase
from app.domain.services.auth_service import AuthService
from app.domain.services.load_profile_service import LoadProfileService
from app.domain.services.mqtt_service import MQTTService
from app.domain.services.sms_service import SmsService
from app.domain.services.token_service import TokenService
from app.domain.services.topology.house_service import HouseService
from app.domain.services.topology.node_service import NodeService
from app.domain.services.topology.net_topology_service import NetTopologyService
from app.domain.services.topology.substation_service import SubstationService
from app.domain.services.topology.topology_simulator import TopologySimulator
from app.domain.services.topology.transformer_service import TransformerService
from app.domain.services.topology.electrical_appliances_service import ElectricalAppliancesService
from app.domain.services.user_service import UserService
from app.domain.services.websocket_service import WebSocketConnectionManager


class Container(containers.DeclarativeContainer):
    configuration = providers.Singleton(ApiConfiguration)
    HyggeDatabase.set_config(configuration().db)
    _user_repository = providers.Singleton(UserRepository)
    _auth_attempt_repository = providers.Singleton(AuthAttemptRepository)
    _group_repository = providers.Singleton(GroupRepository)
    _user_group_rel_repository = providers.Singleton(UserGroupRelRepository)
    _account_repository = providers.Singleton(AccountRepository)
    _substation_repo: IRepository = providers.Singleton(SubstationRepository)
    _transformer_repo: IRepository = providers.Singleton(TransformerRepository)
    _house_repo: IRepository = providers.Singleton(HouseRepository)
    _node_repo: IRepository = providers.Singleton(NodeRepository)
    _electrical_appliances_repo = providers.Singleton(ElectricalAppliancesRepository)
    _load_profiles_repository = providers.Singleton(LoadProfilesRepository)
    _load_profile_details_repository = providers.Singleton(LoadProfileDetailsRepository)
    _load_profile_files_repository = providers.Singleton(LoadProfileFilesRepository)
    _load_profile_builder_repository = providers.Singleton(LoadProfileBuilderItemsRepository)
    _load_generation_engine_repository = providers.Singleton(LoadGenerationEngineRepository)
    _predefined_templates_repository = providers.Singleton(PredefinedTemplatesRepository)

    token_service = providers.Factory(
        TokenService,
        configuration,
        _account_repository,
        _group_repository
    )

    web_socket_service = providers.Singleton(
        WebSocketConnectionManager
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

    user_service = providers.Factory(
        UserService,
        token_service,
        user_repository=_user_repository,
        user_group_repository=_user_group_rel_repository,
        group_repository=_group_repository,
        account_repository=_account_repository
    )

    net_topology_service = providers.Factory(
        NetTopologyService,
        substation_repo=_substation_repo,
        transformer_repo=_transformer_repo,
        house_repo=_house_repo,
        node_repo=_node_repo
    )

    topology_simulator = providers.Factory(
        TopologySimulator,
        transformer_repo=_transformer_repo,
        house_repo=_house_repo
    )

    electrical_appliances_service = providers.Factory(
        ElectricalAppliancesService,
        repository=_electrical_appliances_repo
    )

    substation_service = providers.Factory(
        SubstationService,
        repository=_substation_repo
    )

    transformer_service = providers.Factory(
        TransformerService,
        repository=_transformer_repo
    )

    house_service = providers.Factory(
        HouseService,
        repository=_house_repo
    )

    node_service = providers.Factory(
        NodeService,
        node_repo=_node_repo
    )

    load_profile_service = providers.Factory(
        LoadProfileService,
        repository=_load_profiles_repository(),
        load_details_repository=_load_profile_details_repository,
        load_profile_files_repository=_load_profile_files_repository,
        user_repository=_user_repository,
        load_profile_builder_repository=_load_profile_builder_repository,
        load_generation_engine_repository=_load_generation_engine_repository,
        predefined_templates_repository=_predefined_templates_repository
    )
