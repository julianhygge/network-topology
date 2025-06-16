from datetime import datetime, time
from typing import Any, Dict, List, Optional
from uuid import UUID

from pydantic import BaseModel


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


class NetMeteringPolicyResponse(BaseModel):
    simulation_run_id: UUID
    retail_price_per_kwh: float
    fixed_charge_tariff_rate_per_kw: Optional[float]


class GrossMeteringPolicyResponse(BaseModel):
    simulation_run_id: UUID
    import_retail_price_per_kwh: float
    export_wholesale_price_per_kwh: float
    fixed_charge_tariff_rate_per_kw: Optional[float]


class TimeOfUseResponse(BaseModel):
    id: UUID
    simulation_run_id: UUID
    time_period_label: Optional[str]
    start_time: time
    end_time: time
    import_retail_rate_per_kwh: float
    export_wholesale_rate_per_kwh: float


class SimulationRunsResponse(BaseModel):
    id: UUID
    run_name: Optional[str]
    topology_root_node_id: Optional[UUID]
    simulation_algorithm_type_id: UUID
    billing_cycle_month: Optional[int]
    billing_cycle_year: Optional[int]
    status: str
    simulation_start_timestamp: Optional[datetime]
    simulation_end_timestamp: Optional[datetime]
    locality_id: Optional[UUID]
    run_sequence_identifier: str
    simulation_container_id: UUID
    description: Optional[str]
    created_on: datetime


class SimulationSelectedResponse(BaseModel):
    simulation_run_id: UUID
    net_metering_policy_type_id: UUID
    fac_charge_per_kwh_imported: Optional[float]
    tax_rate_on_energy_charges: Optional[float]


class HouseBillResponse(BaseModel):
    id: UUID
    simulation_run_id: UUID
    house_node_id: UUID
    total_energy_imported_kwh: float
    total_energy_exported_kwh: float
    net_energy_balance_kwh: float
    calculated_bill_amount: float
    bill_details: Dict[str, Any]

class SimulationContainerResponse(BaseModel):
    id: UUID
    name: str
    description: str
    location_name: str
    time_step_min: int
    algorithm_name: str
    power_unit: str
    created_on: datetime
    modified_on: datetime


class SimulationContainerStatusResponse(BaseModel):
    id: UUID
    name: str
    description: str
    location_name: str
    time_step_min: int
    algorithm_name: Optional[Dict] = None
    power_unit: str
    created_on: datetime
    modified_on: datetime
    status: Optional[Dict] = None

class SimulationContainerResponseList(BaseModel):
    items: List[SimulationContainerStatusResponse]