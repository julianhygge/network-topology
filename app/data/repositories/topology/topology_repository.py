from uuid import UUID

from app.data.interfaces.topology.ihouse_repository import IHouseRepository
from app.data.interfaces.topology.itransformer_repository import ITransformerRepository
from app.data.repositories.base_repository import BaseRepository
from app.data.schemas.transactional.topology_schema import Account, Locality, Substation, Transformer, \
    House, Node


class AccountRepository(BaseRepository):
    model = Account
    id_field = Account.id


class LocalityRepository(BaseRepository):
    model = Locality
    id_field = Locality.id


class SubstationRepository(BaseRepository):
    model = Substation
    id_field = Substation.id


class TransformerRepository(BaseRepository, ITransformerRepository):
    model = Transformer
    id_field = Transformer.id

    def get_transformers_by_substation_id(self, substation_id: UUID):
        transformers = Transformer.select().where(Transformer.substation == substation_id)
        return transformers


class HouseRepository(BaseRepository, IHouseRepository):
    model = House
    id_field = House.id

    def get_houses_by_substation_id(self, substation_id: UUID):
        houses = (House
                  .select()
                  .join(Transformer)
                  .where(Transformer.substation == substation_id))
        return houses


class NodeRepository(BaseRepository):
    model = Node
    id_field = Node.id
