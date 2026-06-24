from collections import defaultdict
from fastapi import WebSocket


class ConnectionManager:
    def __init__(self) -> None:
        self.active_connections: dict[int, list[WebSocket]] = defaultdict(list)

    async def connect(self, temple_id: int, websocket: WebSocket) -> None:
        await websocket.accept()
        self.active_connections[temple_id].append(websocket)

    def disconnect(self, temple_id: int, websocket: WebSocket) -> None:
        if websocket in self.active_connections.get(temple_id, []):
            self.active_connections[temple_id].remove(websocket)

    async def broadcast(self, temple_id: int, message: dict) -> None:
        dead_connections: list[WebSocket] = []
        for connection in self.active_connections.get(temple_id, []):
            try:
                await connection.send_json(message)
            except Exception:
                dead_connections.append(connection)
        for connection in dead_connections:
            self.disconnect(temple_id, connection)


manager = ConnectionManager()
