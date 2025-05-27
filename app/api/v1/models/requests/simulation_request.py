from datetime import datetime

from pydantic import BaseModel, Field
from uuid import UUID

class SimulationRunsRequestModel(BaseModel):
    run_name: str = Field(None, example="Simulation-1")
    topology_root_node_id: UUID = Field(..., example="94522a0a-c8f1-40f8-a2e5-9aed2dc55555")
    simulation_algorithm_type_id: UUID = Field(..., example="94522a0a-c8f1-40f8-a2e5-9aed2dc55555")
    billing_cycle_month: int = Field(..., example="1")
    billing_cycle_year: int = Field(..., example="2021")
    status: str = Field(..., example="Completed")
    simulation_start_timestamp: datetime = Field(..., example="2023-02-02 00:00:00")
    simulation_end_timestamp: datetime = Field(..., example="2023-02-02 00:00:00")
