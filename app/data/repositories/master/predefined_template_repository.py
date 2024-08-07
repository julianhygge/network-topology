from app.data.repositories.base_repository import BaseRepository
from app.data.schemas.master.master_schema import PredefinedTemplates


class PredefinedMasterTemplatesRepository(BaseRepository):
    model = PredefinedTemplates
    id_field = PredefinedTemplates.id
