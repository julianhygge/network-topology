from app.data.interfaces.topology.ielectrical_appliances_repository import IElectricalAppliancesRepository
from app.domain.interfaces.net_topology.ielectrical_appliances_service import IElectricalAppliancesService
from app.domain.services.base_service import BaseService


class ElectricalAppliancesService(BaseService, IElectricalAppliancesService):
    def __init__(self, repository: IElectricalAppliancesRepository):
        super().__init__(repository)
        self.repository = repository

    def get_electrical_appliances(self):
        data = self.repository.list()
        return data


