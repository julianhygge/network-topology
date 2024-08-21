from pandas import DataFrame
from numpy import interp
from app.domain.interfaces.net_topology.iload_profile_file_completer import (
    BaseLoadProfileFileCompleter,
)
from scipy.interpolate import CubicSpline


class LoadProfileFileCompleterLinearInterpolate(BaseLoadProfileFileCompleter):
    def complete_data(
        self,
        timestamps,
        consumption_kwh,
        interpolation_timestamps,
    ):
        result = interp(
            interpolation_timestamps,
            timestamps,
            consumption_kwh,
        )
        return result


class LoadProfileFileCompleterSpline(BaseLoadProfileFileCompleter):
    def complete_data(
        self,
        timestamps,
        consumption_kwh,
        interpolation_timestamps,
    ) -> DataFrame:
        cubic_spline = CubicSpline(
            timestamps,
            consumption_kwh,
        )
        result = cubic_spline(interpolation_timestamps)
        return result
