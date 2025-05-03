from decimal import Decimal
from typing import Optional
from uuid import UUID


class HouseDTO:
    def __init__(
        self,
        id: UUID,
        transformer_id: UUID,
        load_profile: Optional[str],
        has_solar: bool,
        solar_kw: Optional[Decimal],
        house_type: Optional[str],
        connection_kw: Optional[Decimal],
        has_battery: bool,
        battery_type: Optional[str],
        voluntary_storage: bool,
        battery_peak_charging_rate: Optional[Decimal],
        battery_peak_discharging_rate: Optional[Decimal],
        battery_total_kwh: Optional[Decimal],
    ):
        self.id = id
        self.transformer_id = transformer_id
        self.load_profile = load_profile
        self.has_solar = has_solar
        self.solar_kw = solar_kw
        self.house_type = house_type
        self.connection_kw = connection_kw
        self.has_battery = has_battery
        self.battery_type = battery_type
        self.voluntary_storage = voluntary_storage
        self.battery_peak_charging_rate = battery_peak_charging_rate
        self.battery_peak_discharging_rate = battery_peak_discharging_rate
        self.battery_total_kwh = battery_total_kwh


class TransformerDTO:
    def __init__(
        self,
        id: UUID,
        substation_id: UUID,
        max_capacity_kw: Decimal,
        export_efficiency: Optional[Decimal],
        allow_export: bool,
    ):
        self.id = id
        self.substation_id = substation_id
        self.max_capacity_kw = max_capacity_kw
        self.export_efficiency = export_efficiency
        self.allow_export = allow_export
