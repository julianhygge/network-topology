import uuid
from abc import ABC, abstractmethod
from typing import Any, Dict, Optional, Union
from uuid import UUID

class INodeService(ABC):
    @abstractmethod
    def read(self, item_id: Union[int, uuid.UUID]) -> Optional[Dict[str, Any]]:
        pass

    @abstractmethod
    def get_breadcrumb_navigation_path(self, node_id: UUID) -> Dict[str, Any]:
        pass
