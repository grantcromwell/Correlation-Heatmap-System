"""API v1 router aggregation."""
from fastapi import APIRouter

from app.api.v1 import correlations, decoupling, websocket, export

api_router = APIRouter()

# Include all routers
api_router.include_router(correlations.router)
api_router.include_router(decoupling.router)
api_router.include_router(websocket.router)
api_router.include_router(export.router)

