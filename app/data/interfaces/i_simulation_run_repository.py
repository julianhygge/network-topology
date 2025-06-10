from abc import abstractmethod

from app.data.interfaces.i_repository import IRepository, T

class ISimulationRunRepository(IRepository[T]):

    @abstractmethod
    def count_simulation_run_by_status(self, simulation_container_id):
        pass