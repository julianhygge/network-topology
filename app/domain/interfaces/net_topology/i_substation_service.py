from abc import ABC, abstractmethod
from typing import Any, Dict
from uuid import UUID


class ISubstationService(ABC):

    @abstractmethod
    def create_bulk(self, user_id: UUID, **data) -> list[dict[str, Any]]:
        pass
