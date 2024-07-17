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
        if house.load_profile is None:
            return False
        if house.has_solar and house.solar_kw is None:
            return False
        if house.has_battery:
            battery_fields = [
                'battery_type', 'voluntary_storage',
                'battery_peak_charging_rate', 'battery_peak_discharging_rate',
                'battery_total_kwh'
            ]
            for field in battery_fields:
                if getattr(house, field) is None:
                    return False
        if house.connection_kw is None:
            return False
        return True

    @staticmethod
    def _is_transformer_complete(transformer: Transformer) -> bool:
        required_fields = [
            'max_capacity_kw',
            'name',
            'primary_ampacity',
            'secondary_ampacity',
            'years_of_service',
            'digital_twin_model'
        ]
        for field in required_fields:
            if getattr(transformer, field) is None:
                return False
        if transformer.allow_export and transformer.forward_efficiency is None:
            return False
        return True
