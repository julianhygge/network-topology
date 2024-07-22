import datetime
from app.data.interfaces.iload_load_profile_repository import ILoadProfileRepository
from app.data.interfaces.iload_profile_details_repository import ILoadProfileDetailsRepository
from io import BytesIO
import pandas as pd
# from pandas import Timestamp

from app.data.interfaces.iuser_repository import IUserRepository
from app.data.interfaces.load.iload_profile_files_repository import ILoadProfileFilesRepository
from app.domain.interfaces.enums.load_source_enum import LoadSource
from app.domain.services.base_service import BaseService


class LoadProfileService(BaseService):
    def __init__(self,
                 repository: ILoadProfileRepository,
                 load_profile_files_repository: ILoadProfileFilesRepository,
                 user_repository: IUserRepository,
                 load_details_repository: ILoadProfileDetailsRepository):
        super().__init__(repository)
        self._load_profile_repository = repository
        self._load_details_repository = load_details_repository
        self._load_profile_files_repository = load_profile_files_repository
        self._user_repository = user_repository

    def _map_profile_to_dict(self, profile):
        data = {
            "profile_id": profile.id,
            "active": profile.active,
            "profile_name": profile.profile_name,
            "user_id": str(profile.user_id),
            "user": profile.user_id.name,
            "created_on": profile.created_on,
            "modified_on": profile.modified_on,
            "source": profile.source
        }
        if profile.source == LoadSource.File.value:
            file_name = self._load_profile_files_repository.get_file(profile.id).filename
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
                consumption_pattern[i] *= 1.3  # Increase consumption to reflect peak activity
            elif 6 <= hour < 8:  # From 6 am to 8 am
                consumption_pattern[i] *= 1.2  # Increase consumption to reflect peak activity

    @staticmethod
    def _normalize_adjusted_consumptions(adjusted_consumptions, original_total_consumption):
        """
        Normalizes the adjusted consumptions to ensure the total matches the original total consumption.
        """
        adjusted_total = sum(adjusted_consumptions)
        if adjusted_total == 0:
            return adjusted_consumptions

        normalization_factor = original_total_consumption / adjusted_total
        normalized_consumptions = [consumption * normalization_factor for consumption in adjusted_consumptions]
        return normalized_consumptions

    @staticmethod
    def _divide_consumption_in_intervals(total_consumption, interval_minutes=15):
        intervals_per_day = 1440 // interval_minutes
        consumption_per_interval = total_consumption / intervals_per_day
        return consumption_per_interval

    @staticmethod
    def _initialize_consumption_pattern(interval_minutes):
        return [1] * (1440 // interval_minutes)

    def _apply_profile_adjustments(self, people_profiles, consumption_pattern, interval_minutes):
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

    def list_profiles(self, user_id):
        get_private_profile_by_user = list(self._get_load_profiles_by_user_id(user_id))
        get_public_profiles = list(self._get_public_profiles())
        combined_profiles = get_public_profiles + get_private_profile_by_user
        return [self._map_profile_to_dict(profile) for profile in combined_profiles]

    async def upload_profile_service_file(self, user_id, profile_name: str, file,
                                          interval_15_minutes: bool):
        content = await file.read()
        if file.filename.endswith('.xlsx'):
            df = pd.read_excel(BytesIO(content))
        elif file.filename.endswith('.csv'):
            df = pd.read_csv(BytesIO(content))
        else:
            raise ValueError("Unsupported file type")

        if interval_15_minutes:
            self._validate_15_minute_intervals(df)

        with self.repository.database_instance.atomic():
            details, load_profile = self.process_dataframe(user_id, df, profile_name)
            self._load_details_repository.create_details_in_bulk(details)
            new_file = self._load_profile_files_repository.save_file(details[0]['profile_id'], file.filename, content)

            response = {
                "profile_id": load_profile.id,
                "file_id": new_file.id,
                "file_name": file.filename,
                "user": load_profile.user_id.name
            }
            return response

    def get_load_profile_file(self, profile_id):
        file = self._load_profile_files_repository.get_file(profile_id)
        return file

    @staticmethod
    async def read_excel(file):
        content = await file.read()
        df = pd.read_excel(BytesIO(content), engine='openpyxl')
        return df

    @staticmethod
    async def read_csv(file):
        content = await file.read()
        df = pd.read_csv(BytesIO(content))
        return df

    def process_dataframe(self, user_id, df: pd.DataFrame, profile_name: str):
        profile_data = {
            "active": True,
            "created_by": user_id,
            "modified_by": user_id,
            "user_id": user_id,
            "public": False,
            "profile_name": profile_name,
            "source": LoadSource.File
        }

        load_profile = self._load_profile_repository.create(**profile_data)
        details = df.to_dict('records')

        processed_details = []
        for detail in details:
            columns = list(detail.keys())
            datetime_column = columns[0]
            production_column = columns[1]
            processed_detail = {}
            # processed_detail = {
            #     "profile_id": load_profile.id,
            #     "timestamp": detail[datetime_column] if isinstance(detail[datetime_column], Timestamp)
            #     else datetime.datetime.strptime(detail[datetime_column], "%d/%m/%Y %H:%M"),
            #     "consumption_kwh": detail[production_column]
            # }
            processed_details.append(processed_detail)

        return processed_details, load_profile

    def _get_load_profiles_by_user_id(self, user_id):
        return self._load_profile_repository.get_load_profiles_by_user_id(user_id)

    def _get_public_profiles(self):
        return self._load_profile_repository.get_public_profiles()

    @staticmethod
    def _validate_15_minute_intervals(df: pd.DataFrame):
        timestamps = df.iloc[:, 0]
        timestamps = [datetime.datetime.strptime(ts, "%d/%m/%Y %H:%M") for ts in timestamps]
        interval_to_validate = 15  # minutes
        interval_in_seconds = 60 * interval_to_validate
        for i in range(1, len(timestamps)):
            if (timestamps[i] - timestamps[i - 1]).total_seconds() != interval_in_seconds:
                raise ValueError("Data is not in 15-minute intervals")
