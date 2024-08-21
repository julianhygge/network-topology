from pandas import DataFrame
from numpy import interp
from app.domain.interfaces.net_topology.iload_profile_file_completer import (
    BaseLoadProfileFileCompleter,
)


class LoadProfileFileCompleterLinearInterpolate(BaseLoadProfileFileCompleter):
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
        output.insert(2, "profile_id", profile_id)

        return output
