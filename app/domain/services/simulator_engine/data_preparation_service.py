import csv
import io
import os
import zipfile
from datetime import datetime
from typing import List, Tuple, cast
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
from app.domain.entities.node import Node
from app.domain.interfaces.net_topology.i_net_topology_service import (
    INetTopologyService,
)
from app.domain.interfaces.simulator_engine.i_data_preparation_service import (
    IDataPreparationService,
)
from app.exceptions.hygge_exceptions import HyggeException, NotFoundException


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

    def get_house_profile(self, house: Node) -> HouseProfile:
        """Get the load and solar profile of a house.
        Assumes load and solar data are sorted and correspond positionally
        for a full year at 15-minute intervals."""

        loads_data_tuples: List[Tuple[datetime, float]] = (
            self._get_loads_by_house_id(house.id)
        )
        solar_data_tuples: List[Tuple[datetime, float]] = (
            self._get_solar_by_house_id(house.id)
        )

        profile_timestamps: List[datetime] = []
        profile_load_values: List[float] = []
        profile_solar_values: List[float] = []
        profile_solar_offset_values: List[float] = []
        profile_imported_units: List[float] = []
        profile_exported_units: List[float] = []
        profile_net_usage: List[float] = []

        num_points = min(len(loads_data_tuples), len(solar_data_tuples))

        for i in range(num_points):
            timestamp = loads_data_tuples[i][0]
            load_value = loads_data_tuples[i][1]
            solar_value = solar_data_tuples[i][1]

            net_energy_at_point = solar_value - load_value
            imported_units_at_point = 0.0
            exported_units_at_point = 0.0
            net_usage_at_point = 0.0

            if net_energy_at_point < 0:
                imported_units_at_point = abs(net_energy_at_point)
            elif net_energy_at_point > 0:
                exported_units_at_point = net_energy_at_point

            net_usage_at_point = load_value - solar_value

            profile_timestamps.append(timestamp)
            profile_load_values.append(load_value)
            profile_solar_values.append(solar_value)
            profile_solar_offset_values.append(net_energy_at_point)
            profile_imported_units.append(imported_units_at_point)
            profile_exported_units.append(exported_units_at_point)
            profile_net_usage.append(net_usage_at_point)

        return HouseProfile(
            house_id=house.id,
            house_name=house.name,
            timestamps=profile_timestamps,
            load_values=profile_load_values,
            solar_values=profile_solar_values,
            solar_offset_values=profile_solar_offset_values,
            imported_units=profile_imported_units,
            exported_units=profile_exported_units,
            net_usage=profile_net_usage,
        )

    def _create_house_profile_csv_content(
        self, house_profile: HouseProfile
    ) -> str:
        """Creates CSV content for a given house profile."""
        output = io.StringIO()
        writer = csv.writer(output)
        writer.writerow(
            [
                "timestamp",
                "load",
                "solar",
                "solar_offset",
                "imported_units",
                "exported_units",
                "net_usage",
            ]
        )

        for i in range(len(house_profile.timestamps)):
            writer.writerow(
                [
                    house_profile.timestamps[i].isoformat(),
                    house_profile.load_values[i],
                    house_profile.solar_values[i],
                    house_profile.solar_offset_values[i],
                    house_profile.imported_units[i],
                    house_profile.exported_units[i],
                    house_profile.net_usage[i],
                ]
            )
        return output.getvalue()

    def create_house_profile_csvs_by_substation_id(
        self, substation_id: UUID, output_directory: str = "house_profiles_csv"
    ) -> List[str]:
        """
        Generates CSV files for each house profile under a substation
        and saves them to a specified directory.
        Returns a list of file paths.
        """
        house_profiles = self.get_houses_profile_by_substation_id(
            substation_id
        )
        if not house_profiles:
            raise NotFoundException(
                f"No houses found for substation {substation_id}"
            )

        if not os.path.exists(output_directory):
            os.makedirs(output_directory)

        file_paths: List[str] = []
        for profile in house_profiles:
            csv_content = self._create_house_profile_csv_content(profile)
            file_name = f"house_{profile.house_name}.csv"
            file_path = os.path.join(output_directory, file_name)
            try:
                with open(file_path, "w", newline="") as f:
                    f.write(csv_content)
                file_paths.append(file_path)
            except IOError as e:
                raise HyggeException(
                    f"Failed to write CSV for house {profile.house_id}: {e}"
                ) from e
        return file_paths

    def get_house_profile_csvs_zip_by_substation_id(
        self, substation_id: UUID, output_directory: str = "house_profiles_csv"
    ) -> bytes:
        """
        Generates CSV files for house profiles and returns them as a
        ZIP file in memory.
        """
        csv_file_paths = self.create_house_profile_csvs_by_substation_id(
            substation_id, output_directory
        )

        if not csv_file_paths:
            raise NotFoundException(
                f"No CSV files generated for substation {substation_id}"
            )

        zip_buffer = io.BytesIO()
        with zipfile.ZipFile(zip_buffer, "w", zipfile.ZIP_DEFLATED) as zipf:
            for file_path in csv_file_paths:
                zipf.write(file_path, os.path.basename(file_path))
        zip_buffer.seek(0)
        return zip_buffer.getvalue()

    def get_houses_profile_by_substation_id(
        self, substation_id: UUID
    ) -> List[HouseProfile]:
        """Get the list of house profiles for the houses in a substation
        at 15-minute intervals for a full year."""

        houses = self._topology_service.get_houses_by_substation_id(
            substation_id
        )

        house_profiles = [self.get_house_profile(house) for house in houses]

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

        # Calculate efficiency adjustments
        efficiency_factor = self._calculate_efficiency_factor(
            tilt_type=str(profile.tilt_type),
            years_since_installation=cast(
                float, profile.years_since_installation
            ),
        )

        return [
            (
                item.timestamp,
                item.per_kw_generation
                * installed_capacity
                * efficiency_factor,
            )
            for item in solar_references
        ]

    def _calculate_efficiency_factor(
        self, tilt_type: str, years_since_installation: float
    ) -> float:
        """
        Calculate efficiency factor based on tilt type and system age.

        :param tilt_type: Type of solar panel mounting ('fixed' or 'tracking')
        :param years_since_installation: Years since the system was installed
        :return: Efficiency factor (multiplier between 0 and 1+)
        """
        # Base efficiency factor
        base_efficiency = 1.0

        # Tilt type adjustment
        if tilt_type == "tracking":
            # Sun tracking systems are typically 15-25% more efficient
            tilt_efficiency = 1.20  # 20% improvement
        elif tilt_type == "fixed":
            tilt_efficiency = 1.0  # No adjustment for fixed systems
        else:
            # Default to fixed if unknown tilt type
            tilt_efficiency = 1.0

        # Age degradation adjustment
        # Solar panels typically degrade 0.5-0.8% per year
        # Using 0.6% per year degradation rate
        annual_degradation_rate = 0.006
        age_efficiency = max(
            0.5, 1.0 - (years_since_installation * annual_degradation_rate)
        )

        # Combined efficiency factor
        total_efficiency = base_efficiency * tilt_efficiency * age_efficiency

        return total_efficiency
