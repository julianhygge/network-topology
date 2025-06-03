import datetime
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException

from app.api.authorization.authorization import permission
from app.api.authorization.enums import Permission, Resources
from app.api.v1.dependencies.container_instance import (
    get_energy_summary_service,
)
from app.api.v1.models.responses.simulation_responses import (
    EnergySummaryResponse,
)
from app.domain.services.simulator_engine.energy_summary_service import (
    EnergySummaryService,
)

energy_summary_router = APIRouter()

GetEnergySummaryServiceDep = Depends(get_energy_summary_service)

SimulationRetrievePermissionDep = Depends(
    permission(Resources.SIMULATION, Permission.RETRIEVE)
)


@energy_summary_router.get(
    path="/houses/{house_id}/energy-summary",
    response_model=EnergySummaryResponse,
)
async def get_house_energy_summary(
    house_id: UUID,
    start_datetime: datetime.datetime,
    end_datetime: datetime.datetime,
    service: EnergySummaryService = GetEnergySummaryServiceDep,
    _: UUID = SimulationRetrievePermissionDep,
):
    """
    Retrieve the total imported and exported energy for a specific house
    for a given datetime range.
    """
    try:
        summary = service.get_house_energy_summary(
            house_id, start_datetime, end_datetime
        )
        return EnergySummaryResponse.model_validate(summary)
    except HTTPException as http_exc:
        raise http_exc
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e)) from e


@energy_summary_router.get(
    path="/nodes/{node_id}/energy-summary",
    response_model=EnergySummaryResponse,
)
async def get_node_energy_summary(
    node_id: UUID,
    start_datetime: datetime.datetime,
    end_datetime: datetime.datetime,
    service: EnergySummaryService = GetEnergySummaryServiceDep,
    _: UUID = SimulationRetrievePermissionDep,
):
    """
    Retrieve the total imported and exported energy for all houses under a
    specific node (Locality, substation, substation, or a house itself)
    for a given datetime range.
    """
    try:
        summary = service.get_node_energy_summary(
            node_id, start_datetime, end_datetime
        )
        return EnergySummaryResponse.model_validate(summary)
    except HTTPException as http_exc:
        raise http_exc
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e)) from e
