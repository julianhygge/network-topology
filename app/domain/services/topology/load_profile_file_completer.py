from pandas import DataFrame, DatetimeIndex, Timestamp, date_range, Timedelta
from numpy import interp
from app.domain.interfaces.net_topology.iload_profile_file_completer import (
    ILoadProfileFileCompleter,
)
from app.utils.logger import logger


class LoadProfileFileCompleterBase(ILoadProfileFileCompleter):
    def create_interpolation_array(
        self, min_date: Timestamp, max_date: Timestamp
    ) -> DatetimeIndex:
        min_value = min_date.floor("15min")
        if max_date.minute == 0:
            max_date = max_date + Timedelta("1h")
        max_value = max_date.ceil("1h")
        return date_range(
            start=min_value, end=max_value, freq="15min", inclusive="left"
        )


class LoadProfileFileCompleterLinearInterpolate(LoadProfileFileCompleterBase):
    def complete_data(self, profile_data):
        interpolation_array = self.create_interpolation_array(
            profile_data["timestamp"].min(), profile_data["timestamp"].max()
        )
        result = interp(
            interpolation_array,
            profile_data["timestamp"],
            profile_data["consumption_kwh"],
        )
        output = DataFrame(
            {
                "timestamp": interpolation_array,
                "consumption_kwh": result,
            }
        )
        profile_id = profile_data.at[0, "profile_id"]
        logger.info(f"Profile ID: {profile_id}")
        output.insert(2, "profile_id", profile_id)
        logger.info(f"{output.head()}")
        logger.info(f"{output.tail()}")
        logger.info(output.info())

        return output
