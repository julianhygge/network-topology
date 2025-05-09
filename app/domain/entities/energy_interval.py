"""Domain entity for EnergyInterval."""

from dataclasses import dataclass
from datetime import datetime
from decimal import Decimal


@dataclass
class EnergyInterval:
    """Energy interval item"""

    timestamp: datetime
    energy_kw: Decimal
