from abc import ABC, abstractmethod
from pandas import DataFrame


class ILoadProfileFileCompleter(ABC):
    @abstractmethod
    def complete_data(self, profile_data: DataFrame) -> DataFrame:
        """
        Completes the data in the DataFrame based on the strategy.
        @param profile_data - must have columns "timestamp", "consumption_kwh", and "profile_id"
        @return returns an DataFrame with the only columns "timestamp", "consumption_kwh", and "profile_id".
        The "consumption_kwh" has been completed based on the "timestamp" and interpolation strategy implemented.
        """
