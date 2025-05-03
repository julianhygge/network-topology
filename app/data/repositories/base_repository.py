from typing import Any, Dict, List, Union

from peewee import ModelSelect

from app.data.interfaces.i_repository import IRepository, T
from app.data.schemas.hygge_database import HyggeDatabase


class BaseRepository(IRepository[T]):
    model = None
    id_field = None

    @property
    def database_instance(self):
        return HyggeDatabase.get_instance()

    def create(self, **query) -> T:
        obj = self.model.create(**query)
        return obj

    def read(self, id_value) -> T:
        obj = self.model.get_or_none(self.id_field == id_value)
        return obj

    def update(self, id_value, **query) -> int:
        return self.model.update(**query).where(self.id_field == id_value).execute()

    def delete(self, id_value) -> int:
        return self.model.delete().where(self.id_field == id_value).execute()

    def list(self) -> List[T]:
        return list(self.model.select())

    def list_actives(self) -> List[T]:
        return list(self.model.select().where(self.model.active))

    def upsert(self, conflict_target: List[str], defaults: Dict[str, any], **query) -> T:
        query.update(defaults)
        return self.model.insert(**query).on_conflict(
            conflict_target=conflict_target,
            update=defaults
        ).execute()

    def upsert_and_retrieve(self, conflict_target: List[str], defaults: Dict[str, any], **query) -> T:
        self.upsert(conflict_target=conflict_target, defaults=defaults, **query)

        retrieval_query = self.model.select()
        for field in conflict_target:
            if field in query:
                retrieval_query = retrieval_query.where(getattr(self.model, field) == query[field])
            elif field in defaults:
                retrieval_query = retrieval_query.where(getattr(self.model, field) == defaults[field])

        result = retrieval_query.first()
        return result

    def list_public(self) -> List[T]:
        return list(self.model.select().where(self.model.public & self.model.active))

    def list_no_public_by_user_id(self, user_id) -> List[T]:
        return list(self.model.select().where((self.model.created_by == user_id) &
                                              self.model.active &
                                              (~self.model.public)))

    def to_dicts(self, obj) -> Union[Dict[str, Any], List[Dict[str, Any]], Any]:
        if isinstance(obj, ModelSelect):
            return [self.to_dicts(item) for item in obj]
        elif hasattr(obj, '__data__'):
            return {key: self.to_dicts(value) for key, value in obj.__data__.items()}
        elif isinstance(obj, list):
            return [self.to_dicts(item) for item in obj]
        elif hasattr(obj, '__dict__'):
            return {key: self.to_dicts(value) for key, value in obj.__dict__.items() if not key.startswith('_')}
        else:
            return obj

    def list_by_user_id(self, user_id) -> List[T]:
        return list(self.model.select().where((self.model.created_by == user_id) &
                                              self.model.active))
