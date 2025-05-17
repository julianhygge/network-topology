from typing import List

from app.domain.interfaces.solar.i_consumption_patterns import (
    ConsumptionPatternStrategy,
)


class UnspecifiedProfileStrategy(ConsumptionPatternStrategy):
    def apply_pattern(
        self, consumption_pattern: List[float], interval_minutes: int
    ):
        """
        Apply adjustments for individuals working from home during daytime.
        """
        for i in range(len(consumption_pattern)):
            consumption_pattern[i] *= 1.05
