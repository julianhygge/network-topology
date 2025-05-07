from decimal import Decimal
from typing import List
from uuid import UUID

from app.data.interfaces.dtos.topology_dtos import HouseDTO, TransformerDTO
from app.data.interfaces.topology.i_house_repository import IHouseRepository
from app.data.interfaces.topology.i_topology_simulator import ITopologySimulator
from app.data.interfaces.topology.i_transformer_repository import ITransformerRepository


class TopologySimulator(ITopologySimulator):

    def __init__(
        self,
        house_repo: IHouseRepository,
        transformer_repo: ITransformerRepository,
    ):
        self._house_repo = house_repo
        self._transformer_repo = transformer_repo

    def calculate_total_load(self, houses):
        return sum(house.connection_kw for house in houses if house.connection_kw)

    def calculate_total_solar(self, houses):
        return sum(
            house.solar_kw for house in houses if house.has_solar and house.solar_kw
        )

    def calculate_excess_solar(
        self, total_solar: Decimal, total_load: Decimal
    ) -> Decimal:
        return max(total_solar - total_load, Decimal(0))

    def calculate_battery_capacity(self, houses):
        return sum(
            house.battery_total_kwh
            for house in houses
            if house.has_battery and house.battery_total_kwh
        )

    def calculate_peak_capacity_rate(self, houses):
        return sum(
            house.battery_peak_charging_rate
            for house in houses
            if house.has_battery and house.battery_peak_charging_rate
        )

    def run(self, substation_id: UUID):
        """"""

    def allocation_algorithm(
        self,
        houses: List[HouseDTO],
        transformers: List[TransformerDTO],
        total_load: Decimal,
        total_solar: Decimal,
        excess_solar: Decimal,
        battery_capacity: Decimal,
        peak_capacity_rate: Decimal,
    ) -> None:
        for transformer in transformers:
            houses_under_transformer = [
                house for house in houses if house.transformer_id == transformer.id
            ]

            for house in houses_under_transformer:
                if house.has_solar:
                    house.load_profile = f"Allocated solar: {house.solar_kw} kW"

            for house in houses_under_transformer:
                if house.has_battery:
                    if excess_solar > 0:
                        house.load_profile += f", Charging battery at {house.battery_peak_charging_rate} kW"
                    else:
                        house.load_profile += f", Discharging battery at {house.battery_peak_discharging_rate} kW"

            for house in houses_under_transformer:
                if house.has_battery:
                    pass
