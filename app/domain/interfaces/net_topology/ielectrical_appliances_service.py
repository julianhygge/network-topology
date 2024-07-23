from abc import ABC, abstractmethod


class IElectricalAppliancesService(ABC):

    @abstractmethod
    def get_electrical_appliances(self):
        pass

    @abstractmethod
    def create(self, user_id, data):
        pass
