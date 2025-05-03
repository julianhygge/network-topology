import uuid
from typing import Any, Dict, Optional, Union

from app.data.interfaces.i_repository import IRepository
from app.domain.services.topology.topology_service_base import \
    TopologyServiceBase


class HouseService(TopologyServiceBase):
    def __init__(self, repository: IRepository):
        super().__init__(repository)
        self.repository = repository

    def read(self, item_id: Union[int, uuid.UUID]) -> Optional[Dict[str, Any]]:
        item = self.repository.read(item_id)
        item_dict = self.repository.to_dicts(item)
        status = self._get_house_status(item)
        item_dict["status"] = status
        return item_dict
