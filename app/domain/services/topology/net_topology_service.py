from typing import Dict, Any
from app.data.interfaces.irepository import IRepository
from app.domain.interfaces.net_topology.inet_topology_service import INetTopologyService
from app.domain.services.topology.topology_service_base import TopologyServiceBase
from app.exceptions.hygge_exceptions import NotFoundException


class NetTopologyService(TopologyServiceBase, INetTopologyService):
    def __init__(self,
                 substation_repo: IRepository,
                 transformer_repo: IRepository,
                 house_repo: IRepository):
        super().__init__(substation_repo)
        self.substation_repo = substation_repo
        self.transformer_repo = transformer_repo
        self.house_repo = house_repo

    def get_topology_by_substation_id(self, substation_id: str) -> Dict[str, Any]:
        substation = self.substation_repo.read(substation_id)
        if not substation:
            return {}

        locality_id = substation.locality.id
        transformers = self.transformer_repo.model.select().where(
            self.transformer_repo.model.substation == substation_id)

        transformers_list = []
        for transformer in transformers:
            houses = self.house_repo.model.select().where(self.house_repo.model.transformer == transformer.id)
            houses_details = [
                {
                    "id": str(house.id),
                    "is_complete": self._is_house_complete(house)
                }
                for house in houses
            ]
            transformers_list.append({
                "id": str(transformer.id),
                "is_complete": self._is_transformer_complete(transformer),
                "houses_details": houses_details
            })

        return {
            "substation_id": str(substation.id),
            "substation_name": substation.name,
            "locality_id": str(locality_id),
            "locality_name": substation.locality.name,
            "transformers": transformers_list
        }

    def update_topology(self, substation_id, data):
        substation = self.substation_repo.read(substation_id)
        if not substation:
            raise NotFoundException(f"Substation with id {substation_id} not found")

        for transformer_data in data['transformers']:
            action = transformer_data.pop('action')
            if action == 'add':
                new_data = {
                    "substation_id": substation_id,
                }
                transformer = self.transformer_repo.create(**new_data)
            elif action == 'update':
                transformer_id = transformer_data.pop('id')
                transformer = self.transformer_repo.read(transformer_id)
                if not transformer:
                    raise NotFoundException(f"Transformer with id {transformer_id} not found")

            elif action == 'delete':
                transformer_id = transformer_data['id']
                self.transformer_repo.delete(transformer_id)
                continue

            houses_details = transformer_data.get('houses_details', [])
            if houses_details is None:
                continue
            for house_data in houses_details:
                house_action = house_data.pop('action')
                if house_action == 'add':
                    new_data = {
                        "transformer_id": transformer
                    }
                    self.house_repo.create(**new_data)
                elif house_action == 'update':
                    pass
                elif house_action == 'delete':
                    house_id = house_data['id']
                    self.house_repo.delete(house_id)

    def update_transformer(self, transformer_id, data):
        transformer = self.transformer_repo.read(transformer_id)
        if not transformer:
            raise NotFoundException(f"Transformer with id {transformer_id} not found")

        self.transformer_repo.update(transformer_id, **data)

        updated_transformer = self.transformer_repo.read(transformer_id)
        is_complete = self._is_transformer_complete(updated_transformer)
        updated_dicts = self.substation_repo.to_dicts(updated_transformer)
        updated_dicts["is_complete"] = is_complete
        return updated_dicts

    def update_house(self, house_id, data):
        house = self.house_repo.read(house_id)
        if not house:
            raise NotFoundException(f"House with id {house_id} not found")

        self.house_repo.update(house_id, **data)

        updated_house = self.house_repo.read(house_id)
        is_complete = self._is_house_complete(updated_house)
        updated_dicts = self.substation_repo.to_dicts(updated_house)
        updated_dicts["is_complete"] = is_complete

        return updated_dicts


