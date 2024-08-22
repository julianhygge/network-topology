from app.data.repositories.base_repository import BaseRepository
from app.data.schemas.master.master_schema import ElectricalAppliances


class ElectricalAppliancesRepository(BaseRepository):
    model = ElectricalAppliances
    id_field = ElectricalAppliances.id

