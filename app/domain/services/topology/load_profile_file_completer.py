from pandas import DataFrame
from numpy import interp
from app.domain.interfaces.net_topology.iload_profile_file_completer import (
    BaseLoadProfileFileCompleter,
)
from scipy.interpolate import Akima1DInterpolator, CubicSpline, PchipInterpolator


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


class LoadProfileFileCompleterPChip(BaseLoadProfileFileCompleter):
    def complete_data(self, timestamps, consumption_kwh, interpolation_timestamps):
        pchip = PchipInterpolator(timestamps, consumption_kwh)
        result = pchip(interpolation_timestamps)
        return result


class LoadProfileFileCompleterAkima1D(BaseLoadProfileFileCompleter):
    def complete_data(self, timestamps, consumption_kwh, interpolation_timestamps):
        akima1D = Akima1DInterpolator(timestamps, consumption_kwh)
        result = akima1D(interpolation_timestamps)
        return result
