from abc import ABC, abstractmethod
from pandas import DataFrame, DatetimeIndex, Timedelta, Timestamp, date_range


class BaseLoadProfileFileCompleter(ABC):
    def create_interpolation_array(
        self, min_date: Timestamp, max_date: Timestamp
    ) -> DatetimeIndex:
        """Create the interpolation timestamp array based on the min and max date."""
        min_value = min_date.floor("15min")
        if max_date.minute == 0:
            max_date = max_date + Timedelta("1h")
        max_value = max_date.ceil("1h")
        return date_range(
            start=min_value, end=max_value, freq="15min", inclusive="left"
        )

    @abstractmethod
    def complete_data(self, profile_data: DataFrame) -> DataFrame:
        """
        Completes the data in the DataFrame based on the strategy.
        @param profile_data - must have columns "timestamp", "consumption_kwh", and "profile_id"
        @return returns an DataFrame with the only columns "timestamp", "consumption_kwh", and "profile_id".
        The "consumption_kwh" has been completed based on the "timestamp" and interpolation strategy implemented.
        """
