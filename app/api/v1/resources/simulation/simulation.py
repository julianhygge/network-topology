from fastapi import APIRouter

from app.api.v1.resources.simulation.algorithms import algorithms_router
from app.api.v1.resources.simulation.bills import bills_router
from app.api.v1.resources.simulation.container import container_router
from app.api.v1.resources.simulation.energy_summary import (
    energy_summary_router,
)
from app.api.v1.resources.simulation.policies import policies_router
from app.api.v1.resources.simulation.runs import runs_router

simulation_router = APIRouter(tags=["Simulation"])


simulation_router.include_router(algorithms_router)
simulation_router.include_router(runs_router)
simulation_router.include_router(policies_router)
simulation_router.include_router(bills_router)
simulation_router.include_router(energy_summary_router)
simulation_router.include_router(container_router)