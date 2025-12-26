"""FastAPI application entry point."""
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.api.v1.router import api_router
from app.api.graphql.schema import create_graphql_router
from app.api.websocket.manager import ConnectionManager
from app.config import settings

app = FastAPI(
    title="Correlation Heatmap API",
    description="API for discovering, backtesting, and visualizing correlations across asset classes",
    version="0.1.0",
    docs_url="/docs",
    redoc_url="/redoc",
)

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=[settings.frontend_url],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include API routers
app.include_router(api_router, prefix=settings.api_prefix)

# GraphQL router
graphql_router = create_graphql_router()
app.include_router(graphql_router, prefix="/graphql")

# WebSocket manager
ws_manager = ConnectionManager()


@app.get("/health")
async def health_check():
    """Health check endpoint."""
    return {"status": "healthy", "version": "0.1.0"}


@app.get("/health/db")
async def db_health_check():
    """Database health check endpoint."""
    # TODO: Implement database connectivity check
    return {"status": "not_implemented"}


@app.get("/health/apis")
async def apis_health_check():
    """External APIs health check endpoint."""
    # TODO: Implement external API connectivity checks
    return {"status": "not_implemented"}

