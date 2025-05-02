from dependency_injector import containers, providers
from app.config.configuration import ApiConfiguration
from app.config.i_configuration import LoadProfileStrategy
from app.data.interfaces.irepository import IRepository
from app.data.repositories.authorization.auth_attempt_repository import (
    AuthAttemptRepository,
)
from app.data.repositories.authorization.group_repository import GroupRepository
from app.data.repositories.authorization.user_group_rel_repository import (
    UserGroupRelRepository,
)
from app.data.repositories.authorization.user_repository import (
    UserRepository,
    AccountRepository,
)
from app.data.repositories.load_profile.load_profile_repository import (
    LoadProfilesRepository,
    LoadProfileDetailsRepository,
    LoadProfileFilesRepository,
    LoadProfileBuilderItemsRepository,
    LoadGenerationEngineRepository,
    PredefinedTemplatesRepository,
)
from app.data.repositories.master.predefined_template_repository import (
    PredefinedMasterTemplatesRepository,
)
from app.data.repositories.solar.solar_profile_repository import SolarProfileRepository
from app.data.repositories.topology.topology_repository import (
    SubstationRepository,
    TransformerRepository,
    HouseRepository,
    NodeRepository,
)
from app.data.repositories.master.electrical_appliances_repository import (
    ElectricalAppliancesRepository,
)
from app.data.schemas.hygge_database import HyggeDatabase
from app.domain.interfaces.net_topology.i_load_profile_file_completer import (
    ILoadProfileFileCompleter,
)
from app.domain.services.auth_service import AuthService
from app.domain.services.base_service import BaseService
from app.domain.services.load_profile_service import LoadProfileService
from app.domain.services.mqtt_service import MQTTService
from app.domain.services.sms_service import SmsService
from app.domain.services.token_service import TokenService
from app.domain.services.topology.house_service import HouseService
from app.domain.services.topology.load_profile_file_completer import (
    LoadProfileFileCompleterAkima1D,
    LoadProfileFileCompleterLinear,
    LoadProfileFileCompleterPChip,
    LoadProfileFileCompleterSpline,
)
from app.domain.services.topology.node_service import NodeService
from app.domain.services.topology.net_topology_service import NetTopologyService
from app.domain.services.topology.solar_profile_service import SolarProfileService
from app.domain.services.topology.substation_service import SubstationService
from app.domain.services.topology.topology_simulator import TopologySimulator
from app.domain.services.topology.transformer_service import TransformerService
from app.domain.services.user_service import UserService


def _load_profile_completer_factory(
    configuration: ApiConfiguration,
) -> type[ILoadProfileFileCompleter]:
    strategy = configuration.load_profile.interpolation_strategy
    if strategy == LoadProfileStrategy.Spline:
        return LoadProfileFileCompleterSpline
    elif strategy == LoadProfileStrategy.PChip:
        return LoadProfileFileCompleterPChip
    elif strategy == LoadProfileStrategy.Akima1D:
        return LoadProfileFileCompleterAkima1D
    return LoadProfileFileCompleterLinear


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
    _solar_profile_repo = providers.Singleton(SolarProfileRepository)
    _load_profiles_repository = providers.Singleton(LoadProfilesRepository)
    _load_profile_details_repository = providers.Singleton(LoadProfileDetailsRepository)
    _load_profile_files_repository = providers.Singleton(LoadProfileFilesRepository)
    _load_profile_builder_repository = providers.Singleton(
        LoadProfileBuilderItemsRepository
    )
    _load_generation_engine_repository = providers.Singleton(
        LoadGenerationEngineRepository
    )
    _predefined_templates_repository = providers.Singleton(
        PredefinedTemplatesRepository
    )
    _predefined_master_templates_repository = providers.Singleton(
        PredefinedMasterTemplatesRepository
    )
    _load_profile_completer = providers.Singleton(
        _load_profile_completer_factory(configuration())
    )

    token_service = providers.Factory(
        TokenService, configuration, _account_repository, _group_repository
    )

    mqtt_service = providers.Factory(MQTTService, configuration)

    sms_service = providers.Factory(SmsService, configuration, mqtt_service)

    auth_service = providers.Factory(
        AuthService,
        user_repository=_user_repository,
        user_group_rel_repository=_user_group_rel_repository,
        auth_attempt_repository=_auth_attempt_repository,
        token_service=token_service,
        sms_service=sms_service,
        configuration=configuration,
    )

    user_service = providers.Factory(
        UserService,
        token_service,
        user_repository=_user_repository,
        user_group_repository=_user_group_rel_repository,
        group_repository=_group_repository,
        account_repository=_account_repository,
    )

    net_topology_service = providers.Factory(
        NetTopologyService,
        substation_repo=_substation_repo,
        transformer_repo=_transformer_repo,
        house_repo=_house_repo,
        node_repo=_node_repo,
    )

    topology_simulator = providers.Factory(
        TopologySimulator, transformer_repo=_transformer_repo, house_repo=_house_repo
    )

    electrical_appliances_service = providers.Factory(
        BaseService, repository=_electrical_appliances_repo
    )

    solar_profile_service = providers.Factory(
        SolarProfileService, repository=_solar_profile_repo
    )

    substation_service = providers.Factory(
        SubstationService, repository=_substation_repo
    )

    transformer_service = providers.Factory(
        TransformerService, repository=_transformer_repo
    )

    house_service = providers.Factory(HouseService, repository=_house_repo)

    node_service = providers.Factory(NodeService, node_repo=_node_repo)

    load_profile_service = providers.Factory(
        LoadProfileService,
        repository=_load_profiles_repository,
        load_details_repository=_load_profile_details_repository,
        load_profile_files_repository=_load_profile_files_repository,
        user_repository=_user_repository,
        load_profile_builder_repository=_load_profile_builder_repository,
        load_generation_engine_repository=_load_generation_engine_repository,
        predefined_templates_repository=_predefined_templates_repository,
        load_profile_completer=_load_profile_completer,
        configuration=configuration().load_profile,
    )

    predefined_template_service = providers.Factory(
        BaseService, repository=_predefined_master_templates_repository
    )
