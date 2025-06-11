from typing import Any, Dict, cast

from app.data.interfaces.i_repository import IRepository
from app.data.interfaces.i_simulation_run_repository import ISimulationRunRepository
from app.domain.interfaces.i_service import UserIdGeneric
from app.domain.interfaces.simulator_engine.I_simulation_container_service import ISimulationContainerService
from app.domain.services.base_service import BaseService


class SimulationContainerService(BaseService, ISimulationContainerService):
    def __init__(
            self,
            simulation_container_repository: IRepository,
            simulation_run_repository: ISimulationRunRepository
    ):
        super().__init__(simulation_container_repository)
        self._sim_container_repo = simulation_container_repository
        self._sim_run_repo = simulation_run_repository

    def get_simulation_container_list(self):
        sim_container = self._sim_container_repo.list_actives()
        sim_container_list = []
        for sim_container in sim_container:
            status_list = self._sim_run_repo.count_simulation_run_by_status(sim_container)
            sim_dict = self._sim_container_repo.to_dicts(sim_container)
            sim_dict["status"] = {}

            for item in status_list:
                sim_dict["status"][item["status"]] = item["count"]
            sim_container_list.append(sim_dict)

        return sim_container_list


    def create_simulation_container(self, user_id, **data):
        data["created_by"] = user_id
        created_item = self._sim_container_repo.create(data)
        result = self.repository.to_dicts(created_item)
        print(result)
        if isinstance(result, dict):
            return cast(Dict[str, Any], result)
        raise ValueError("Failed to convert created item to dictionary.")


    def create(self, user_id: UserIdGeneric, **kwargs: Any) -> Dict[str, Any]:
        """get simulation container id from request"""
        sim_container_id = kwargs["simulation_container_id"]

        """Count number of simulation run by container id"""
        number_of_sim_run = len(self._sim_run_repo.filter(simulation_container_id=sim_container_id))

        kwargs["run_sequence_identifier"] = f'sm-{number_of_sim_run+1:02}'
        created_item = self._sim_run_repo.create(kwargs)
        result = self.repository.to_dicts(created_item)
        if isinstance(result, dict):
            return cast(Dict[str, Any], result)
        raise ValueError("Failed to convert created item to dictionary.")
