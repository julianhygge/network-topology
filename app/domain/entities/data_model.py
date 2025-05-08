from typing import TypeVar

from app.data.schemas.schema_base import BaseModel as PeeweeModelClass

# Type variable for Peewee model, subclass of our BaseModel
T = TypeVar("T", bound=PeeweeModelClass)
