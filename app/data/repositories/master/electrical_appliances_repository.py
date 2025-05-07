"""Module for the ElectricalAppliancesRepository."""
from app.data.repositories.base_repository import BaseRepository
from app.data.schemas.master.master_schema import ElectricalAppliances


class ElectricalAppliancesRepository(BaseRepository[ElectricalAppliances]):
    """
    Repository for managing ElectricalAppliances data.

    This class extends `BaseRepository` to provide generic CRUD operations
    for the `ElectricalAppliances` model.
    """
    pass
