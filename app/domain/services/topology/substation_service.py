from typing import Any
from uuid import UUID

from app.data.interfaces.i_repository import IRepository
from app.domain.interfaces.net_topology.i_substation_service import ISubstationService
from app.domain.services.base_service import BaseService


class SubstationService(BaseService, ISubstationService):
    def __init__(self, repository: IRepository):
        super().__init__(repository)

    def create_bulk(self, user_id: UUID, **data) -> list[dict[str, Any]]:
        current_substations = self.repository.list_by_user_id(user_id)
        last_substation_number = 0
        if any(current_substations):
            current_substations.sort(key=lambda x: x.name, reverse=True)
            last_substation = current_substations[0]
            last_name = last_substation.name
            words = last_name.split(" ")
            last_substation_number = int(words[2])

        substations_to_create = int(data.pop("number_of_substations"))
        locality_id = data.pop("locality_id")
        name = "Grid - "
        for n in range(substations_to_create):
            with self.repository.database_instance.atomic():
                new_index = last_substation_number + n + 1
                new_substation = {
                    "locality_id": locality_id,
                    "name": name + str(new_index),
                    "nomenclature": name + str(new_index),
                    "created_by": user_id,
                    "modified_by": user_id,
                }
                self.repository.create(new_substation)

        substations = self.list_all()
        substations.sort(key=lambda x: x["created_on"])
        return substations
