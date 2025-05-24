"""Service for managing load profiles based on predefined templates."""

from typing import Any, Dict, List, Optional
from uuid import UUID

from pandas import Timedelta

from app.api.v1.models.requests.load_profile.load_profile_create import (
    PersonProfileItem,
)
from app.data.interfaces.i_repository import IRepository
from app.data.interfaces.load.i_load_load_profile_repository import (
    ILoadProfileRepository,
)
from app.data.interfaces.load.i_predefined_templates_repository import (
    IPredefinedTemplatesRepository,
)
from app.data.interfaces.load.i_template_load_patterns_repository import (
    ITemplateConsumptionPatternsRepository,
)
from app.domain.interfaces.enums.load_source_enum import LoadSource
from app.domain.services.solar.consumption_pattern_service import (
    ConsumptionPatternService,
)
from app.utils.datetime_util import start_of_a_non_leap_year
from app.utils.logger import logger


class LoadProfileTemplateService:
    """
    Service responsible for operations related to predefined load profile
    templates, including creating profiles from templates and managing
    template-based consumption patterns.
    """

    def __init__(
        self,
        load_profile_repo: ILoadProfileRepository,
        pre_templates_repo: IPredefinedTemplatesRepository,
        template_patterns_repo: ITemplateConsumptionPatternsRepository,
        pre_master_templates_repo: IRepository,
        consumption_pattern_service: ConsumptionPatternService,
    ):
        self._load_profile_repo = load_profile_repo
        self._load_pre_templates_repo = pre_templates_repo
        self._template_patterns_repo = template_patterns_repo
        self._pre_master_templates_repo = pre_master_templates_repo
        self._consumption_pattern_service = consumption_pattern_service

    def create_or_update_load_predefined_template(
        self, user_id: UUID, house_id: UUID, template_id: int
    ) -> Any:  # Assuming LoadPredefinedTemplate
        """
        Creates or updates a load profile using a predefined template for a
        specific house and user.
        """
        load_profile = self._load_profile_repo.get_or_create_by_house_id(
            user_id, house_id, LoadSource.Template.value
        )
        return self._load_pre_templates_repo.create_or_update(
            load_profile.id, template_id
        )

    def get_load_predefined_template(
        self, user_id: UUID, house_id: UUID
    ) -> Optional[Any]:  # Assuming Optional[LoadPredefinedTemplate]
        """
        Retrieves the predefined template configuration for a load profile
        associated with a given house and user.
        """
        load_profiles = (
            self._load_profile_repo.get_load_profiles_by_user_id_and_house_id(
                user_id, house_id
            )
        )

        template_profile = next(
            (
                profile
                for profile in load_profiles
                if profile.source == LoadSource.Template.value
            ),
            None,
        )
        if template_profile:
            # Assuming get_by_profile_id takes profile_id (UUID)
            return self._load_pre_templates_repo.get_by_profile_id(
                template_profile.id
            )
        return None

    async def generate_profile_from_template(
        self,
        template_id: int,
        profile_items: List[PersonProfileItem],
    ) -> Dict[str, Any]:
        """
        Generates a 15-minute interval load profile for a full year based on a
        predefined template and household people profiles.
        """
        # Assuming read_or_none is a method in IRepository
        master_template = self._pre_master_templates_repo.read_or_none(
            template_id
        )

        if not master_template:
            raise ValueError(
                f"Master predefined template with ID {template_id} "
                f"not found or invalid."
            )

        total_daily_kwh_from_template = master_template.power_kw

        # Clear existing patterns for this template_id to prevent duplicates
        self._template_patterns_repo.delete_by_template_id(master_template.id)

        interval_minutes = 15

        normalized_daily_consumption_kwh = (
            self._consumption_pattern_service.generate_normalized_pattern(
                profile_items,
                total_daily_kwh_from_template,
                interval_minutes,
            )
        )

        start_of_a_year = start_of_a_non_leap_year()
        num_days_in_year = 365  # For a non-leap year

        template_patterns_to_save = []
        current_timestamp = start_of_a_year

        try:
            for _ in range(num_days_in_year):
                for consumption_value in normalized_daily_consumption_kwh:
                    template_patterns_to_save.append(
                        {
                            "template_id": master_template.id,
                            "timestamp": current_timestamp,
                            "consumption_kwh": consumption_value,
                        }
                    )
                    current_timestamp += Timedelta(minutes=interval_minutes)

            if template_patterns_to_save:
                self._template_patterns_repo.create_patterns_in_bulk(
                    template_patterns_to_save
                )

            logger.debug(
                "Generated %s load profile details for template ID %s",
                len(template_patterns_to_save),
                master_template.id,
            )

            return {
                "template_id": master_template.id,
                "message": "Load profile generated successfully from template",
                "details_count": len(template_patterns_to_save),
            }

        except Exception as e:
            logger.error(
                "Error generating profile from template %s: %s",
                template_id,
                str(e),
                exc_info=True,
            )
            raise
