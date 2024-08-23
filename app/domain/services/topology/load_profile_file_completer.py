from pandas import DataFrame
from numpy import interp
from app.domain.interfaces.net_topology.iload_profile_file_completer import (
    ILoadProfileFileCompleter,
)
from scipy.interpolate import Akima1DInterpolator, CubicSpline, PchipInterpolator
from app.utils.logger import logger


class LoadProfileFileCompleterLinear(ILoadProfileFileCompleter):
    def complete_data(
        self,
        timestamps,
        consumption_kwh,
        interpolation_timestamps,
    ):
        logger.info("Completing data with linear interpolation")
        result = interp(
            interpolation_timestamps,
            timestamps,
            consumption_kwh,
        )
        return result


class LoadProfileFileCompleterSpline(ILoadProfileFileCompleter):
    def complete_data(
        self,
        timestamps,
        consumption_kwh,
        interpolation_timestamps,
    ) -> DataFrame:
        logger.info("Completing data with cubic spline interpolation")
        cubic_spline = CubicSpline(
            timestamps,
            consumption_kwh,
        )
        result = cubic_spline(interpolation_timestamps)
        return result


class LoadProfileFileCompleterPChip(ILoadProfileFileCompleter):
    def complete_data(self, timestamps, consumption_kwh, interpolation_timestamps):
        logger.info("Completing data with pchip interpolation")
        pchip = PchipInterpolator(timestamps, consumption_kwh)
        result = pchip(interpolation_timestamps)
        return result


class LoadProfileFileCompleterAkima1D(ILoadProfileFileCompleter):
    def complete_data(self, timestamps, consumption_kwh, interpolation_timestamps):
        logger.info("Completing data with akima 1d interpolation")
        akima1D = Akima1DInterpolator(timestamps, consumption_kwh)
        result = akima1D(interpolation_timestamps)
        return result
