from typing import Dict, Optional
from fastapi import WebSocket


class ConnectionManager:
    def __init__(self):
        # App users: { user_id: websocket }
        self.active_connections: Dict[str, WebSocket] = {}

        # Single drone connection
        self.drone_connection: Optional[WebSocket] = None

        # Optional: track which user is currently streaming with the drone
        self.active_stream_user: Optional[str] = None

    async def connect(self, client_id: str, websocket: WebSocket, is_drone: bool = False):
        await websocket.accept()

        if is_drone:
            self.drone_connection = websocket
        else:
            self.active_connections[client_id] = websocket

    def disconnect(self, client_id: str, is_drone: bool = False):
        if is_drone:
            self.drone_connection = None
            self.active_stream_user = None
        else:
            if client_id in self.active_connections:
                del self.active_connections[client_id]
            if self.active_stream_user == client_id:
                self.active_stream_user = None

    async def send_to_drone(self, message: dict):
        if self.drone_connection:
            await self.drone_connection.send_json(message)

    async def send_personal_message(self, message: dict, user_id: str):
        websocket = self.active_connections.get(user_id)
        if websocket:
            await websocket.send_json(message)

    async def broadcast(self, message: dict):
        for connection in self.active_connections.values():
            await connection.send_json(message)

    def set_active_stream_user(self, user_id: str):
        self.active_stream_user = user_id

    def get_active_stream_user(self) -> Optional[str]:
        return self.active_stream_user


manager = ConnectionManager()