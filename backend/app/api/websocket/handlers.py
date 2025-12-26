"""WebSocket message handlers."""
from typing import Dict

from app.api.websocket.manager import ConnectionManager


async def handle_subscribe(
    manager: ConnectionManager, client_id: str, channels: list[str]
):
    """Handle subscription request."""
    for channel in channels:
        manager.subscribe(client_id, channel)


async def handle_unsubscribe(
    manager: ConnectionManager, client_id: str, channels: list[str]
):
    """Handle unsubscription request."""
    for channel in channels:
        manager.unsubscribe(client_id, channel)


async def handle_message(
    manager: ConnectionManager, client_id: str, message: Dict
):
    """Handle incoming WebSocket message."""
    action = message.get("action")

    if action == "subscribe":
        channels = message.get("channels", [])
        await handle_subscribe(manager, client_id, channels)
    elif action == "unsubscribe":
        channels = message.get("channels", [])
        await handle_unsubscribe(manager, client_id, channels)

