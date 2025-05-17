from typing import List

from app.domain.interfaces.solar.i_consumption_patterns import (
    ConsumptionPatternStrategy,
)


class NightWorkerStrategy(ConsumptionPatternStrategy):
    def apply_pattern(
        self, consumption_pattern: List[float], interval_minutes: int
    ):
        """
        For night workers, adjust for being away at night and active during the day.
        """
        # General adjustments still form a base for household activities
        for i in range(len(consumption_pattern)):
            hour = (i * interval_minutes) // 60
            if 22 <= hour or hour < 6:  # Typical night work hours (away)
                consumption_pattern[i] *= 0.3  # Significantly lower
            elif (
                8 <= hour < 12 or 14 <= hour < 18
            ):  # Active during the day at home
                consumption_pattern[i] *= 1.25
