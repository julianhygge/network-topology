"""Service for managing consumption patterns."""

from typing import Dict, List, Type

from app.api.v1.models.requests.load_profile.load_profile_create import (
    PersonProfileItem,
)
from app.domain.interfaces.enums.work_profile_type import WorkProfileType
from app.domain.interfaces.solar.i_consumption_patterns import (
    ConsumptionPatternStrategy,
)
from app.domain.services.solar.consumption_patterns.away_day_workers import (
    DayWorkerStrategy,
)
from app.domain.services.solar.consumption_patterns.away_night_workers import (
    NightWorkerStrategy,
)
from app.domain.services.solar.consumption_patterns.home_day_workers import (
    HomeWorkerStrategy,
)


class ConsumptionPatternService:
    """
    Service responsible for applying and normalizing consumption patterns
    based on household profiles and general adjustments.
    """

    def __init__(self):
        self._strategy_registry: Dict[
            WorkProfileType, Type[ConsumptionPatternStrategy]
        ] = {
            WorkProfileType.WORKS_AT_HOME: HomeWorkerStrategy,
            WorkProfileType.NIGHT_WORKER_OUTSIDE: NightWorkerStrategy,
            WorkProfileType.DAY_WORKER_OUTSIDE: DayWorkerStrategy,
        }

    @staticmethod
    def _apply_general_adjustments(
        consumption_pattern: List[float], interval_minutes: int
    ) -> None:
        """
        Applies general adjustments to the consumption pattern based on common
        household activities. Reduces consumption from 11 pm to 6 am,
        and increases consumption between 7 pm and 10 pm,
        as well as between 6 am and 8 am.
        """
        for i in range(len(consumption_pattern)):
            hour = (i * interval_minutes) // 60
            if 23 <= hour or hour < 6:  # From 11 pm to 6 am
                # Significantly reduce consumption
                consumption_pattern[i] *= 0.5
            elif 19 <= hour < 22:  # From 7 pm to 10 pm
                consumption_pattern[i] *= (
                    1.3  # Increase consumption to reflect peak activity
                )
            elif 6 <= hour < 8:  # From 6 am to 8 am
                consumption_pattern[i] *= (
                    1.2  # Increase consumption to reflect peak activity
                )

    @staticmethod
    def _normalize_adjusted_consumptions(
        adjusted_consumptions: List[float], original_total_consumption: float
    ) -> List[float]:
        """
        Normalizes the adjusted consumptions to ensure
        the total matches the original total consumption.
        """
        adjusted_total = sum(adjusted_consumptions)
        if adjusted_total == 0:
            return adjusted_consumptions

        normalization_factor = original_total_consumption / adjusted_total
        normalized_consumptions = [
            consumption * normalization_factor
            for consumption in adjusted_consumptions
        ]
        return normalized_consumptions

    @staticmethod
    def _divide_consumption_in_intervals(
        total_consumption: float, interval_minutes: int = 15
    ) -> float:
        """Divides total consumption into per-interval consumption."""
        intervals_per_day = 1440 // interval_minutes
        consumption_per_interval = total_consumption / intervals_per_day
        return consumption_per_interval

    @staticmethod
    def _initialize_consumption_pattern(interval_minutes: int) -> List[float]:
        """Initializes a base consumption pattern."""
        return [1.0] * (1440 // interval_minutes)

    def _get_strategy_instance(
        self, profile_type: WorkProfileType
    ) -> ConsumptionPatternStrategy:
        """Get an instance of a Strategy pattern for the given profile."""
        strategy_class = self._strategy_registry.get(
            profile_type, DayWorkerStrategy  # Default to DayWorkerStrategy
        )
        return strategy_class()

    def apply_profile_adjustments(
        self,
        profile_items: List[PersonProfileItem],
        consumption_pattern: List[float],
        interval_minutes: int,
    ) -> None:
        """
        Applies consumption adjustments based on each person's
        work profile within the household.
        The adjustments from multiple people are compounded.
        """
        self._apply_general_adjustments(consumption_pattern, interval_minutes)

        for person_profile in profile_items:
            for _ in range(person_profile.count):
                strategy_pattern = self._get_strategy_instance(
                    profile_type=person_profile.profile_type
                )
                strategy_pattern.apply_pattern(
                    consumption_pattern, interval_minutes
                )

    def generate_normalized_pattern(
        self,
        profile_items: List[PersonProfileItem],
        total_daily_kwh: float,
        interval_minutes: int = 15,
    ) -> List[float]:
        """
        Generates a normalized daily consumption pattern based on profile items
        and total daily kWh.
        """
        base_pattern = self._initialize_consumption_pattern(interval_minutes)
        self.apply_profile_adjustments(
            profile_items, base_pattern, interval_minutes
        )
        normalized_pattern = self._normalize_adjusted_consumptions(
            base_pattern, total_daily_kwh
        )
        return normalized_pattern
