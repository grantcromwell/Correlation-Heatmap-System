"""WebSocket endpoints."""
from uuid import uuid4

from fastapi import APIRouter, WebSocket, WebSocketDisconnect

from app.api.websocket.manager import ws_manager
from app.api.websocket.handlers import handle_message

router = APIRouter()


@router.websocket("/ws/correlations/updates")
async def websocket_correlations(websocket: WebSocket):
    """WebSocket endpoint for correlation updates."""
    client_id = str(uuid4())
    await ws_manager.connect(websocket, client_id)

    try:
        while True:
            data = await websocket.receive_json()
            await handle_message(ws_manager, client_id, data)
    except WebSocketDisconnect:
        ws_manager.disconnect(client_id)


@router.websocket("/ws/workflows/{workflow_id}")
async def websocket_workflow(websocket: WebSocket, workflow_id: str):
    """WebSocket endpoint for workflow progress updates."""
    client_id = str(uuid4())
    await ws_manager.connect(websocket, client_id)
    ws_manager.subscribe(client_id, f"workflow:{workflow_id}")

    try:
        while True:
            await websocket.receive_text()
    except WebSocketDisconnect:
        ws_manager.disconnect(client_id)

