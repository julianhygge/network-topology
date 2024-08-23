from typing import Any, Dict, List, Union
from uuid import UUID

from app.data.interfaces.load.iload_generation_enginer_repository import (
    ILoadGenerationEngineRepository,
)
from app.data.interfaces.load.iload_load_profile_repository import (
    ILoadProfileRepository,
)
from app.data.interfaces.load.iload_profile_builder_repository import (
    ILoadProfileBuilderRepository,
)
from app.data.interfaces.load.iload_profile_details_repository import (
    ILoadProfileDetailsRepository,
)
from io import BytesIO
from pandas import (
    DatetimeIndex,
    NaT,
    Timedelta,
    Timestamp,
    date_range,
    DataFrame,
    read_csv,
    read_excel,
    to_datetime,
)
from app.data.interfaces.iuser_repository import IUserRepository
from app.data.interfaces.load.iload_profile_files_repository import (
    ILoadProfileFilesRepository,
)
from app.data.interfaces.load.ipredefined_templates_repository import (
    IPredefinedTemplatesRepository,
)
from app.domain.interfaces.enums.load_source_enum import LoadSource
from app.domain.interfaces.net_topology.iload_profile_file_completer import (
    BaseLoadProfileFileCompleter,
)
from app.domain.services.base_service import BaseService

from app.utils.logger import logger


