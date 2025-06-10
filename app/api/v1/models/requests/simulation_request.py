from datetime import datetime, time
from typing import Any, Dict, Optional
from uuid import UUID

from pydantic import BaseModel, Field


class SimulationRunsRequestModel(BaseModel):
    simulation_container_id: UUID = Field(...)
    description: str = Field(...)
    run_name: Optional[str] = Field(None)
    topology_root_node_id: Optional[UUID] = Field(None)
    simulation_algorithm_type_id: UUID = Field(...)
    billing_cycle_month: Optional[int] = Field(None)
    billing_cycle_year: Optional[int] = Field(None)
    status: Optional[str] = Field("PENDING")
    simulation_start_timestamp: Optional[datetime] = Field(None)
    simulation_end_timestamp: Optional[datetime] = Field(None)
    locality_id: UUID = Field(...)


class SimulationRunsUpdateModel(BaseModel):
    run_name: Optional[str] = Field(None)
    topology_root_node_id: Optional[UUID] = Field(None)
    simulation_algorithm_type_id: Optional[UUID] = Field(None)
    billing_cycle_month: Optional[int] = Field(None)
    billing_cycle_year: Optional[int] = Field(None)
    status: Optional[str] = Field(None)
    simulation_start_timestamp: Optional[datetime] = Field(None)
    simulation_end_timestamp: Optional[datetime] = Field(None)
    locality_id: Optional[UUID] = Field(None)
    description: Optional[str] = Field(None)


class NetMeteringRequestModel(BaseModel):
    simulation_run_id: UUID = Field(...)
    retail_price_per_kwh: float = Field(...)
    fixed_charge_tariff_rate_per_kw: Optional[float] = Field(210.0)


class NetMeteringUpdateModel(BaseModel):
    retail_price_per_kwh: Optional[float] = Field(None)
    fixed_charge_tariff_rate_per_kw: Optional[float] = Field(None)


class GrossMeteringRequestModel(BaseModel):
    simulation_run_id: UUID = Field(...)
    import_retail_price_per_kwh: float = Field(...)
    export_wholesale_price_per_kwh: float = Field(...)
    fixed_charge_tariff_rate_per_kw: Optional[float] = Field(210.0)


class GrossMeteringUpdateModel(BaseModel):
    import_retail_price_per_kwh: Optional[float] = Field(None)
    export_wholesale_price_per_kwh: Optional[float] = Field(None)
    fixed_charge_tariff_rate_per_kw: Optional[float] = Field(None)


class TimeOfUseRequestModel(BaseModel):
    simulation_run_id: UUID = Field(...)
    time_period_label: Optional[str] = Field(None)
    start_time: time = Field(...)
    end_time: time = Field(...)
    import_retail_rate_per_kwh: float = Field(...)
    export_wholesale_rate_per_kwh: float = Field(...)


class TimeOfUseUpdateModel(BaseModel):
    time_period_label: Optional[str] = Field(None)
    start_time: Optional[time] = Field(None)
    end_time: Optional[time] = Field(None)
    import_retail_rate_per_kwh: Optional[float] = Field(None)
    export_wholesale_rate_per_kwh: Optional[float] = Field(None)


class SimulationSelectedRequestModel(BaseModel):
    simulation_run_id: UUID = Field(...)
    net_metering_policy_type_id: UUID = Field(...)
    fac_charge_per_kwh_imported: Optional[float] = Field(0.0)
    tax_rate_on_energy_charges: Optional[float] = Field(0.09)


class SimulationSelectedUpdateModel(BaseModel):
    net_metering_policy_type_id: Optional[UUID] = Field(None)
    fac_charge_per_kwh_imported: Optional[float] = Field(None)
    tax_rate_on_energy_charges: Optional[float] = Field(None)


class HouseBillRequestModel(BaseModel):
    simulation_run_id: UUID = Field(...)
    house_node_id: UUID = Field(...)
    total_energy_imported_kwh: float = Field(...)
    total_energy_exported_kwh: float = Field(...)
    net_energy_balance_kwh: float = Field(...)
    calculated_bill_amount: float = Field(...)
    bill_details: Dict[str, Any] = Field(...)


class HouseBillUpdateModel(BaseModel):
    house_node_id: Optional[UUID] = Field(None)
    total_energy_imported_kwh: Optional[float] = Field(None)
    total_energy_exported_kwh: Optional[float] = Field(None)
    net_energy_balance_kwh: Optional[float] = Field(None)
    calculated_bill_amount: Optional[float] = Field(None)
    bill_details: Optional[Dict[str, Any]] = Field(None)

class SimulationContainerRequestModel(BaseModel):
    name: str = Field(...)
    time_step_min: int = Field(...)
    power_unit: str = Field(...)
    description: Optional[str] = Field(None)
    location_name: Optional[str] = Field(None)
    algorithm_name: Optional[str] = Field(None)
