"""WebSocket connection manager."""
from typing import Dict, Set

from fastapi import WebSocket


class ConnectionManager:
    """Manages WebSocket connections and subscriptions."""

    def __init__(self):
        """Initialize connection manager."""
        self.active_connections: Dict[str, WebSocket] = {}
        self.subscriptions: Dict[str, Set[str]] = {}

    async def connect(self, websocket: WebSocket, client_id: str):
        """Accept WebSocket connection."""
        await websocket.accept()
        self.active_connections[client_id] = websocket
        self.subscriptions[client_id] = set()

    def disconnect(self, client_id: str):
        """Remove WebSocket connection."""
        self.active_connections.pop(client_id, None)
        self.subscriptions.pop(client_id, None)

    async def send_personal_message(self, message: dict, client_id: str):
        """Send message to specific client."""
        if client_id in self.active_connections:
            await self.active_connections[client_id].send_json(message)

    async def broadcast(self, message: dict, channel: str):
        """Broadcast message to all subscribers of a channel."""
        for client_id, channels in self.subscriptions.items():
            if channel in channels:
                await self.send_personal_message(message, client_id)

    def subscribe(self, client_id: str, channel: str):
        """Subscribe client to channel."""
        if client_id in self.subscriptions:
            self.subscriptions[client_id].add(channel)

    def unsubscribe(self, client_id: str, channel: str):
        """Unsubscribe client from channel."""
        if client_id in self.subscriptions:
            self.subscriptions[client_id].discard(channel)

