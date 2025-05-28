from datetime import datetime, time
from typing import Optional, Dict, Any

from pydantic import BaseModel, Field
from uuid import UUID

class SimulationRunsRequestModel(BaseModel):
    run_name: Optional[str] = Field(None, example="Simulation-1")
    topology_root_node_id: UUID = Field(..., example="94522a0a-c8f1-40f8-a2e5-9aed2dc55555")
    simulation_algorithm_type_id: UUID = Field(..., example="94522a0a-c8f1-40f8-a2e5-9aed2dc55555")
    billing_cycle_month: int = Field(..., example=1)
    billing_cycle_year: int = Field(..., example=2021)
    status: str = Field(..., example="Completed")
    simulation_start_timestamp: datetime = Field(..., example="2023-02-02 00:00:00")
    simulation_end_timestamp: datetime = Field(..., example="2023-02-02 00:00:00")

class SimulationRunsUpdateModel(BaseModel):
    run_name: Optional[str] = Field(None, example="Simulation-1")
    topology_root_node_id: Optional[UUID] = Field(None, example="94522a0a-c8f1-40f8-a2e5-9aed2dc55555")
    simulation_algorithm_type_id: Optional[UUID] = Field(None, example="94522a0a-c8f1-40f8-a2e5-9aed2dc55555")
    billing_cycle_month: Optional[int] = Field(None, example=1)
    billing_cycle_year: Optional[int] = Field(None, example=2021)
    status: Optional[str] = Field(None, example="Completed")
    simulation_start_timestamp: Optional[datetime] = Field(None, example="2023-02-02 00:00:00")
    simulation_end_timestamp: Optional[datetime] = Field(None, example="2023-02-02 00:00:00")


class NetMeteringRequestModel(BaseModel):
    simulation_run_id: UUID = Field(..., example="94522a0a-c8f1-40f8-a2e5-9aed2dc55555")
    retail_price_per_kwh: float = Field(..., example=5.2)

class NetMeteringUpdateModel(BaseModel):
    retail_price_per_kwh: Optional[float] = Field(None, example=5.2)

class GrossMeteringRequestModel(BaseModel):
    simulation_run_id: UUID = Field(..., example="94522a0a-c8f1-40f8-a2e5-9aed2dc55555")
    import_retail_price_per_kwh: float = Field(..., example=5.2)
    export_wholesale_price_per_kwh: float = Field(..., example=5)

class GrossMeteringUpdateModel(BaseModel):
    import_retail_price_per_kwh: Optional[float] = Field(None, example=5.2)
    export_wholesale_price_per_kwh: Optional[float] = Field(None, example=5.2)

class TimeOfUseRequestModel(BaseModel):
    simulation_run_id: UUID = Field(..., example="94522a0a-c8f1-40f8-a2e5-9aed2dc55555")
    time_period_label: Optional[str] = Field(None, example="Completed")
    start_time: time = Field(..., example="06:34:00")
    end_time: time = Field(..., example="07:12:00")
    import_retail_rate_per_kwh: float = Field(..., example=2.4)
    export_wholesale_rate_per_kwh: float = Field(..., example=2.4)


class TimeOfUseUpdateModel(BaseModel):
    time_period_label: Optional[str] = Field(None, example="Completed")
    start_time: Optional[time] = Field(None, example="06:34:00")
    end_time: Optional[time] = Field(None, example="06:34:00")
    import_retail_rate_per_kwh: Optional[float] = Field(None, example=5.2)
    export_wholesale_rate_per_kwh: Optional[float] = Field(None, example=5.2)

class SimulationSelectedRequestModel(BaseModel):
    simulation_run_id: UUID = Field(..., example="94522a0a-c8f1-40f8-a2e5-9aed2dc55555")
    net_metering_policy_type_id: UUID = Field(..., example="94522a0a-c8f1-40f8-a2e5-9aed2dc55555")
    fixed_charge_tariff_rate_per_kw: float = Field(..., example=5)
    fac_charge_per_kwh_imported: float = Field(..., example=7.2)
    tax_rate_on_energy_charges: float = Field(..., example=9)

class SimulationSelectedUpdateModel(BaseModel):
    net_metering_policy_type_id: Optional[UUID] = Field(None, example="94522a0a-c8f1-40f8-a2e5-9aed2dc55555")
    fixed_charge_tariff_rate_per_kw: Optional[float] = Field(None, example=5.2)
    fac_charge_per_kwh_imported: Optional[float] = Field(None, example=5.2)
    tax_rate_on_energy_charges: Optional[float] = Field(None, example=5)

class HouseBillRequestModel(BaseModel):
    simulation_run_id: UUID = Field(..., example="94522a0a-c8f1-40f8-a2e5-9aed2dc55555")
    house_node_id: UUID = Field(..., example="94522a0a-c8f1-40f8-a2e5-9aed2dc55555")
    total_energy_imported_kwh: float = Field(..., example=5)
    total_energy_exported_kwh: float = Field(..., example=5)
    net_energy_balance_kwh: float = Field(..., example=5)
    calculated_bill_amount: float = Field(..., example=5)
    bill_details: Dict[str, Any] = Field(..., example={"house_name": "House1", "peak_hours": True})

class HouseBillUpdateModel(BaseModel):
    house_node_id: Optional[UUID] = Field(None, example="94522a0a-c8f1-40f8-a2e5-9aed2dc55555")
    total_energy_imported_kwh: Optional[float] = Field(None, example=5.2)
    total_energy_exported_kwh: Optional[float] = Field(None, example=5.2)
    net_energy_balance_kwh: Optional[float] = Field(None, example=5.2)
    calculated_bill_amount: Optional[float] = Field(None, example=5.2)
    bill_details: Optional[Dict[str, Any]] = Field(None, example={"house_name": "House1", "peak_hours": True})

