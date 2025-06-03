import json

from app.data.interfaces.i_repository import IRepository
from app.data.interfaces.load.i_predefined_templates_repository import IPredefinedTemplatesRepository


class NetTopologyExportImportService:
    def __init__(
            self,
            node_repository: IRepository,
            substation_repository: IRepository,
            transformer_repository: IRepository,
            house_repository: IRepository,
            solar_profile_repository: IRepository,
            predefined_templates_repository: IPredefinedTemplatesRepository,
            load_profiles_repository: IRepository
    ):
        self._node_repo = node_repository
        self._substation_repo = substation_repository
        self._transformer_repo = transformer_repository
        self._house_repo = house_repository
        self._solar_profile_repo = solar_profile_repository
        self._pre_template_repo = predefined_templates_repository
        self._load_profile_repo = load_profiles_repository

    def export_network_topology(self, substation_id):

        # Step-1
        # get substation detail from substation_id
        substation_data = self._substation_repo.read_or_none(substation_id)

        # Step-2
        # from node repo, get detail of transformer, sub-transformer, houses
        node_data = self._node_repo.filter(substation_id=substation_id)
        all_nodes = self._node_repo.to_dicts(node_data)

        nodes_by_parent = {}
        for node in all_nodes:
            if node['parent'] not in nodes_by_parent:
                nodes_by_parent[node['parent']] = []
            nodes_by_parent[node['parent']].append(node)

        grid_structure = {
            "Grid": {
                "grid_id": substation_data.id,
                "grid_name": substation_data.name
            }
        }

        grid_structure["Grid"].update(
            self.build_children(substation_id, nodes_by_parent, is_substation_level=True))

        json_str = json.dumps(grid_structure, indent=2, default=str)
        filename = f'network-topology-{substation_id}.json'

        return json_str, filename

        return grid_structure

    def build_house_structure(self, node):

        solar_property = self.get_solar_profile(node)
        load_profile = self.get_load_profile(node)

        return {
            "house_id": node['id'],
            "house_name": node['name'],
            "solar_profile": solar_property,
            "load_profile": load_profile
        }

    def build_children(self, parent_id, nodes_by_parent, is_substation_level=False):
        children = {}

        if parent_id not in nodes_by_parent:
            return children

        transformer_counter = 1
        house_count = 1

        for nodes in nodes_by_parent[parent_id]:

            if nodes['node_type'] == 'transformer':
                # Name transformers based on hierarchy level
                if is_substation_level:
                    # Direct children of substation are "Transformer", "Transformer-2", etc.
                    key = f"Transformer-{transformer_counter}"
                else:
                    # All nested transformers are "Sub-Transformer", "Sub-Transformer-2", etc.
                    key = f"Sub-Transformer-{transformer_counter}"

                transformer_counter += 1

                transformer_property = self.get_transformer_property(nodes)

                transformer_structure = {
                    "transformer_id": nodes['id'],
                    "transformer_name": nodes['name'],

                }
                transformer_structure.update(transformer_property)

                # Recursively add children (this handles unlimited nesting)
                child_structure = self.build_children(nodes['id'], nodes_by_parent, is_substation_level=False)
                transformer_structure.update(child_structure)

                children[key] = transformer_structure

            elif nodes['node_type'] == 'house':
                key = f"House-{house_count}"
                children[key] = self.build_house_structure(nodes)
                house_count += 1

        return children

    def get_transformer_property(self, node):
        data = self._transformer_repo.read_or_none(node['id'])
        data_dict = self._transformer_repo.to_dicts(data)
        return data_dict

    def get_load_profile(self, node):
        data = self._load_profile_repo.filter(house_id=node['id'])
        for dt in data:
            pre_data = self._pre_template_repo.get_by_profile_id(dt)
            template = self._pre_template_repo.read_or_none(pre_data)
            return self._pre_template_repo.to_dicts(template)

    def get_solar_profile(self, node):
        data = self._solar_profile_repo.read_or_none(node['id'])
        return self._solar_profile_repo.to_dicts(data)
