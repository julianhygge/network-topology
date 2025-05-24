"""Service for managing load profile files."""

from io import BytesIO
from typing import Any, Dict, List, Tuple, Union
from uuid import UUID

import pandas  # Import pandas
from fastapi import UploadFile
from pandas import (
    DataFrame,
    DatetimeIndex,
    NaT,
    Timedelta,
    Timestamp,
    date_range,
    read_csv,
    read_excel,
    to_datetime,
)

from app.config.i_configuration import IConfiguration
from app.data.interfaces.load.i_load_load_profile_repository import (
    ILoadProfileRepository,
)
from app.data.interfaces.load.i_load_profile_details_repository import (
    ILoadProfileDetailsRepository,
)
from app.data.interfaces.load.i_load_profile_files_repository import (
    ILoadProfileFilesRepository,
)
from app.domain.interfaces.enums.load_source_enum import LoadSource
from app.domain.interfaces.net_topology.i_load_profile_file_completer import (
    ILoadProfileFileCompleter,
)
from app.utils.logger import logger


class LoadProfileFileService:
    """
    Service responsible for handling load profile file operations including
    upload, validation, reading, and processing.
    """

    def __init__(
        self,
        load_profile_repo: ILoadProfileRepository,
        load_profile_files_repo: ILoadProfileFilesRepository,
        load_details_repo: ILoadProfileDetailsRepository,
        load_profile_completer: ILoadProfileFileCompleter,
        conf: IConfiguration,
    ):
        self._load_profile_repo = load_profile_repo
        self._load_profile_files_repository = load_profile_files_repo
        self._load_details_repository = load_details_repo
        self._load_profile_completer = load_profile_completer
        self._load_profile_min_days = conf.load_profile.min_days
        self._load_profile_time_formats = conf.load_profile.time_formats
        self._max_interval_length = conf.load_profile.max_interval_length

    @staticmethod
    def _find_time_format(df: DataFrame, formats: list[str]) -> str:
        """
        Finds the time format used in the data frame, returns it and converts
        the timestamps to datetime objects.
        Raises a ValueError if the timestamps do not match any of the formats.
        """
        for time_format in formats:
            try:
                df["timestamp"] = to_datetime(
                    df["timestamp"], format=time_format
                )
                return time_format
            except ValueError:
                pass
        raise ValueError("Could not determine time format for timestamps.")

    def _validate_and_prepare_profile_data(self, df: DataFrame) -> None:
        """Validates and prepares the data frame for processing."""
        if df.empty:
            raise ValueError("Empty data frame provided for load profile.")
        if len(df.columns) < 2:
            raise ValueError(
                "Data frame must have at least 2 columns "
                "(timestamp, consumption_kwh)."
            )
        # Keep only the first two columns if more are present
        if len(df.columns) > 2:
            df.drop(df.columns[2:], axis=1, inplace=True)

        df.rename(
            columns={
                df.columns[0]: "timestamp",
                df.columns[1]: "consumption_kwh",
            },
            inplace=True,
        )

        self._find_time_format(df, self._load_profile_time_formats)

        # Ensure 'consumption_kwh' is numeric
        df["consumption_kwh"] = pandas.to_numeric(
            df["consumption_kwh"], errors="coerce"
        )
        if df["consumption_kwh"].isnull().any():
            raise ValueError("Consumption data contains non-numeric values.")

        min_date = df["timestamp"].min()
        max_date = df["timestamp"].max()

        if min_date >= max_date:
            raise ValueError(
                "Start date must be before end date in profile data."
            )
        diff = max_date - min_date
        if diff.days > 366:  # Allowing for leap years
            raise ValueError("Data spans more than a year.")
        if diff.days < self._load_profile_min_days:
            raise ValueError(
                f"Data must span at least {self._load_profile_min_days} days."
            )

    @staticmethod
    def _validate_intervals(
        df: DataFrame, minutes: int = 15, exact: bool = True
    ) -> None:
        """
        Validates that the data is in the specified interval
        if exact is True. Otherwise, validates that the data has all
        intervals smaller than or equal to the specified minutes.
        """
        timestamps = df["timestamp"]
        interval_in_seconds = 60 * minutes
        for i in range(1, len(timestamps)):
            diff = (
                timestamps.iloc[i] - timestamps.iloc[i - 1]
            ).total_seconds()
            if exact and diff != interval_in_seconds:
                raise ValueError(
                    f"Data is not in exact {minutes}-minute intervals."
                )
            if not exact and diff > interval_in_seconds:
                raise ValueError(
                    f"Data has intervals greater than {minutes} minutes."
                )

    @staticmethod
    async def _read_file_content(file: UploadFile) -> DataFrame:
        """Reads content from an file (Excel or CSV) into a DataFrame."""
        filename = file.filename
        if not filename:
            raise ValueError("Uploaded file must have a filename.")
        content = await file.read()
        if filename.lower().endswith(".xlsx"):
            df = read_excel(BytesIO(content), engine="openpyxl")
        elif filename.lower().endswith(".csv"):
            df = read_csv(BytesIO(content))
        else:
            raise ValueError(
                "Unsupported file type. Please upload .xlsx or .csv."
            )
        return df

    @staticmethod
    def _days_in_year(timestamp: Timestamp) -> int:
        """Determines if the year of the timestamp is a leap year."""
        return 366 if timestamp.is_leap_year else 365

    def _create_interpolation_array(
        self, min_date: Timestamp, max_date: Timestamp
    ) -> DatetimeIndex:
        """Create interpolation timestamp array based on min and max date."""
        min_value = min_date.floor("15min")
        days = self._days_in_year(min_date)
        min_value_plus_year = min_value + Timedelta(days=days)
        max_value = max_date.ceil("1h")

        if min_value_plus_year is not NaT:  # Check for NaT explicitly
            min_value_plus_year = min_value_plus_year.ceil("1h")
            max_value = max(max_value, min_value_plus_year)
        return date_range(
            start=min_value, end=max_value, freq="15min", inclusive="left"
        )

    def _process_dataframe_for_db(
        self,
        user_id: UUID,
        df: DataFrame,
        profile_name: str,
        house_id: UUID,
        is_15_mins_interval: bool,
    ) -> Tuple[List[Dict[str, Any]], Any]:
        """Processes the DataFrame and prepares data for database insertion."""
        profile_data = {
            "active": True,
            "created_by": user_id,
            "modified_by": user_id,
            "user_id": user_id,
            "public": False,
            "profile_name": profile_name,
            "source": LoadSource.File.value,
            "house_id": house_id,
        }

        load_profile_obj = self._load_profile_repo.create(profile_data)
        if is_15_mins_interval:
            # Insert at the beginning, converting UUID to str for DataFrame
            df.insert(0, "profile_id", str(load_profile_obj.id))
            details = df.to_dict(orient="records")  # Use orient for clarity
            return details, load_profile_obj

        interpolation_array = self._create_interpolation_array(
            df["timestamp"].min(), df["timestamp"].max()
        )
        timestamps_series = df["timestamp"]  # This is pd.Series
        consumption_kwh_series = df["consumption_kwh"]  # This is pd.Series
        # Assuming complete_data expects Series for timestamps and consumption
        result = self._load_profile_completer.complete_data(
            timestamps_series, consumption_kwh_series, interpolation_array
        )
        completed_df = DataFrame(
            {"timestamp": interpolation_array, "consumption_kwh": result}
        )
        # Insert at the beginning, converting UUID to str for DataFrame
        completed_df.insert(0, "profile_id", str(load_profile_obj.id))
        logger.info("Processed DataFrame head: %s", completed_df.head())
        logger.info("Processed DataFrame tail: %s", completed_df.tail())
        details = completed_df.to_dict("records")
        return details, load_profile_obj

    async def upload_profile_file(
        self,
        user_id: UUID,
        profile_name: str,
        file: UploadFile,
        interval_15_minutes: bool,
        house_id: UUID,
    ) -> Dict[str, Union[str, UUID]]:
        """
        Uploads, validates, processes, and saves a load profile file.
        """
        df = await self._read_file_content(file)
        self._validate_and_prepare_profile_data(df)

        if interval_15_minutes:
            self._validate_intervals(df)  # Default 15 mins, exact
        else:
            # Assuming max_interval_length is in hours, convert to minutes
            max_interval_minutes = self._max_interval_length * 60
            self._validate_intervals(
                df, minutes=max_interval_minutes, exact=False
            )

        details, load_profile_obj = self._process_dataframe_for_db(
            user_id, df, profile_name, house_id, interval_15_minutes
        )
        # Bulk creation should be efficient
        self._load_details_repository.create_details_in_bulk(details)

        file.file.seek(0)
        file_content = await file.read()
        filename_to_save = file.filename if file.filename else "uploaded_file"

        new_file_record = self._load_profile_files_repository.save_file(
            load_profile_obj.id, filename_to_save, file_content
        )

        response = {
            "profile_id": load_profile_obj.id,
            "file_id": new_file_record.id,
            "file_name": new_file_record.filename,
            "user_id": str(load_profile_obj.user_id),
            "house_id": str(load_profile_obj.house_id),
        }
        return response

    def get_load_profile_file_content(self, profile_id: UUID):
        """Retrieves the raw file content for a given profile ID."""
        file_record = self._load_profile_files_repository.get_file(profile_id)
        if not file_record:
            raise ValueError(f"No file found for profile ID {profile_id}")
        return file_record
