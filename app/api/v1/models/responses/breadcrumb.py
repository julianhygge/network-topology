from pydantic import BaseModel, UUID4, Field
from typing import List


class BreadcrumbItem(BaseModel):
    id: UUID4 = Field(..., example="74f5596d-1df2-45ff-834c-a0511674c57f")
    name: str = Field(..., example="Locality")
    nomenclature: str = Field(..., example="T.1.1")


class BreadcrumbResponseModel(BaseModel):
    locality: str = Field(..., example="Shantipuram")
    substation_id: UUID4 = Field(..., example="74f5596d-1df2-45ff-834c-a0511674c57f")
    substation_name: str = Field(..., example="Substation1")
    substation_nomenclature: str = Field(..., example="S.1.9")
    path: List[BreadcrumbItem]
