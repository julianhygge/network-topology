from app.domain.services.base_service import BaseService
from app.data.repositories.topology.electrical_appliances_repository import ElectricalAppliancesRepository


class ElectricalAppliancesService(BaseService):
    def __init__(self, repository: ElectricalAppliancesRepository):
        super().__init__(repository)
        self.repository = repository
