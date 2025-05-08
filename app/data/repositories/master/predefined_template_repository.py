"""Module for the PredefinedMasterTemplatesRepository."""

from app.data.repositories.base_repository import BaseRepository
from app.data.schemas.master.master_schema import PredefinedTemplates


class PredefinedMasterTemplatesRepository(BaseRepository[PredefinedTemplates]):
    """
    Repository for managing PredefinedTemplates master data.

    This class extends `BaseRepository` to provide generic CRUD operations
    for the `PredefinedTemplates` model.
    """

    pass
