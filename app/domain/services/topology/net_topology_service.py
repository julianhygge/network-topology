from typing import Dict, Any
from app.data.interfaces.irepository import IRepository
from app.data.interfaces.topology.inode_repository import INodeRepository
from app.domain.interfaces.net_topology.inet_topology_service import INetTopologyService
from app.domain.services.topology.topology_service_base import TopologyServiceBase
from app.exceptions.hygge_exceptions import NotFoundException


class NetTopologyService(TopologyServiceBase, INetTopologyService):
    def __init__(self,
                 substation_repo: IRepository,
                 node_repo: INodeRepository,
                 transformer_repo: IRepository,
                 house_repo: IRepository):
        super().__init__(substation_repo)
        self.substation_repo = substation_repo
        self.node_repo = node_repo
        self.transformer_repo = transformer_repo
        self.house_repo = house_repo

    def get_topology_by_substation_id(self, substation_id: str) -> Dict[str, Any]:
        substation = self.substation_repo.read(substation_id)
        if not substation:
            return {}

        locality_id = substation.locality.id
        root_node = self.node_repo.read(substation_id)

        return {
            "substation_id": str(substation.id),
            "substation_name": substation.name,
            "locality_id": str(locality_id),
            "locality_name": substation.locality.name,
            "nodes": self._get_node_details(root_node)
        }

    def _get_node_details(self, node):
        children = self.node_repo.get_children(node.id)
        if node.node_type == 'substation':
            node_details = {"children": []}
            for child in children:
                node_details["children"].append(self._get_node_details(child))
            return node_details["children"]
        node_details = {
            "id": str(node.id),
            "type": node.node_type
        }

        if node.name is not None:
            node_details.update({
                "name": node.name
            })

        if node.node_type == 'transformer':
            transformer = self.transformer_repo.read(node.id)
            node_details.update({
                "is_complete": self._is_transformer_complete(transformer)
            })
        elif node.node_type == 'house':
            house = self.house_repo.read(node.id)
            node_details.update({
                "is_complete": self._is_house_complete(house)
            })
        if node.node_type != 'house':
            node_details.update({
                "children": []
            })
        for child in children:
            node_details["children"].append(self._get_node_details(child))

        return node_details

    def update_topology(self, user_id, substation_id, data):
        substation = self.substation_repo.read(substation_id)
        if not substation:
            raise NotFoundException(f"Substation with id {substation_id} not found")

        root_node = self.node_repo.read(substation_id)
        self._update_node_topology(user_id, substation_id, root_node, data['nodes'])

    def _update_node_topology(self, user_id, substation_id, parent_node, nodes_data):
        for node_data in nodes_data:
            action = node_data.pop('action', None)
            node_type = node_data.pop('type')
            node_id = node_data.pop('id', None)
            if action == 'add':
                new_node_data = {
                    "parent": parent_node.id,
                    "node_type": node_type,
                    "created_by": user_id,
                    "modified_by": user_id,
                    "substation_id": substation_id

                }
                new_node = self.node_repo.create(**new_node_data)
                new_data = {
                    "substation_id": substation_id,
                    "node": new_node.id,
                    "id": new_node.id
                }
                node_id = new_node.id
                if node_type == 'transformer':
                    self.transformer_repo.create(**new_data)
                elif node_type == 'house':
                    self.house_repo.create(**new_data)
            elif action == 'delete':
                self.node_repo.delete(node_id)
                continue

            if 'children' in node_data and node_data['children'] is not None:
                self._update_node_topology(user_id, substation_id, self.node_repo.read(node_id), node_data['children'])

    def update_transformer(self, transformer_id, data):
        transformer = self.transformer_repo.read(transformer_id)
        if not transformer:
            raise NotFoundException(f"Transformer with id {transformer_id} not found")

        self.transformer_repo.update(transformer_id, **data)

        updated_transformer = self.transformer_repo.read(transformer_id)
        is_complete = self._is_transformer_complete(updated_transformer)
        updated_dicts = self.transformer_repo.to_dicts(updated_transformer)
        updated_dicts["is_complete"] = is_complete
        return updated_dicts

    def update_house(self, house_id, data):
        house = self.house_repo.read(house_id)
        if not house:
            raise NotFoundException(f"House with id {house_id} not found")

        self.house_repo.update(house_id, **data)

        updated_house = self.house_repo.read(house_id)
        is_complete = self._is_house_complete(updated_house)
        updated_dicts = self.house_repo.to_dicts(updated_house)
        updated_dicts["is_complete"] = is_complete

        return updated_dicts
