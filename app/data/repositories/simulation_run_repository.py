from app.data.interfaces.i_simulation_run_repository import ISimulationRunRepository
from app.data.repositories.base_repository import BaseRepository
from app.data.schemas.simulation.simulation_runs_schema import SimulationRuns
from peewee import fn


class SimulationRunRepository(BaseRepository[SimulationRuns], ISimulationRunRepository[SimulationRuns]):


    def __init__(self):
        super().__init__(model=SimulationRuns)

    def count_simulation_run_by_status(self, simulation_container_id):
        query = (
            self._model
            .select(
                self._model.status,
                fn.COUNT(self._model.id).alias('count'))
                .where(self._model.simulation_container_id == simulation_container_id)
                .group_by(self._model.status)
                .dicts()
            )

        return list(query)
