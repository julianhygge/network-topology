from typing import List, Optional
from uuid import UUID

from peewee import DoesNotExist, IntegrityError, fn

from app.data.interfaces.topology.i_house_repository import IHouseRepository
from app.data.interfaces.topology.i_node_repository import INodeRepository
from app.data.interfaces.topology.i_transformer_repository import ITransformerRepository
from app.data.repositories.base_repository import BaseRepository
from app.data.schemas.transactional.topology_schema import (
    Account,
    House,
    Locality,
    Node,
    Substation,
    Transformer,
)
from app.utils.logger import logger


class AccountRepository(BaseRepository):
    model = Account
    id_field = Account.id


class LocalityRepository(BaseRepository):
    model = Locality
    id_field = Locality.id


class SubstationRepository(BaseRepository):
    model = Substation
    id_field = Substation.id

    def create(self, **query) -> Substation:
        try:
            with self.database_instance.atomic():
                obj = self.model.create(**query)
                query["id"] = obj.id
                query["node_type"] = "substation"
                query["substation_id"] = obj.id
                Node.create(**query)
                return obj
        except IntegrityError as e:
            logger.exception(e)
            raise


class TransformerRepository(BaseRepository, ITransformerRepository):
    model = Transformer
    id_field = Transformer.id

    def get_transformers_by_substation_id(self, substation_id: UUID):
        transformers = Transformer.select().where(
            Transformer.substation == substation_id
        )
        return transformers


class HouseRepository(BaseRepository, IHouseRepository):
    model = House
    id_field = House.id

    def get_houses_by_substation_id(self, substation_id: UUID):
        houses = (
            House.select()
            .join(Transformer)
            .where(Transformer.substation == substation_id)
        )
        return houses


class NodeRepository(BaseRepository, INodeRepository):
    model = Node
    id_field = Node.id

    def read(self, id_value: UUID) -> Optional[Node]:
        try:
            return Node.get(Node.id == id_value)
        except DoesNotExist:
            return None

    def get_children(self, parent_id: UUID) -> List[Node]:
        return list(
            Node.select()
            .where(Node.parent == parent_id)
            .order_by(Node.created_on, fn.COALESCE(Node.nomenclature, ""))
        )

    def get_parent(self, node_id: UUID) -> Optional[Node]:
        node = self.read(node_id)
        if node and node.parent:
            try:
                return Node.get(Node.id == node.parent.id)
            except DoesNotExist:
                return None
        return None

    def get_substation(self, node_id: UUID) -> Optional[Node]:
        node = self.read(node_id)
        if node and node.substation:
            try:
                return Substation.get(Substation.id == node.substation.id)
            except DoesNotExist:
                return None
        return None

    def get_locality(self, node_id: UUID) -> Optional[Locality]:
        substation = self.get_substation(node_id)
        if substation and substation.locality:
            try:
                return Locality.get(Locality.id == substation.locality.id)
            except DoesNotExist:
                return None
        return None
