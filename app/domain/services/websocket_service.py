from collections import defaultdict
from app.domain.interfaces.iwebsocket_service import IWebSocketConnectionManager


class WebSocketConnectionManager(IWebSocketConnectionManager):
    def __init__(self):
        self.active_connections = defaultdict(list)

    async def connect(self, websocket, bid_round_id: str):
        await websocket.accept()
        self.active_connections[bid_round_id].append(websocket)

    async def disconnect(self, websocket, bid_round_id: str):
        if websocket in self.active_connections[bid_round_id]:
            self.active_connections[bid_round_id].remove(websocket)
        if not self.active_connections[bid_round_id]:
            del self.active_connections[bid_round_id]

    async def send_personal_message(self, message: str, websocket):
        try:
            await websocket.send_text(message)
        except Exception as e:
            print(f"Error sending message: {e}")

    async def broadcast(self, message: str, bid_round_id: str):
        connections = self.active_connections.get(bid_round_id, [])
        for connection in connections:
            try:
                await connection.send_text(message)
            except Exception as e:
                print(f"Error broadcasting message: {e}")
                await self.disconnect(connection, bid_round_id)
