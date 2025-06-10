"""Dependency injection container setup using dependency-injector."""

from dependency_injector import containers, providers

from app.config.configuration import ApiConfiguration
from app.config.i_configuration import LoadProfileStrategy
from app.data.repositories.authorization.auth_attempt_repository import (
    AuthAttemptRepository,
)
from app.data.repositories.authorization.group_repository import (
    GroupRepository,
)
from app.data.repositories.authorization.user_group_rel_repository import (
    UserGroupRelRepository,
)
from app.data.repositories.authorization.user_repository import (
    AccountRepository,
    UserRepository,
)
from app.data.repositories.base_repository import BaseRepository
from app.data.repositories.load_profile.load_profile_repository import (
    LoadGenerationEngineRepository,
    LoadProfileBuilderItemsRepository,
    LoadProfileDetailsRepository,
    LoadProfileFilesRepository,
    LoadProfilesRepository,
    PredefinedTemplatesRepository,
)
from app.data.repositories.load_profile.template_patterns_repository import (
    TemplateConsumptionPatternsRepository,
)
from app.data.repositories.simulation_run_repository import SimulationRunRepository
from app.data.repositories.solar.solar_repository import (
    SolarInstallationRepository,
    SolarProfileRepository,
)
from app.data.repositories.topology.topology_repository import (
    NodeRepository,
    SubstationRepository,
)
from app.data.schemas.hygge_database import HyggeDatabase
from app.data.schemas.master.master_schema import (
    ElectricalAppliances,
    NetMeteringPolicyTypes,
    PredefinedTemplates,
    SimulationAlgorithm,
)
from app.data.schemas.simulation.house_bill_schema import HouseBill
from app.data.schemas.simulation.metering_policy_schema import (
    GrossMeteringPolicy,
    NetMeteringPolicy,
    TimeOfUseRatePolicy,
)
from app.data.schemas.simulation.simulation_container import SimulationContainer
from app.data.schemas.simulation.simulation_runs_schema import (
    SimulationRuns,
    SimulationSelectedPolicy,
)
from app.data.schemas.solar.solar_schema import SiteRefYearProduction
from app.data.schemas.transactional.topology_schema import (
    House,
    HouseFlag,
    Transformer,
)
from app.domain.interfaces.net_topology.i_load_profile_file_completer import (
    ILoadProfileFileCompleter,
)
from app.domain.services.auth.auth_service import AuthService
from app.domain.services.auth.token_service import TokenService
from app.domain.services.auth.user_service import UserService
from app.domain.services.base_service import BaseService
from app.domain.services.communication.mqtt_service import MQTTService
from app.domain.services.communication.sms_service import SmsService
from app.domain.services.load.load_profile_file_completer import (
    LoadProfileFileCompleterAkima1D,
    LoadProfileFileCompleterLinear,
    LoadProfileFileCompleterPChip,
    LoadProfileFileCompleterSpline,
)
from app.domain.services.simulator_engine.bill_simulation_service import (
    BillSimulationService,
)
from app.domain.services.simulator_engine.data_preparation_service import (
    DataPreparationService,
)
from app.domain.services.simulator_engine.energy_summary_service import (
    EnergySummaryService,
)
from app.domain.services.simulator_engine.net_topology_export_import_service import NetTopologyExportImportService
from app.domain.services.simulator_engine.simulation_container_service import SimulationContainerService
from app.domain.services.solar.consumption_pattern_service import (
    ConsumptionPatternService,
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
from app.domain.services.solar.load_profile_service import LoadProfileService
from app.domain.services.solar.load_profile_template_service import (
    LoadProfileTemplateService,
)
from app.domain.services.solar.solar_installtion_service import (
    SolarInstallationService,
)
from app.domain.services.solar.solar_profile_service import SolarProfileService
from app.domain.services.topology.house_service import HouseService
from app.domain.services.topology.net_topology_service import (
    NetTopologyService,
)
from app.domain.services.topology.node_service import NodeService
from app.domain.services.topology.substation_service import SubstationService
from app.domain.services.topology.topology_simulator import TopologySimulator
from app.domain.services.topology.transformer_service import TransformerService


def _load_profile_completer_factory(
    configuration: ApiConfiguration,
) -> type[ILoadProfileFileCompleter]:
    """
    Factory function to select the load profile completer based on config.

    Args:
        configuration: The application configuration.

    Returns:
        The class type of the selected load profile completer.
    """
    strategy = configuration.load_profile.interpolation_strategy
    if strategy == LoadProfileStrategy.Spline:
        return LoadProfileFileCompleterSpline
    if strategy == LoadProfileStrategy.PChip:
        return LoadProfileFileCompleterPChip
    if strategy == LoadProfileStrategy.Akima1D:
        return LoadProfileFileCompleterAkima1D
    # Default to Linear if no match or invalid strategy
    return LoadProfileFileCompleterLinear


class Container(containers.DeclarativeContainer):
    """
    Main dependency injection container for the application.

    Configures and provides instances of repositories, services, and other
    components needed throughout the application.
    """

    configuration = providers.Singleton(ApiConfiguration)
    HyggeDatabase.set_config(configuration().db)
    _user_repository = providers.Singleton(UserRepository)
    _auth_attempt_repository = providers.Singleton(AuthAttemptRepository)
    _group_repository = providers.Singleton(GroupRepository)
    _user_group_rel_repository = providers.Singleton(UserGroupRelRepository)
    _account_repository = providers.Singleton(AccountRepository)
    _substation_repo = providers.Singleton(SubstationRepository)
    _transformer_repo = providers.Singleton(
        BaseRepository[Transformer], Transformer
    )
    _flag_repo = providers.Singleton(BaseRepository[HouseFlag], HouseFlag)
    _house_repo = providers.Singleton(BaseRepository[House], House)
    _node_repo = providers.Singleton(NodeRepository)
    _electrical_appliances_repo = providers.Singleton(
        BaseRepository[ElectricalAppliances], ElectricalAppliances
    )
    _solar_profile_repo = providers.Singleton(SolarProfileRepository)
    _solar_installation_repo = providers.Singleton(SolarInstallationRepository)
    _load_profiles_repository = providers.Singleton(LoadProfilesRepository)
    _yearly_solar_reference_repo = providers.Singleton(
        BaseRepository[SiteRefYearProduction],
        SiteRefYearProduction,
    )
    _load_profile_details_repository = providers.Singleton(
        LoadProfileDetailsRepository
    )
    _load_profile_files_repository = providers.Singleton(
        LoadProfileFilesRepository
    )
    _load_profile_builder_repository = providers.Singleton(
        LoadProfileBuilderItemsRepository
    )
    _load_generation_engine_repository = providers.Singleton(
        LoadGenerationEngineRepository
    )
    _predefined_templates_repository = providers.Singleton(
        PredefinedTemplatesRepository
    )

    _simulation_algorithm_repository = providers.Singleton(
        BaseRepository[SimulationAlgorithm], SimulationAlgorithm
    )

    _policy_types_repository = providers.Singleton(
        BaseRepository[NetMeteringPolicyTypes], NetMeteringPolicyTypes
    )

    _simulation_runs_repository = providers.Singleton(SimulationRunRepository)

    _simulation_container_repository = providers.Singleton(
        BaseRepository[SimulationContainer], SimulationContainer
    )

    _net_metering_policy_repository = providers.Singleton(
        BaseRepository[NetMeteringPolicy], NetMeteringPolicy
    )
    _gross_metering_policy_repository = providers.Singleton(
        BaseRepository[GrossMeteringPolicy], GrossMeteringPolicy
    )

    _tou_rate_policy_repository = providers.Singleton(
        BaseRepository[TimeOfUseRatePolicy], TimeOfUseRatePolicy
    )

    _selected_policy_repository = providers.Singleton(
        BaseRepository[SimulationSelectedPolicy], SimulationSelectedPolicy
    )

    _house_bill_repository = providers.Singleton(
        BaseRepository[HouseBill], HouseBill
    )

    _template_patterns_repository = providers.Singleton(
        TemplateConsumptionPatternsRepository
    )
    _predefined_master_templates_repo = providers.Singleton(
        BaseRepository[PredefinedTemplates], PredefinedTemplates
    )

    _load_profile_completer = providers.Singleton(
        _load_profile_completer_factory(configuration())
    )

    _consumption_pattern_service = providers.Singleton(
        ConsumptionPatternService
    )

    _load_profile_file_service = providers.Singleton(
        LoadProfileFileService,
        load_profile_repo=_load_profiles_repository,
        load_profile_files_repo=_load_profile_files_repository,
        load_details_repo=_load_profile_details_repository,
        load_profile_completer=_load_profile_completer,
        conf=configuration,  # Pass the main configuration
    )

    # Provider for LoadProfileBuilderService
    _load_profile_builder_service = providers.Singleton(
        LoadProfileBuilderService,
        load_profile_repo=_load_profiles_repository,
        load_profile_builder_repo=_load_profile_builder_repository,
    )

    # Provider for LoadProfileEngineService
    _load_profile_engine_service = providers.Singleton(
        LoadProfileEngineService,
        load_profile_repo=_load_profiles_repository,
        load_gen_engine_repo=_load_generation_engine_repository,
    )

    # Provider for LoadProfileTemplateService
    _load_profile_template_service = providers.Singleton(
        LoadProfileTemplateService,
        load_profile_repo=_load_profiles_repository,
        pre_templates_repo=_predefined_templates_repository,
        template_patterns_repo=_template_patterns_repository,
        pre_master_templates_repo=_predefined_master_templates_repo,
        consumption_pattern_service=_consumption_pattern_service,
    )

    token_service = providers.Singleton(
        TokenService, configuration, _account_repository, _group_repository
    )

    mqtt_service = providers.Singleton(MQTTService, configuration)

    sms_service = providers.Singleton(SmsService, configuration, mqtt_service)

    auth_service = providers.Singleton(
        AuthService,
        user_repository=_user_repository,
        user_group_rel_repository=_user_group_rel_repository,
        auth_attempt_repository=_auth_attempt_repository,
        token_service=token_service,
        sms_service=sms_service,
        configuration=configuration,
    )

    user_service = providers.Singleton(
        UserService,
        token_service,
        user_repository=_user_repository,
        user_group_repository=_user_group_rel_repository,
        group_repository=_group_repository,
        account_repository=_account_repository,
    )

    net_topology_service = providers.Singleton(
        NetTopologyService,
        pre_master_template_repo=_predefined_master_templates_repo,
        load_profile_repository=_load_profiles_repository,
        substation_repo=_substation_repo,
        transformer_repo=_transformer_repo,
        house_repo=_house_repo,
        node_repo=_node_repo,
        template_patterns_repository=_template_patterns_repository,
        pre_templates_repository=_predefined_templates_repository,
        yearly_solar_reference_repo=_yearly_solar_reference_repo,
    )

    topology_simulator = providers.Singleton(
        TopologySimulator,
        transformer_repo=_transformer_repo,
        house_repo=_house_repo,
    )

    electrical_appliances_service = providers.Singleton(
        BaseService, repository=_electrical_appliances_repo
    )

    simulation_algorithm_service = providers.Singleton(
        BaseService, repository=_simulation_algorithm_repository
    )

    policy_type_service = providers.Singleton(
        BaseService, repository=_policy_types_repository
    )

    simulation_runs_service = providers.Singleton(
        BaseService, repository=_simulation_runs_repository
    )


    net_metering_policy_service = providers.Singleton(
        BaseService, repository=_net_metering_policy_repository
    )

    gross_metering_policy_service = providers.Singleton(
        BaseService, repository=_gross_metering_policy_repository
    )

    tou_rate_policy_service = providers.Singleton(
        BaseService, repository=_tou_rate_policy_repository
    )

    simulation_selected_policy_service = providers.Singleton(
        BaseService, repository=_selected_policy_repository
    )

    house_bill_service = providers.Singleton(
        BaseService, repository=_house_bill_repository
    )

    solar_profile_service = providers.Singleton(
        SolarProfileService, repository=_solar_profile_repo
    )

    solar_installation_service = providers.Singleton(
        SolarInstallationService, repository=_solar_installation_repo
    )

    substation_service = providers.Singleton(
        SubstationService, repository=_substation_repo
    )

    transformer_service = providers.Singleton(
        TransformerService, repository=_transformer_repo
    )

    house_service = providers.Singleton(HouseService, repository=_house_repo)

    node_service = providers.Singleton(NodeService, node_repo=_node_repo)

    load_profile_service = providers.Singleton(
        LoadProfileService,
        repository=_load_profiles_repository,
        load_details_repository=_load_profile_details_repository,
        load_profile_files_repository=_load_profile_files_repository,
    )

    predefined_template_service = providers.Factory(
        BaseService, repository=_predefined_master_templates_repo
    )

    data_preparations_service = providers.Singleton(
        DataPreparationService,
        topology_service=net_topology_service,
        load_profile_repository=_load_profiles_repository,
        template_patterns_repository=_template_patterns_repository,
        pre_templates_repository=_predefined_templates_repository,
        yearly_solar_reference_repo=_yearly_solar_reference_repo,
        solar_profile_repository=_solar_profile_repo,
    )

    energy_summary_service = providers.Singleton(
        EnergySummaryService,
        net_topology_service=net_topology_service,
        data_preparation_service=data_preparations_service,
    )

    bill_simulation_service = providers.Singleton(
        BillSimulationService,
        simulation_runs_repository=_simulation_runs_repository,
        selected_policy_repository=_selected_policy_repository,
        net_metering_policy_repo=_net_metering_policy_repository,
        gross_metering_policy_repo=_gross_metering_policy_repository,
        tou_rate_policy_params_repository=_tou_rate_policy_repository,
        house_bill_service=house_bill_service,
        net_topology_service=net_topology_service,
        data_preparation_service=data_preparations_service,
        energy_summary_service=energy_summary_service,
    )

    flag_service = providers.Singleton(BaseService, _flag_repo)

    network_topology_export_import_service = providers.Singleton(
        NetTopologyExportImportService,
        node_repository=_node_repo,
        substation_repository=_substation_repo,
        transformer_repository=_transformer_repo,
        house_repository=_house_repo,
        solar_profile_repository=_solar_profile_repo,
        predefined_templates_repository=_predefined_templates_repository,
        load_profiles_repository=_load_profiles_repository,

    )

    simulation_container_service = providers.Singleton(
        SimulationContainerService,
        simulation_container_repository=_simulation_container_repository,
        simulation_run_repository=_simulation_runs_repository
    )
