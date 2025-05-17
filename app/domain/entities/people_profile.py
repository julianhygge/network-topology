"""Domain entity for EnergyInterval."""

from dataclasses import dataclass

from app.domain.interfaces.enums.work_profile_type import WorkProfileType


@dataclass
class PersonProfileItem:
    """Defines a type of work profile and the count of people with it."""

    profile_type: WorkProfileType
    count: int
