"""Main FastAPI application for Financial Research Agent."""

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager
from services.scheduled_tasks import task_scheduler
import uvicorn
import logging
from api.routers import reports
from rich.logging import RichHandler

from config import settings
from api.routers import health, research, strategies, knowledge_graph, backtest, agents
from utils.logger import setup_logger

# Setup logging
logger = setup_logger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Handle application startup and shutdown."""
    # Startup
    logger.info(f"Starting {settings.app_name} v{settings.app_version}")
    logger.info(f"Environment: {settings.environment}")
    task_scheduler.start()
    
    # Initialize connections, load models, etc.
    from utils.db import init_postgres, get_neo4j_driver, init_pinecone, get_redis_client
    
    try:
        # Initialize databases
        init_postgres()
        get_neo4j_driver()
        init_pinecone()
        get_redis_client()
        logger.info("All database connections initialized")
    except Exception as e:
        logger.error(f"Failed to initialize databases: {e}")
    
    yield
    
    # Shutdown
    logger.info("Shutting down application...")
    task_scheduler.stop()
    from utils.db import close_neo4j_driver
    close_neo4j_driver()


# Create FastAPI instance
app = FastAPI(
    title=settings.app_name,
    version=settings.app_version,
    docs_url="/docs",
    redoc_url="/redoc",
    lifespan=lifespan
)

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include routers
app.include_router(health.router, tags=["health"])
app.include_router(
    research.router, 
    prefix=f"{settings.api_prefix}/research", 
    tags=["research"]
)
app.include_router(
    strategies.router, 
    prefix=f"{settings.api_prefix}/strategies", 
    tags=["strategies"]
)
app.include_router(
    knowledge_graph.router, 
    prefix=f"{settings.api_prefix}/knowledge-graph", 
    tags=["knowledge-graph"]
)
app.include_router(
    backtest.router, 
    prefix=f"{settings.api_prefix}/backtest", 
    tags=["backtest"]
)
app.include_router(
    agents.router,
    prefix=f"{settings.api_prefix}/agents",
    tags=["agents"]
)
app.include_router(
    reports.router,
    prefix=f"{settings.api_prefix}/reports",
    tags=["reports"]
)


@app.get("/")
async def root():
    """Root endpoint."""
    return {
        "name": settings.app_name,
        "version": settings.app_version,
        "docs": "/docs",
        "health": "/health"
    }


if __name__ == "__main__":
    uvicorn.run(
        "main:app",
        host=settings.api_host,
        port=settings.api_port,
        reload=settings.debug,
        log_config={
            "version": 1,
            "disable_existing_loggers": False,
            "formatters": {
                "default": {
                    "format": "%(asctime)s - %(name)s - %(levelname)s - %(message)s",
                },
            },
            "handlers": {
                "default": {
                    "formatter": "default",
                    "class": "logging.StreamHandler",
                    "stream": "ext://sys.stdout",
                },
            },
            "root": {
                "level": "INFO",
                "handlers": ["default"],
            },
        }
    )