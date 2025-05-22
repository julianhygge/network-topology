from datetime import datetime
from typing import List, Tuple
from uuid import UUID

from app.data.interfaces.i_repository import IRepository
from app.data.interfaces.load.i_load_load_profile_repository import (
    ILoadProfileRepository,
)
from app.data.interfaces.load.i_predefined_templates_repository import (
    IPredefinedTemplatesRepository,
)
from app.data.interfaces.load.i_template_load_patterns_repository import (
    ITemplateConsumptionPatternsRepository,
)
from app.data.interfaces.solar.i_solar_repository import (
    ISolarProfileRepository,
)
from app.domain.entities.house_profile import HouseProfile
from app.domain.interfaces.net_topology.i_net_topology_service import (
    INetTopologyService,
)
from app.domain.interfaces.simulator_engine.i_data_preparation_service import (
    IDataPreparationService,
)
from app.exceptions.hygge_exceptions import NotFoundException


class DataPreparationService(IDataPreparationService):
    def __init__(
        self,
        topology_service: INetTopologyService,
        load_profile_repository: ILoadProfileRepository,
        template_patterns_repository: ITemplateConsumptionPatternsRepository,
        pre_templates_repository: IPredefinedTemplatesRepository,
        yearly_solar_reference_repo: IRepository,
        solar_profile_repository: ISolarProfileRepository,
    ):
        self._topology_service = topology_service
        self._load_profile_repo = load_profile_repository
        self._template_patterns_repo = template_patterns_repository
        self._pre_templates_repo = pre_templates_repository
        self._yearly_solar_reference_repo = yearly_solar_reference_repo
        self._solar_profile_repo = solar_profile_repository

    def get_house_profile(self, house_id: UUID) -> HouseProfile:
        """Get the load and solar profile of a house.
        Assumes load and solar data are sorted and correspond positionally
        for a full year at 15-minute intervals."""

        loads_data_tuples: List[Tuple[datetime, float]] = (
            self._get_loads_by_house_id(house_id)
        )
        solar_data_tuples: List[Tuple[datetime, float]] = (
            self._get_solar_by_house_id(house_id)
        )

        profile_timestamps: List[datetime] = []
        profile_load_values: List[float] = []
        profile_solar_values: List[float] = []
        profile_solar_offset_values: List[float] = []

        num_points = min(len(loads_data_tuples), len(solar_data_tuples))

        for i in range(num_points):
            timestamp = loads_data_tuples[i][0]
            load_value = loads_data_tuples[i][1]
            solar_value = solar_data_tuples[i][1]

            profile_timestamps.append(timestamp)
            profile_load_values.append(load_value)
            profile_solar_values.append(solar_value)
            profile_solar_offset_values.append(solar_value - load_value)

        return HouseProfile(
            house_id=house_id,
            timestamps=profile_timestamps,
            load_values=profile_load_values,
            solar_values=profile_solar_values,
            solar_offset_values=profile_solar_offset_values,
        )

    def get_houses_profile_by_substation_id(
        self, substation_id: UUID
    ) -> List[HouseProfile]:
        """Get the list of house profiles for the houses in a substation
        at 15-minute intervals for a full year."""

        houses = self._topology_service.get_houses_by_substation_id(
            substation_id
        )

        house_profiles = [self.get_house_profile(house.id) for house in houses]

        return house_profiles

    def _get_loads_by_house_id(
        self, house_id: UUID
    ) -> List[Tuple[datetime, float]]:
        """
        Get loads intervals (timestamp, value) for a given house ID.

        :param house_id: UUID of the house
        :return: List of tuples (timestamp, load_kwh)
        :raises NotFoundException: If the house is not found
        """

        load_profile = self._load_profile_repo.get_by_house_id(house_id)

        if not load_profile:
            raise NotFoundException(
                f"Load profile for house {house_id} not found"
            )

        pre_template = self._pre_templates_repo.filter(
            profile_id=load_profile.id
        )
        if not pre_template:
            raise NotFoundException(
                f"Predefined template for load profile {load_profile.id} "
                f"not found"
            )

        load_patterns = self._template_patterns_repo.filter(
            template_id=pre_template[0].template_id_id
        )

        if not load_patterns:
            return []

        load_patterns.sort(key=lambda x: x.timestamp)

        return [
            (item.timestamp, float(item.consumption_kwh))
            for item in load_patterns
        ]

    def _get_solar_by_house_id(
        self, house_id: UUID
    ) -> List[Tuple[datetime, float]]:
        """
        Get solar generation intervals (timestamp, value) for a given house ID.

        :param house_id: UUID of the house
        :return: List of tuples (timestamp, solar_generation_per_kw)
        :raises NotFoundException: If the house is not found
        """

        # TODO: here I need to select the solar profile any solar for now
        # Need to get the solar from the locations
        # This should be dynamic based on the house's location or
        # configuration.
        solar_references = self._yearly_solar_reference_repo.filter(
            site_id=2609522
        )
        if not solar_references:
            raise NotFoundException(
                f"Solar profile for house {house_id} not found "
                f"(using hardcoded site_id)"
            )
        solar_references.sort(key=lambda x: x.timestamp)

        solar_profiles = self._solar_profile_repo.filter(house_id=house_id)
        if not solar_profiles:
            raise NotFoundException(
                f"Solar profile for house {house_id} not found"
            )
        profile = solar_profiles[0]

        installed_capacity = profile.installed_capacity_kw

        return [
            (
                item.timestamp,
                item.per_kw_generation * installed_capacity,
            )
            for item in solar_references
        ]
