from abc import ABC, abstractmethod
from typing import Iterable
from pandas import DataFrame, DatetimeIndex


class ILoadProfileFileCompleter(ABC):

    @abstractmethod
    def complete_data(
        self,
        timestamps: DataFrame,
        consumption_kwh: DataFrame,
        interpolation_timestamps: DatetimeIndex,
    ) -> Iterable:
        """
        Completes the data in the DataFrame based on the strategy.
        @param profile_data - must have columns "timestamp", "consumption_kwh", and "profile_id"
        @return Array with interpolated values of length len(interpolation_timestamps) based on the timestamps and consumption_kwh
        """
