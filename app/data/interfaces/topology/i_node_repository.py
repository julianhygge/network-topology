"""Module for the node repository interface."""

from abc import abstractmethod
from typing import List, Optional
from uuid import UUID

from app.data.interfaces.i_repository import IRepository, T

# Use parentheses for long import
from app.data.schemas.transactional.topology_schema import (
    Locality,
    Node,
    Substation,
)


# T is Node for this interface
class INodeRepository(IRepository[T]):
    """
    Interface defining specific operations for NodeRepository
    beyond the generic IRepository, focusing on topology traversal.
    """

    @abstractmethod
    def get_children(self, parent_id: UUID) -> List[Node]:
        """
        Retrieves all direct children of a given parent node.

        Args:
            parent_id: The UUID of the parent node.

        Returns:
            A list of child Node instances.
        """

    @abstractmethod
    def read(self, id_value: UUID) -> Optional[Node]:
        """
        Retrieves a node by its ID. Overrides generic read if needed,
        though often covered by BaseRepository.get_by_id.

        Args:
            id_value: The UUID of the node to retrieve.

        Returns:
            A Node instance if found, otherwise None.
        """

    @abstractmethod
    def get_parent(self, node_id: UUID) -> Optional[Node]:
        """
        Retrieves the parent node of a given node.

        Args:
            node_id: The UUID of the node whose parent is to be retrieved.

        Returns:
            The parent Node instance if found, otherwise None.
        """

    @abstractmethod
    def get_substation(self, node_id: UUID) -> Optional[Substation]:
        """
        Retrieves the Substation associated with a given node.

        Args:
            node_id: The UUID of the node.

        Returns:
            The associated Substation instance if found, otherwise None.
        """

    @abstractmethod
    def get_locality(self, node_id: UUID) -> Optional[Locality]:
        """
        Retrieves the Locality associated with a given node
        (via its Substation).

        Args:
            node_id: The UUID of the node.

        Returns:
            The associated Locality instance if found, otherwise None.
        """
