from typing import Any, Union, Tuple

from app.data.interfaces.irepository import IRepository
from app.data.schemas.enums.enums import NodeStatusEnum
from app.data.schemas.transactional.topology_schema import House, Transformer
from app.domain.services.base_service import BaseService


class TopologyServiceBase(BaseService):
    def __init__(self, repository: IRepository):
        super().__init__(repository)
        self.repository = repository

    @staticmethod
    def _is_house_complete(house: House) -> bool:
        if not house.load_profile or house.load_profile.strip() == "":
            return False
        if house.has_solar and (house.solar_kw is None or house.solar_kw <= 0):
            return False
        if house.has_battery:
            battery_fields = [
                ("battery_type", ""),
                ("voluntary_storage", None),
                ("battery_peak_charging_rate", 0),
                ("battery_peak_discharging_rate", 0),
                ("battery_total_kwh", 0),
            ]
            for field, empty_value in battery_fields:
                value = getattr(house, field)
                if value is None or value == empty_value:
                    return False
        if house.connection_kw is None or house.connection_kw <= 0:
            return False
        if not house.house_type or house.house_type.strip() == "":
            return False
        return True

    @staticmethod
    def _is_transformer_complete(transformer: Transformer) -> bool:
        required_fields = [
            ("max_capacity_kw", 0),
            ("name", ""),
            ("primary_ampacity", 0),
            ("secondary_ampacity", 0),
            ("years_of_service", 0),
            ("digital_twin_model", None),
        ]
        for field, empty_value in required_fields:
            value = getattr(transformer, field)
            if value is None or value == empty_value:
                return False
        if transformer.allow_export and (
            transformer.forward_efficiency is None
            or transformer.forward_efficiency <= 0
        ):
            return False
        return True

    @staticmethod
    def _to_status_enum(at_least_one_filled: bool, all_filled: bool) -> NodeStatusEnum:
        if not at_least_one_filled:
            return NodeStatusEnum.Empty
        if not all_filled:
            return NodeStatusEnum.InProgress
        return NodeStatusEnum.Complete

    @staticmethod
    def _check_required_fields(
        node: Union[House, Transformer], required_fields: list[Tuple[str, Any]]
    ) -> NodeStatusEnum:
        """
        Check if the required fields are filled in the given node i.e. not the default value.
        If at least one field is filled, the status is InProgress.
        If all fields are filled, the status is Complete.
        If no field is filled, the status is Empty.
        """
        check_properties = [
            getattr(node, field) != empty_value
            for field, empty_value in required_fields
        ]
        at_least_one_filled = any(check_properties)
        all_filled = all(check_properties)
        return TopologyServiceBase._to_status_enum(at_least_one_filled, all_filled)

    @staticmethod
    def _get_transformer_status(transformer: Transformer) -> NodeStatusEnum:
        required_fields = [
            ("max_capacity_kw", None),
            ("name", None),
            ("primary_ampacity", None),
            ("secondary_ampacity", None),
            ("years_of_service", None),
        ]
        required_fields_check = TopologyServiceBase._check_required_fields(
            transformer, required_fields
        )
        if required_fields_check != NodeStatusEnum.Complete:
            return required_fields_check

        if transformer.allow_export and (
            transformer.forward_efficiency is None
            or transformer.forward_efficiency <= 0
        ):
            return NodeStatusEnum.InProgress
        return NodeStatusEnum.Complete
