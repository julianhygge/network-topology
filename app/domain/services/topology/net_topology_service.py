from typing import Any, Dict, List, Union
from uuid import UUID

from app.data.interfaces.i_repository import IRepository
from app.data.interfaces.load.i_load_load_profile_repository import (
    ILoadProfileRepository,
)
from app.data.interfaces.load.i_predefined_templates_repository import (
    IPredefinedTemplatesRepository,
)
from app.data.interfaces.load.i_template_load_patterns_repository import (
    ITemplateConsumptionPatternsRepository,
)
from app.data.interfaces.topology.i_node_repository import INodeRepository
from app.data.schemas.enums.enums import NodeStatusEnum
from app.domain.interfaces.enums.node_type import NodeType
from app.domain.interfaces.net_topology.i_net_topology_service import (
    INetTopologyService,
)
from app.domain.services.topology.topology_service_base import (
    TopologyServiceBase,
)
from app.exceptions.hygge_exceptions import (
    InvalidDataException,
    NotFoundException,
)
from app.utils.datetime_util import utc_now_iso


class NetTopologyService(TopologyServiceBase, INetTopologyService):
    def __init__(
        self,
        substation_repo: IRepository,
        node_repo: INodeRepository,
        transformer_repo: IRepository,
        house_repo: IRepository,
        pre_master_template_repo: IRepository,
        load_profile_repository: ILoadProfileRepository,
        template_patterns_repository: ITemplateConsumptionPatternsRepository,
        pre_templates_repository: IPredefinedTemplatesRepository,
    ):
        super().__init__(substation_repo)
        self.substation_repo = substation_repo
        self.node_repo = node_repo
        self.transformer_repo = transformer_repo
        self.house_repo = house_repo
        self._pre_master_template_repo = pre_master_template_repo
        self._load_profile_repo = load_profile_repository
        self._template_patterns_repo = template_patterns_repository
        self._pre_templates_repo = pre_templates_repository

    INITIALS = {NodeType.TRANSFORMER.value: "T", NodeType.HOUSE.value: "H"}

    def get_topology_by_substation_id(
        self, substation_id: UUID
    ) -> Dict[str, Any]:
        """
        Get the topology for a given substation ID.

        :param substation_id: UUID of the substation
        :return: Dictionary containing the topology information
        :raises NotFoundException: If the substation is not found
        """
        substation = self.substation_repo.read(substation_id)
        if not substation:
            raise NotFoundException(
                f"Substation with id {substation_id} not found"
            )

        root_node = self.node_repo.read(substation_id)

        return {
            "substation_id": str(substation.id),
            "substation_name": substation.name,
            "locality_id": str(substation.locality.id),
            "locality_name": substation.locality.name,
            "nodes": self._get_node_details(root_node),
        }

    def _get_node_details(
        self, node
    ) -> Union[Dict[str, Any], List[Dict[str, Any]]]:
        """Get details of a node and its children."""
        children = self.node_repo.get_children(node.id)

        if node.node_type == NodeType.SUBSTATION.value:
            return [self._get_node_details(child) for child in children]

        node_details = self._get_basic_node_details(node)

        if node.node_type == NodeType.TRANSFORMER.value:
            node_details.update(self._get_transformer_details(node.id))
        elif node.node_type == NodeType.HOUSE.value:
            node_details.update(self._get_house_details(node.id))

        if node.node_type != NodeType.HOUSE.value:
            node_details["children"] = [
                self._get_node_details(child) for child in children
            ]

        return node_details

    @staticmethod
    def _get_basic_node_details(node) -> Dict[str, Any]:
        """Get basic details of a node."""
        details = {
            "id": str(node.id),
            "type": node.node_type,
            "name": node.name,
            "nomenclature": node.nomenclature,
        }

        return details

    def _get_transformer_details(
        self, node_id: UUID
    ) -> Dict[str, NodeStatusEnum]:
        """Get transformer-specific details."""
        transformer = self.transformer_repo.read(node_id)
        return {"status": self._get_transformer_status(transformer)}

    def _get_house_details(self, node_id: UUID) -> Dict[str, NodeStatusEnum]:
        """Get house-specific details."""
        house = self.house_repo.read(node_id)
        return {"status": self._get_house_status(house)}

    def update_topology(
        self, user_id: UUID, substation_id: UUID, data: Dict[str, Any]
    ):
        """
        Update the topology for a given substation.

        :param user_id: UUID of the user making the update
        :param substation_id: UUID of the substation
        :param data: Dictionary containing the topology update data
        :raises NotFoundException: If the substation is not found
        :raises InvalidDataException: If the input data is invalid
        """
        substation = self.substation_repo.read(substation_id)
        if not substation:
            raise NotFoundException(
                f"Substation with id {substation_id} not found"
            )

        if "nodes" not in data or not isinstance(data["nodes"], list):
            raise InvalidDataException("Invalid topology update data")

        root_node = self.node_repo.read(substation_id)
        self._update_node_topology(
            user_id, substation_id, root_node, data["nodes"]
        )

    def _update_node_topology(
        self,
        user_id: UUID,
        substation_id: UUID,
        parent_node,
        nodes_data: List[Dict[str, Any]],
    ):
        """Recursively update the node topology."""
        for node_data in nodes_data:
            action = node_data.pop("action")
            node_type = node_data.pop("type")
            node_id = node_data.pop("id")
            name = node_data.get("name")

            if action == "add":
                node_id = self._add_new_node(
                    user_id, substation_id, parent_node, node_type
                )
            elif action == "delete":
                self._delete_node(node_id)
                continue
            elif action == "update" and name is not None:
                self.node_repo.update(node_id, name=name)

            if (
                node_id
                and "children" in node_data
                and node_data["children"] is not None
            ):
                child_node = self.node_repo.read(node_id)
                self._update_node_topology(
                    user_id, substation_id, child_node, node_data["children"]
                )

    def _add_new_node(
        self, user_id: UUID, substation_id: UUID, parent_node, node_type: str
    ):
        """Add a new node to the topology."""
        try:
            nomenclature = self._generate_node_name(parent_node, node_type)

            new_node_data = self._prepare_new_node_data(
                user_id, substation_id, parent_node, node_type, nomenclature
            )

            new_node = self.node_repo.create(new_node_data)

            self._save_new_node(substation_id, new_node.id, node_type)

            return new_node
        except Exception as e:
            print(f"Error adding the new node: {e}")
            raise

    def _get_children_count(self, parent_node):
        children = self.node_repo.get_children(parent_node)
        return len(children)

    def _generate_node_name(self, parent, node_type: str) -> str:
        children = self.node_repo.get_children(parent)
        node_number = 0
        names = [x.nomenclature for x in children if x.node_type == node_type]
        if names:
            names.sort()
            last_node = names[-1]
            nodes = last_node.split(".")
            node_number = int(nodes[-1])

        name_parent = parent.nomenclature.replace(" ", "")
        initial = self.INITIALS.get(node_type, "N")
        words = name_parent.split("-")
        return f"{initial}-{words[1]}.{node_number + 1}"

    @staticmethod
    def _prepare_new_node_data(
        user_id: UUID,
        substation_id: UUID,
        parent_node,
        node_type: str,
        nomenclature: str,
    ) -> dict:
        return {
            "parent": parent_node.id,
            "node_type": node_type,
            "created_by": user_id,
            "modified_by": user_id,
            "substation_id": substation_id,
            "name": nomenclature,
            "nomenclature": nomenclature,
        }

    def _save_new_node(
        self, substation_id: UUID, new_node_id: UUID, node_type: str
    ):
        """Save the new node in the appropriate repository."""
        new_data = {
            "substation_id": substation_id,
            "node": new_node_id,
            "id": new_node_id,
        }

        if node_type == NodeType.TRANSFORMER.value:
            self.transformer_repo.create(new_data)
        elif node_type == NodeType.HOUSE.value:
            self.house_repo.create(new_data)

    def _delete_node(self, node_id: UUID):
        """Delete a node from the topology."""
        self.node_repo.delete(node_id)

    def update_transformer(
        self, user_id, transformer_id: UUID, data: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        Update a transformer's details.

        :param user_id: user performing the update
        :param transformer_id: UUID of the transformer
        :param data: Dictionary containing the update data
        :return: Updated transformer details
        :raises NotFoundException: If the transformer is not found
        """
        transformer = self.transformer_repo.read(transformer_id)
        if not transformer:
            raise NotFoundException(
                f"Transformer with id {transformer_id} not found"
            )

        data["modified_on"] = utc_now_iso()
        data["modified_by"] = user_id
        self.transformer_repo.update(transformer_id, data)

        # self.node_repo.update(transformer_id, name=data["name"])
        updated_transformer = self.transformer_repo.read(transformer_id)
        status = self._get_transformer_status(updated_transformer)
        updated_dict = self.transformer_repo.to_dicts(updated_transformer)
        updated_dict["status"] = status
        return updated_dict

    def update_house(
        self, user_id, house_id: UUID, data: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        Update a house's details.

        :param user_id: user performing the update
        :param house_id: UUID of the house
        :param data: Dictionary containing the update data
        :return: Updated house details
        :raises NotFoundException: If the house is not found
        """
        house = self.house_repo.read(house_id)
        if not house:
            raise NotFoundException(f"House with id {house_id} not found")

        data["modified_on"] = utc_now_iso()
        data["modified_by"] = user_id
        self.house_repo.update(house_id, **data)
        updated_house = self.house_repo.read(house_id)
        # self.node_repo.update(house_id, name=data["name"])
        status = self._get_house_status(updated_house)
        updated_dict = self.house_repo.to_dicts(updated_house)
        updated_dict["status"] = status

        return updated_dict

    def _collect_house_nodes(self, node, houses: List[Dict[str, Any]]):
        """Recursively collect house nodes from the topology."""
        if node.node_type == NodeType.HOUSE.value:
            house_details = self._get_basic_node_details(node)
            house_details.update(self._get_house_details(node.id))
            houses.append(house_details)

        children = self.node_repo.get_children(node.id)
        for child in children:
            self._collect_house_nodes(child, houses)

    def get_houses_by_substation_id(
        self, substation_id: UUID
    ) -> List[Dict[str, Any]]:
        """
        Get houses for a given substation ID.

        :param substation_id: UUID of the substation (grid/topology ID)
        :return: List of dictionaries containing house information
        :raises NotFoundException: If the substation is not found
        """
        substation = self.substation_repo.read(substation_id)
        if not substation:
            raise NotFoundException(
                f"Substation with id {substation_id} not found"
            )

        root_node = self.node_repo.read(substation_id)
        houses = []
        self._collect_house_nodes(root_node, houses)
        for house in houses:
            house_load = self._get_loads_by_house_id(house["id"])

        return houses

    def _get_loads_by_house_id(self, house_id: UUID) -> List[Dict[str, Any]]:
        """
        Get loads intervals for a given house ID.

        :param house_id: UUID of the house
        :return: List of dictionaries containing timestamp and load information
        :raises NotFoundException: If the house is not found
        """

        house = self.house_repo.read(house_id)
        if not house:
            raise NotFoundException(f"House with id {house_id} not found")

        load_profile = self._load_profile_repo.get_by_house_id(house_id)

        if not load_profile:
            raise NotFoundException(
                f"Load profile for house {house_id} not found"
            )

        pre_template = self._pre_templates_repo.filter(
            profile_id=load_profile.id
        )
        load_patterns = (
            self._template_patterns_repo.get_patterns_by_template_id(
                pre_template[0].template_id_id
            )
        )

        if load_patterns is None:
            return []

        load_patterns.sort(key=lambda x: x.get("timestamp") or "")

        processed_loads = []
        for item in load_patterns:
            processed_loads.append(
                {
                    "timestamp": item.get("timestamp"),
                    "consumption_kwh": item.get("consumption_kwh"),
                }
            )
        return processed_loads

    def _get_solar_by_house_id(self, house_id: UUID) -> List[Dict[str, Any]]:
        """
        Get solar generation intervals for a given house ID.

        :param house_id: UUID of the house
        :return: List of dictionaries with timestamp and solar generation
        :raises NotFoundException: If the house is not found
        """

        house = self.house_repo.read(house_id)
        if not house:
            raise NotFoundException(f"House with id {house_id} not found")
        # here I need to select  the solar profile any solar for now
        solar_profile = self._solar_profile_repo.get_by_house_id(house_id)

        if not solar_profile:
            raise NotFoundException(
                f"Solar profile for house {house_id} not found"
            )

        return [
            {
                "timestamp": item.get("timestamp"),
                "generation_kwh": item.get("generation_kwh"),
            }
            for item in solar_profile
        ]
