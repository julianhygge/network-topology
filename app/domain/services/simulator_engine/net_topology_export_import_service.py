import json
import uuid

from app.data.interfaces.i_repository import IRepository
from app.data.interfaces.load.i_predefined_templates_repository import IPredefinedTemplatesRepository
from app.data.schemas.transactional.topology_schema import House


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


    def build_house_structure(self, node):

        solar_property = self.get_solar_profile(node)
        load_profile = self.get_load_profile(node)
        house_property = self.get_house_property(node)

        return {
            "house_id": node['id'],
            "house_name": node['name'],
            "solar_profile": solar_property,
            "load_profile": load_profile,
            "house_property": house_property
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
                    # Direct children of substation are "Transformer-1", "Transformer-2", etc.
                    key = f"Transformer-{transformer_counter}"
                else:
                    # All nested transformers are "Sub-Transformer-1", "Sub-Transformer-2", etc.
                    key = f"Sub-Transformer-{transformer_counter}"

                transformer_counter += 1

                transformer_property = self.get_transformer_property(nodes)

                transformer_structure = {
                    "transformer_id": nodes['id'],
                    "transformer_name": nodes['name'],
                    "transformer_property": transformer_property

                }

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

    def get_house_property(self, node):
        data = self._house_repo.read_or_none(node["id"])
        data_dict = self._house_repo.to_dicts(data)
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




    async def import_json_file(self, user_id, substation_id, file):
        try:
            content = await file.read()
            json_data = json.loads(content.decode('utf-8'))

            grid_data = json_data.get("Grid", {})

            if "Grid" not in json_data:
                raise ValueError("Invalid JSON structure")

            new_node = self._process_substation_import(user_id, substation_id)


            self._process_transformer(user_id, new_node, grid_data, substation_id)
        except Exception as e:
            raise ValueError(f"Invalid JSON format: {str(e)}")

    def _process_substation_import(self, user_id, substation_id):

        # Create new substation and node

        substation_data = {
            "id": substation_id,
            "locality_id": "94522a0a-c8f1-40f8-a2e5-9aed2dc55555",
            "name": "Grid-4",
            "created_by": user_id,
            "modified_by": user_id,
            "nomenclature": "Grid-4"
        }
        new_node = self._substation_repo.create(substation_data)


        return new_node



    def _process_transformer(self, user_id, parent_id, grid_data, substation_id):

        for key, value in grid_data.items():
            if key.startswith("Transformer"):
                self._create_transformer_and_children(user_id, value, parent_id, substation_id)


    def _create_transformer_and_children(self, user_id, transformer_data, parent_id, substation_id):

        new_transformer_id = str(uuid.uuid4())

        node_transformer_data = {
            "id": new_transformer_id,
            "parent_id": parent_id,
            "node_type": "transformer",
            "created_by": user_id,
            "modified_by": user_id,
            "name": transformer_data.get("transformer_name", "T-1.1"),
            "substation_id": substation_id,
            "nomenclature": transformer_data.get("transformer_name", "T-1.1")
        }
        self._node_repo.create(node_transformer_data)

        self._create_transformer_property(transformer_data, new_transformer_id)

        self._process_transformer_children(user_id, transformer_data, new_transformer_id, substation_id)



    def _create_transformer_property(self, transformer_data, transformer_id):

        transformer_property = transformer_data.get("transformer_property", {})
        if transformer_property:

            transformer_property_data = {
                "id": transformer_id,
                "node": transformer_id,
                "max_capacity_kw": transformer_property.get("max_capacity_kw", None),
                "allow_export": transformer_property.get("allow_export", False),
                "backward_efficiency": transformer_property.get("backward_efficiency", None),
                "primary_ampacity": transformer_property.get("primary_ampacity", None),
                "secondary_ampacity": transformer_property.get("secondary_ampacity", None),
                "years_of_service": transformer_property.get("years_of_service", None),
                "forward_efficiency": transformer_property.get("forward_efficiency", None),
                "digital_twin_model": transformer_property.get("digital_twin_model", False),
            }

            self._transformer_repo.create(transformer_property_data)

    def _process_transformer_children(self, user_id, transformer_data, parent_id, substation_id):

        for key, value in transformer_data.items():
            if key.startswith("House"):
                self._create_house(user_id, value, parent_id, substation_id)
            elif key.startswith("Sub-Transformer"):
                self._create_transformer_and_children(user_id, value, parent_id, substation_id)


    def _create_house(self, user_id, house_data, parent_id, substation_id):
        new_house_id = str(uuid.uuid4())
        house_node_data = {
            "id": new_house_id,
            "parent_id": parent_id,
            "node_type": "house",
            "created_by": user_id,
            "modified_by": user_id,
            "name": house_data.get("house_name", "H-1.1"),
            "substation_id": substation_id,
            "nomenclature": house_data.get("house_name", "H-1.1")
        }

        self._node_repo.create(house_node_data)

        self._create_house_properties(user_id, house_data, new_house_id)


    def _create_house_properties(self, user_id, house_data, new_house_id):

        solar_profile = house_data.get("solar_profile", {})
        load_profile = house_data.get("load_profile", {})
        house_property = house_data.get("house_property", {})

        if solar_profile:
            solar_profile_data = {
                "id": new_house_id,
                "created_by": user_id,
                "modified_by": user_id,
                "solar_available": solar_profile.get("solar_available", False),
                "house_id": new_house_id,
                "installed_capacity_kw": solar_profile.get("installed_capacity_kw", None),
                "tilt_type": solar_profile.get("tilt_type", "fixed"),
                "years_since_installation": solar_profile.get("years_since_installation", None),
                "simulate_using_different_capacity": solar_profile.get("simulate_using_different_capacity", False),
                "capacity_for_simulation_kw": solar_profile.get("capacity_for_simulation_kw", None),
                "available_space_sqft": solar_profile.get("available_space_sqft", None),
                "simulated_available_space_sqft": solar_profile.get("simulated_available_space_sqft", None)
            }

            self._solar_profile_repo.create(solar_profile_data)

        if house_property:
            house_property_data = {
                "id": new_house_id,
                "load_profile": house_property.get("load_profile", None),
                "has_solar": house_property.get("has_solar", False),
                "solar_kw": house_property.get("solar_kw", None),
                "house_type": house_property.get("house_type", None),
                "connection_kw": house_property.get("connection_kw", None),
                "has_battery": house_property.get("has_battery", False),
                "battery_type": house_property.get("battery_type", None),
                "voluntary_storage": house_property.get("voluntary_storage", None),
                "battery_peak_charging_rate": house_property.get("battery_peak_charging_rate", None),
                "battery_peak_discharging_rate": house_property.get("battery_peak_discharging_rate", None),
                "battery_total_kwh": house_property.get("battery_total_kwh", None),
                "node_id": new_house_id
            }

            self._house_repo.create(house_property_data)

        if load_profile:
            load_profile_data = {
                "created_by": user_id,
                "modified_by": user_id,
                "user_id": user_id,
                "source": "Template",
                "profile_name": "Template",
                "house_id": new_house_id
            }

            new_load_profile_id = self._load_profile_repo.create(load_profile_data)

            load_predefined_data = {
                "profile_id": new_load_profile_id,
                "template_id": load_profile.get("template_id", 1)
            }

            self._pre_template_repo.create(load_predefined_data)







