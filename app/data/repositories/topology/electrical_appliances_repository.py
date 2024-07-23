from app.data.repositories.base_repository import BaseRepository
from app.data.schemas.master.master_schema import ElectricalAppliances
from app.data.interfaces.topology.ielectrical_appliances_repository import IElectricalAppliancesRepository


class ElectricalAppliancesRepository(BaseRepository, IElectricalAppliancesRepository):
    model = ElectricalAppliances
    id_field = ElectricalAppliances.id

