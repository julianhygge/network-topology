from dataclasses import dataclass
from datetime import datetime
from typing import List
from uuid import UUID


@dataclass
class HouseProfile:
    """
    Represents the energy profile of a house over a year.

    Attributes:
        house_id (UUID): The unique identifier for the house.
        timestamps (List[datetime]): A list of datetime objects representing in
                                     15-minute intervals for the profiles.
        load_values (List[float]): Energy consumption values.
        solar_values (List[float]): Solar energy generation values (kWh).
        solar_offset_values (List[float]): Net energy (solar generation - load)
                                           corresponding to each timestamp.
    """

    house_id: UUID
    house_name: str
    timestamps: List[datetime]
    load_values: List[float]
    solar_values: List[float]
    solar_offset_values: List[float]
