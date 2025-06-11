from abc import ABC, abstractmethod


class ISimulationContainerService(ABC):
    @abstractmethod
    def get_simulation_container_list(self):
        pass

    @abstractmethod
    def create_simulation_container(self, user_id, **data):
        pass