from typing import List

from pydantic import BaseModel

from app.api.v1.models.requests.transformer_requests import HouseResponseModel


class HouseResponseModelList(BaseModel):
    items: List[HouseResponseModel]
