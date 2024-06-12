import uuid
from abc import ABC, abstractmethod
from typing import Any, Dict, List, Optional, Union
from uuid import UUID


class IService(ABC):

    @abstractmethod
    def create(self, user_id: str, **kwargs) -> Dict[str, Any]:
        pass

    @abstractmethod
    def read(self, item_id: Union[int, uuid.UUID]) -> Optional[Dict[str, Any]]:
        pass

    @abstractmethod
    def update(self, user_id: str, item_id: Union[int, UUID], **kwargs) -> Optional[Dict[str, Any]]:
        pass

    @abstractmethod
    def list(self, user_id: str) -> List[Dict[str, Any]]:
        pass

    def list_all(self) -> List[Dict[str, Any]]:
        pass

    def delete(self, item_id: Union[int, UUID]) -> bool:
        pass
