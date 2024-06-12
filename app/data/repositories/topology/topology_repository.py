from app.data.repositories.base_repository import BaseRepository
from app.data.schemas.transactional.topology_schema import  Account, Locality, Substation, Transformer, \
    House


class AccountRepository(BaseRepository):
    model = Account
    id_field = Account.id


class LocalityRepository(BaseRepository):
    model = Locality
    id_field = Locality.id


class SubstationRepository(BaseRepository):
    model = Substation
    id_field = Substation.id


class TransformerRepository(BaseRepository):
    model = Transformer
    id_field = Transformer.id


class HouseRepository(BaseRepository):
    model = House
    id_field = House.id
