from abc import ABC, abstractmethod


class IWebSocketConnectionManager(ABC):

    @abstractmethod
    async def connect(self, websocket, bid_round_id: str):
        pass

    @abstractmethod
    def disconnect(self, websocket, bid_round_id: str):
        pass

    @abstractmethod
    async def send_personal_message(self, message: str, websocket):
        pass

    @abstractmethod
    async def broadcast(self, message: str, bid_round_id: str):
        pass
