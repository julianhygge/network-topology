from typing import List

from app.domain.interfaces.solar.i_consumption_patterns import (
    ConsumptionPatternStrategy,
)


class HomeWorkerStrategy(ConsumptionPatternStrategy):
    def apply_pattern(
        self, consumption_pattern: List[float], interval_minutes: int
    ):
        """
        Apply adjustments for individuals working from home during daytime.
        """
        for i in range(len(consumption_pattern)):
            hour = (i * interval_minutes) // 60
            if 9 <= hour < 17:  # Typical working hours
                consumption_pattern[i] *= 1.15  # Increase due to home presence
