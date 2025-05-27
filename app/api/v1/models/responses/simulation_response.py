from pydantic import BaseModel
from uuid import UUID
from typing import List

class SimulationAlgorithmResponse(BaseModel):
    id: UUID
    algorithm_code: str
    display_name: str
    description: str

class SimulationAlgorithmListResponse(BaseModel):
    items: List[SimulationAlgorithmResponse]

class NetMeteringAlgorithmResponse(BaseModel):
    id: UUID
    policy_code: str
    display_name: str
    description: str

class NetMeteringAlgorithmListResponse(BaseModel):
    items: List[NetMeteringAlgorithmResponse]