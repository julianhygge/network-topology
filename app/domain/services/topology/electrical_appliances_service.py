from app.data.repositories.master.electrical_appliances_repository import (
    ElectricalAppliancesRepository,
)
from app.domain.services.base_service import BaseService


class ElectricalAppliancesService(BaseService):
    def __init__(self, repository: ElectricalAppliancesRepository):
        super().__init__(repository)
        self.repository = repository
