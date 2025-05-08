# pyright: reportUnknownMemberType=false
# pyright: reportUnknownVariableType=false
# pyright: reportUnknownArgumentType=false

"""Module for various topology related repositories."""
from typing import Any, Dict, List, Optional, Union, cast
from uuid import UUID

from peewee import DoesNotExist, IntegrityError, fn

from app.data.interfaces.topology.i_node_repository import INodeRepository
from app.data.repositories.base_repository import BaseRepository
from app.data.schemas.transactional.topology_schema import (
    House,
    HouseFlag,
    Locality,
    Node,
    Substation,
    Transformer,
)
from app.utils.logger import logger


class FlagRepository(BaseRepository[HouseFlag]):
    """"""


class LocalityRepository(BaseRepository[Locality]):
    """
    Repository for managing Locality data.
    This class extends `BaseRepository` to provide generic CRUD operations
    for the `Locality` model.
    """


class SubstationRepository(BaseRepository[Substation]):
    """
    Repository for managing Substation data.
    Extends BaseRepository and includes logic to create a corresponding Node.
    """

    def create(self, data: Dict[str, Any]) -> Substation:
        """
        Creates a new Substation and a corresponding Node entry.

        Args:
            data: Dictionary containing data for the new substation.
                  This data is also used for Node creation.

        Returns:
            The created Substation instance.

        Raises:
            IntegrityError: If a database integrity constraint is violated.
        """
        try:
            with self.database_instance.atomic():
                obj = self.model.create(**data)
                data["id"] = obj.id
                data["node_type"] = "substation"
                data["substation_id"] = obj.id
                Node.create(**data)
                return obj
        except IntegrityError as e:
            logger.exception(
                "Integrity error during substation creation: %s", e
            )
            raise


class TransformerRepository(BaseRepository[Transformer]):
    """
    Repository for managing Transformer data.
    Extends BaseRepository for generic CRUD operations.
    """


class HouseRepository(BaseRepository[House]):
    """
    Repository for managing House data.
    Extends BaseRepository for generic CRUD operations.
    """


class NodeRepository(BaseRepository[Node], INodeRepository[Node]):
    """
    Repository for managing Node data and topology traversal.
    Extends BaseRepository for Node CRUD and implements INodeRepository.
    """

    def read(self, id_value: Union[int, UUID]) -> Optional[Node]:
        """
        Retrieves a node by its ID.

        Args:
            id_value: The ID (int or UUID) of the node to retrieve.

        Returns:
            A Node instance if found, otherwise None.
        """
        try:
            return Node.get(Node.id == id_value)
        except DoesNotExist:
            return None

    def get_children(self, parent_id: UUID) -> List[Node]:
        """
        Retrieves all direct children of a given parent node.

        Args:
            parent_id: The UUID of the parent node.

        Returns:
            A list of child Node instances, ordered by creation date and name.
        """
        return list(
            Node.select()
            .where(Node.parent == parent_id)
            .order_by(Node.created_on, fn.COALESCE(Node.nomenclature, ""))
        )

    def get_parent(self, node_id: UUID) -> Optional[Node]:
        """
        Retrieves the parent node of a given node.

        Args:
            node_id: The UUID of the node whose parent is to be retrieved.

        Returns:
            The parent Node instance if found, otherwise None.
        """
        node = self.read(node_id)
        if node and node.parent:
            try:
                return Node.get(Node.id == node.parent.id)
            except DoesNotExist:
                return None
        return None

    def get_substation(self, node_id: UUID) -> Optional[Substation]:
        """
        Retrieves the Substation associated with a given node.

        Args:
            node_id: The UUID of the node.

        Returns:
            The associated Substation instance if found, otherwise None.
        """
        node = self.read(node_id)
        if node and node.substation:
            try:
                return Substation.get(Substation.id == node.substation.id)
            except DoesNotExist:
                return None
        return None

    def get_locality(self, node_id: UUID) -> Optional[Locality]:
        """
        Retrieves the Locality associated with
        a given node (via its Substation).

        Args:
            node_id: The UUID of the node.

        Returns:
            The associated Locality instance if found, otherwise None.
        """
        substation = self.get_substation(node_id)
        if substation and substation.locality:
            try:
                query = Locality.id == substation.locality.id
                local = Locality.get(query)
                return cast(Locality, local)
            except DoesNotExist:
                return None
        return None
