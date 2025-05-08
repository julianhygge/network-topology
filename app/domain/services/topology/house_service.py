import uuid
from typing import Any, Dict, Optional, Union, cast

from app.data.interfaces.i_repository import IRepository
from app.data.schemas.transactional.topology_schema import (
    House as HouseSchema,  # Peewee model
)
from app.domain.services.topology.topology_service_base import (
    TopologyServiceBase,
)


class HouseService(TopologyServiceBase):
    repository: IRepository[HouseSchema]

    def __init__(self, repository: IRepository[HouseSchema]):
        super().__init__(repository)
        self.repository = repository

    def read(self, item_id: Union[int, uuid.UUID]) -> Optional[Dict[str, Any]]:
        item: Optional[HouseSchema] = self.repository.read(item_id)
        if item is None:
            return None
        item_dict = cast(Dict[str, Any], self.repository.to_dicts(item))
        status = self._get_house_status(item)
        item_dict["status"] = status
        return item_dict

    def get_flags_by_house_id(
        self, house_id: uuid.UUID
    ) -> Optional[Dict[str, Any]]:
        """
        Get flags for a specific house by its ID.

        Args:
            house_id (uuid.UUID): The ID of the house.

        Returns:
            Optional[Dict[str, Any]]: The house data with flags and status,
                                      or None if not found.
        """
        items: list[HouseSchema] = self.repository.filter(
            filters={"id": house_id}
        )

        if not items:  # Check if the list is empty
            return None

        item_dict = cast(Dict[str, Any], self.repository.to_dicts(items))
        return item_dict