class LoadProfileService(BaseService):
    def __init__(
        self,
        repository: ILoadProfileRepository,
        load_profile_files_repository: ILoadProfileFilesRepository,
        user_repository: IUserRepository,
        load_details_repository: ILoadProfileDetailsRepository,
        load_profile_builder_repository: ILoadProfileBuilderRepository,
        load_generation_engine_repository: ILoadGenerationEngineRepository,
        predefined_templates_repository: IPredefinedTemplatesRepository,
        load_profile_completer: BaseLoadProfileFileCompleter,
    ):
        super().__init__(repository)
        self._load_profile_repository = repository
        self._load_details_repository = load_details_repository
        self._load_profile_files_repository = load_profile_files_repository
        self._user_repository = user_repository
        self._load_profile_builder_repository = load_profile_builder_repository
        self._load_generation_engine_repository = load_generation_engine_repository
        self._load_predefined_templates_repository = predefined_templates_repository
        self._LOAD_PROFILE_MIN_DAYS = 100  # TODO: Take from config file
        self._load_profile_completer = load_profile_completer

    def _map_profile_to_dict(self, profile):
        data = {
            "house_id": profile.house_id.id,
            "profile_id": profile.id,
            "active": profile.active,
            "profile_name": profile.profile_name,
            "user_id": str(profile.user_id),
            "user": profile.user_id.name,
            "created_on": profile.created_on,
            "modified_on": profile.modified_on,
            "source": profile.source,
        }
        if profile.source == LoadSource.File.value:
            file_name = self._load_profile_files_repository.get_file(
                profile.id
            ).filename
            data["file_name"] = file_name

        return data

    @staticmethod
    def _apply_general_adjustments(consumption_pattern, interval_minutes):
        """
        Applies general adjustments to the consumption pattern based on common household activities.
        Reduces consumption from 11 pm to 6 am, and increases consumption between 7 pm and 10 pm,
        as well as between 6 am and 8 am.
        """
        for i in range(len(consumption_pattern)):
            hour = (i * interval_minutes) // 60
            if 23 <= hour or hour < 6:  # From 11 pm to 6 am
                consumption_pattern[i] *= 0.5  # Significantly reduce consumption
            elif 19 <= hour < 22:  # From 7 pm to 10 pm
                consumption_pattern[
                    i
                ] *= 1.3  # Increase consumption to reflect peak activity
            elif 6 <= hour < 8:  # From 6 am to 8 am
                consumption_pattern[
                    i
                ] *= 1.2  # Increase consumption to reflect peak activity

    @staticmethod
    def _normalize_adjusted_consumptions(
        adjusted_consumptions, original_total_consumption
    ):
        """
        Normalizes the adjusted consumptions to ensure the total matches the original total consumption.
        """
        adjusted_total = sum(adjusted_consumptions)
        if adjusted_total == 0:
            return adjusted_consumptions

        normalization_factor = original_total_consumption / adjusted_total
        normalized_consumptions = [
            consumption * normalization_factor for consumption in adjusted_consumptions
        ]
        return normalized_consumptions

    @staticmethod
    def _divide_consumption_in_intervals(total_consumption, interval_minutes=15):
        intervals_per_day = 1440 // interval_minutes
        consumption_per_interval = total_consumption / intervals_per_day
        return consumption_per_interval

    @staticmethod
    def _initialize_consumption_pattern(interval_minutes):
        return [1] * (1440 // interval_minutes)

    def _apply_profile_adjustments(
        self, people_profiles, consumption_pattern, interval_minutes
    ):
        """
        Applies consumption adjustments based on each person's work profile within the household.
        """
        for person in people_profiles:
            if person.get("works_at_home"):
                self._adjust_for_home_workers(consumption_pattern, interval_minutes)
            elif person.get("work_schedule") == "Night":
                self._adjust_for_night_workers(consumption_pattern, interval_minutes)
            else:
                # For individuals working outside (daytime workers or variable schedules)
                # and for households without specific profile info
                self._adjust_for_day_workers(consumption_pattern, interval_minutes)

    def _adjust_for_home_workers(self, consumption_pattern, interval_minutes):
        """
        Apply adjustments for individuals working from home during daytime. This includes the general
        adjustments for typical household activity patterns.
        """
        self._apply_general_adjustments(consumption_pattern, interval_minutes)

    def _adjust_for_night_workers(self, consumption_pattern, interval_minutes):
        """
        For night workers, apply adjustments considering they are away at night and likely active
        at home during the day. This adjusts for lower nighttime consumption.
        """
        self._apply_general_adjustments(consumption_pattern, interval_minutes)

    def _adjust_for_day_workers(self, consumption_pattern, interval_minutes):
        """
        Apply adjustments for those working outside during the day. This includes increasing
        consumption in the early morning and evening to reflect typical patterns of leaving and returning home.
        """
        self._apply_general_adjustments(consumption_pattern, interval_minutes)

    def delete_profile(self, profile_id):
        self._load_details_repository.delete_by_profile_id(profile_id)
        delete_profile_result = self._load_profile_repository.delete(profile_id)
        return delete_profile_result

    def list_profiles(self, user_id, house_id):
        get_private_profile_by_user = list(
            self._get_load_profiles_by_user_id(user_id, house_id)
        )
        get_public_profiles = list(self._get_public_profiles())
        combined_profiles = get_public_profiles + get_private_profile_by_user
        return [self._map_profile_to_dict(profile) for profile in combined_profiles]

    def _find_time_format(self, df: DataFrame) -> str:
        """
        Finds the time format used in the data frame, returns it and converts the timestamps to datetime objects.
        Raises a ValueError if the timestamps do not match any of the formats
        """
        # TODO: Pull formats from config
        formats = [
            "%d/%m/%Y %H:%M",
            "%d-%m-%Y %H:%M",
            "%m/%d/%Y %H:%M",
            "%Y-%m-%d %H:%M",
            "%Y/%m/%d %H:%M",
            "%d/%m/%Y",
            "%d-%m-%Y",
            "%m/%d/%Y",
            "%Y-%m-%d",
            "%Y/%m/%d",
        ]
        for format in formats:
            try:
                df["timestamp"] = to_datetime(df["timestamp"], format=format)
                return format
            except ValueError:
                pass
        raise ValueError("Could not determine time format")

    def _validate_and_prepare_profile_data(self, df: DataFrame) -> None:
        """Validates and prepares the data frame for processing."""
        if df.empty:
            raise ValueError("Empty data frame")
        if len(df.columns) < 2:
            raise ValueError("Data frame must have at least 2 columns")
        number_of_columns_to_remove = len(df.columns) - 2
        if number_of_columns_to_remove > 0:
            df.drop(df.columns[-number_of_columns_to_remove:], axis=1, inplace=True)

        df.rename(
            columns={df.columns[0]: "timestamp", df.columns[1]: "consumption_kwh"},
            inplace=True,
        )

        self._find_time_format(df)

        min_date = df.iat[0, 0]
        max_date = df.iat[-1, 0]
        if min_date >= max_date:
            raise ValueError("Dates are not ascending")
        diff = max_date - min_date
        if diff.days > 366:  # TODO: Handle specific year
            raise ValueError("Data spans more than a year")
        if diff.days < self._LOAD_PROFILE_MIN_DAYS:
            raise ValueError("Data spans less than a day")

    async def upload_profile_service_file(
        self,
        user_id,
        profile_name: str,
        file,
        interval_15_minutes: bool,
        house_id: UUID,
    ) -> Dict[str, Union[str, UUID]]:
        content = await file.read()
        if file.filename.endswith(".xlsx"):
            df = read_excel(BytesIO(content))
        elif file.filename.endswith(".csv"):
            df = read_csv(BytesIO(content))
        else:
            raise ValueError("Unsupported file type")

        self._validate_and_prepare_profile_data(df)
        if interval_15_minutes:
            self._validate_intervals(df)
        else:
            day = 60 * 24
            # TODO: Pull from config
            self._validate_intervals(df, day, False)

        with self.repository.database_instance.atomic():
            details, load_profile = self.process_dataframe(
                user_id, df, profile_name, house_id, interval_15_minutes
            )
            self._load_details_repository.create_details_in_bulk(details)
            new_file = self._load_profile_files_repository.save_file(
                details[0]["profile_id"], file.filename, content
            )

            response = {
                "profile_id": load_profile.id,
                "file_id": new_file.id,
                "file_name": file.filename,
                "user": load_profile.user_id.name,
                "house_id": load_profile.house_id.id,
            }
            return response

    def save_load_profile_items(self, user_id: UUID, house_id: UUID, items: List[dict]):
        load_profile = self._load_profile_repository.get_or_create_by_house_id(
            user_id, house_id, LoadSource.Builder
        )
        profile_id = load_profile.id

        existing_items = self._load_profile_builder_repository.get_items_by_profile_id(
            profile_id
        )
        existing_ids = set(item.id for item in existing_items)

        to_create = []
        to_update = []
        new_ids = set()

        for item in items:
            item["profile_id"] = profile_id

            if "id" in item and item["id"] in existing_ids:
                to_update.append(item)
                new_ids.add(item["id"])
            else:
                item["modified_by"] = user_id
                item["created_by"] = user_id
                item.pop("id", None)
                to_create.append(item)

        to_delete = existing_ids - new_ids

        if to_delete:
            for item_id in to_delete:
                self._load_profile_builder_repository.delete(item_id)
        if to_create:
            self._load_profile_builder_repository.create_items_in_bulk(to_create)
        if to_update:
            self._load_profile_builder_repository.update_items_in_bulk(to_update)

        return (
            self._load_profile_builder_repository.get_items_by_profile_id(profile_id),
            profile_id,
        )

    def get_load_profile_builder_items(self, user_id: UUID, house_id: UUID):
        load_profile = self._load_profile_repository.get_or_create_by_house_id(
            user_id, house_id, LoadSource.Builder.value
        )
        return (
            self._load_profile_builder_repository.get_items_by_profile_id(load_profile),
            load_profile.id,
        )

    def get_load_profile_file(self, profile_id):
        file = self._load_profile_files_repository.get_file(profile_id)
        return file

    @staticmethod
    async def read_excel(file) -> DataFrame:
        content = await file.read()
        df = read_excel(BytesIO(content), engine="openpyxl")
        return df

    @staticmethod
    async def read_csv(file) -> DataFrame:
        content = await file.read()
        df = read_csv(BytesIO(content))
        return df

    @staticmethod
    def days_in_year(timestamp: Timestamp) -> int:
        return 366 if timestamp.is_leap_year else 365

    def create_interpolation_array(
        self, min_date: Timestamp, max_date: Timestamp
    ) -> DatetimeIndex:
        """Create the interpolation timestamp array based on the min and max date."""
        min_value = min_date.floor("15min")
        days = self.days_in_year(min_date)
        min_value_plus_year = min_value + Timedelta(days=days)
        max_value = max_date.ceil("1h")

        if min_value_plus_year != NaT:
            min_value_plus_year = min_value_plus_year.ceil("1h")
            max_value = max(max_value, min_value_plus_year)
        return date_range(
            start=min_value, end=max_value, freq="15min", inclusive="left"
        )

    def process_dataframe(
        self,
        user_id,
        df: DataFrame,
        profile_name: str,
        house_id: UUID,
        is_15_mins_interval: bool,
    ) -> tuple[list[Dict[str, Any]], Dict[str, Any]]:
        profile_data = {
            "active": True,
            "created_by": user_id,
            "modified_by": user_id,
            "user_id": user_id,
            "public": False,
            "profile_name": profile_name,
            "source": LoadSource.File,
            "house_id": house_id,
        }

        load_profile = self._load_profile_repository.create(**profile_data)
        if is_15_mins_interval:
            df.insert(2, "profile_id", load_profile.id)
            details = df.to_dict("records")
            return details, load_profile
        interpolation_array = self.create_interpolation_array(
            df["timestamp"].min(), df["timestamp"].max()
        )
        timestamps = df["timestamp"]
        consumption_kwh = df["consumption_kwh"]
        result = self._load_profile_completer.complete_data(
            timestamps, consumption_kwh, interpolation_array
        )
        df = DataFrame({"timestamp": interpolation_array, "consumption_kwh": result})
        df.insert(2, "profile_id", load_profile.id)
        logger.info(df.head())
        logger.info(df.tail())
        details = df.to_dict("records")
        return details, load_profile

    def _get_load_profiles_by_user_id(self, user_id, house_id):
        return self._load_profile_repository.get_load_profiles_by_user_id_and_house_id(
            user_id, house_id
        )

    def _get_public_profiles(self):
        return self._load_profile_repository.get_public_profiles()

    @staticmethod
    def _validate_intervals(
        df: DataFrame, minutes: int = 15, exact: bool = True
    ) -> None:
        """
        Validates that the data is in the specified interval if exact is True. Otherwise, validates
        that the data has all intervals smaller than or equal to the specified minutes.
        """
        timestamps = df.iloc[:, 0]
        interval_in_seconds = 60 * minutes
        for i in range(1, len(timestamps)):
            diff = timestamps[i] - timestamps[i - 1]
            if exact and diff.total_seconds() != interval_in_seconds:
                raise ValueError(f"Data is not in {minutes}-minute intervals")
            if not exact and diff.total_seconds() > interval_in_seconds:
                raise ValueError(f"Data has intervals greater than {minutes} minutes")

    def save_load_generation_engine(self, user_id: UUID, house_id: UUID, data: dict):
        load_profile = self._load_profile_repository.get_or_create_by_house_id(
            user_id, house_id, LoadSource.Engine.value
        )
        profile_id = load_profile.id

        engine_data = {
            "user_id": user_id,
            "profile_id": load_profile,
            "type": data["type"],
            "average_kwh": data.get("average_kwh"),
            "average_monthly_bill": data.get("average_monthly_bill"),
            "max_demand_kw": data.get("max_demand_kw"),
            "created_by": user_id,
            "modified_by": user_id,
        }
        self._load_generation_engine_repository.delete_by_profile_id(profile_id)
        return self._load_generation_engine_repository.model.get_or_create(
            profile_id=profile_id, defaults=engine_data
        )[0]

    def get_load_generation_engine(self, user_id: UUID, house_id: UUID):
        load_profiles = (
            self._load_profile_repository.get_load_profiles_by_user_id_and_house_id(
                user_id, house_id
            )
        )

        engine_profile = next(
            (
                profile
                for profile in load_profiles
                if profile.source == LoadSource.Engine.value
            ),
            None,
        )

        if engine_profile:
            return self._load_generation_engine_repository.model.get_or_none(
                profile_id=engine_profile.id
            )
        else:
            return None

    def create_or_update_load_predefined_template(
        self, user_id: UUID, house_id: UUID, template_id: int
    ):
        load_profile = self._load_profile_repository.get_or_create_by_house_id(
            user_id, house_id, LoadSource.Template.value
        )
        return self._load_predefined_templates_repository.create_or_update(
            load_profile.id, template_id
        )

    def get_load_predefined_template(self, user_id: UUID, house_id: UUID):
        load_profiles = (
            self._load_profile_repository.get_load_profiles_by_user_id_and_house_id(
                user_id, house_id
            )
        )

        template = next(
            (
                profile
                for profile in load_profiles
                if profile.source == LoadSource.Template.value
            ),
            None,
        )
        if template:
            return self._load_predefined_templates_repository.get_by_profile_id(
                template.id
            )
        else:
            return None
