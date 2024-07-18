from pydantic import BaseModel, UUID4
from typing import List

class BreadcrumbItem(BaseModel):
    id: UUID4
    name: str
    nomenclature: str

class BreadcrumbResponseModel(BaseModel):
    locality: str
    substation_id: UUID4
    substation_name: str
    substation_nomenclature: str
    path: List[BreadcrumbItem]
