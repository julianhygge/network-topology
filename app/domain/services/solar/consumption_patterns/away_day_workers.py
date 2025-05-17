from typing import List

from app.domain.interfaces.solar.i_consumption_patterns import (
    ConsumptionPatternStrategy,
)


class DayWorkerStrategy(ConsumptionPatternStrategy):
    def apply_pattern(
        self, consumption_pattern: List[float], interval_minutes: int
    ):
        """
        Apply adjustments for those working outside during the day.
        """
        for i in range(len(consumption_pattern)):
            hour = (i * interval_minutes) // 60
            if 9 <= hour < 17:  # Typical working hours (away)
                consumption_pattern[i] *= 0.6  # Lower consumption
