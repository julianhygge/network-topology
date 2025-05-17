from abc import abstractmethod
from typing import List


class ConsumptionPatternStrategy:
    """
    Abstract base class for the Solar Profile Service.
    Defines the interface for managing solar profiles.
    """

    @abstractmethod
    def apply_pattern(
        self,
        consumption_pattern: List[float],
        interval_minutes: int,
    ) -> List[float]:
        """
        Apply a consumption pattern to a daily load

        Args:
            consumption_pattern: List of the consumption during a day.
            interval_minutes: Interval for the consumption pattern.

        Returns:
            List of the consumption during a day after apply the pattern.
        """
