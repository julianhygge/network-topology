from app.data.interfaces.irepository import IRepository
from app.data.schemas.transactional.topology_schema import House, Transformer
from app.domain.services.base_service import BaseService


class TopologyServiceBase(BaseService):
    def __init__(self,
                 repository: IRepository):
        super().__init__(repository)
        self.repository = repository

    @staticmethod
    def _is_house_complete(house: House) -> bool:
        if not house.load_profile or house.load_profile.strip() == '':
            return False
        if house.has_solar and (house.solar_kw is None or house.solar_kw <= 0):
            return False
        if house.has_battery:
            battery_fields = [
                ('battery_type', ''),
                ('voluntary_storage', None),
                ('battery_peak_charging_rate', 0),
                ('battery_peak_discharging_rate', 0),
                ('battery_total_kwh', 0)
            ]
            for field, empty_value in battery_fields:
                value = getattr(house, field)
                if value is None or value == empty_value:
                    return False
        if house.connection_kw is None or house.connection_kw <= 0:
            return False
        if not house.house_type or house.house_type.strip() == '':
            return False
        return True

    @staticmethod
    def _is_transformer_complete(transformer: Transformer) -> bool:
        required_fields = [
            ('max_capacity_kw', 0),
            ('name', ''),
            ('primary_ampacity', 0),
            ('secondary_ampacity', 0),
            ('years_of_service', 0),
            ('digital_twin_model', None)
        ]
        for field, empty_value in required_fields:
            value = getattr(transformer, field)
            if value is None or value == empty_value:
                return False
        if transformer.allow_export and (transformer.forward_efficiency is None or transformer.forward_efficiency <= 0):
            return False
        return True
