from abc import ABC, abstractmethod
from typing import List
from decimal import Decimal
from uuid import UUID

from app.data.interfaces.dtos.topology_dtos import HouseDTO, TransformerDTO


class ITopologySimulator(ABC):

    @abstractmethod
    def calculate_total_load(self, houses: List['HouseDTO']) -> Decimal:
        pass

    @abstractmethod
    def calculate_total_solar(self, houses: List['HouseDTO']) -> Decimal:
        pass

    @abstractmethod
    def calculate_excess_solar(self, total_solar: Decimal, total_load: Decimal) -> Decimal:
        pass

    @abstractmethod
    def calculate_battery_capacity(self, houses: List['HouseDTO']) -> Decimal:
        pass

    @abstractmethod
    def calculate_peak_capacity_rate(self, houses: List['HouseDTO']) -> Decimal:
        pass

    @abstractmethod
    def run(self, substation_id: UUID):
        pass

    @abstractmethod
    def allocation_algorithm(self, houses: List['HouseDTO'], transformers: List['TransformerDTO'], total_load: Decimal,
                             total_solar: Decimal, excess_solar: Decimal, battery_capacity: Decimal,
                             peak_capacity_rate: Decimal) -> None:
        pass
