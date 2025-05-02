import datetime
import uuid
from typing import List, Dict, Any, Optional, Union
from app.data.interfaces.irepository import IRepository
from app.domain.interfaces.i_service import IService


class BaseService(IService):
    def __init__(self,
                 repository: IRepository):
        self.repository = repository

    def create(self, user_id: str, **kwargs) -> Dict[str, Any]:
        kwargs["created_by"] = user_id
        kwargs["modified_by"] = user_id
        kwargs["active"] = True
        created = self.repository.create(**kwargs)
        created_dicts = self.repository.to_dicts(created)
        return created_dicts

    def read(self, item_id: Union[int, uuid.UUID]) -> Optional[Dict[str, Any]]:
        items = self.repository.read(item_id)
        item_dict = self.repository.to_dicts(items)
        return item_dict

    def update(self, user_id: str, item_id: int, **kwargs) -> Optional[Dict[str, Any]]:
        kwargs["modified_on"] = datetime.datetime.utcnow()
        kwargs["modified_by"] = user_id
        update_result = self.repository.update(item_id, **kwargs)
        if update_result:
            updated_dicts = self.repository.read(item_id)
            if updated_dicts:
                return self.repository.to_dicts(updated_dicts)
        return None

    def delete(self, item_id: int) -> bool:
        deleted = self.repository.delete(item_id)
        if deleted:
            return True
        return False

    def list(self, user_id: str) -> List[Dict[str, Any]]:
        list_items = self.repository.list_actives()
        return self.repository.to_dicts(list_items)

    def list_all(self) -> List[Dict[str, Any]]:
        list_items = self.repository.list_actives()
        return self.repository.to_dicts(list_items)
