"""Health check endpoints."""

from fastapi import APIRouter, Depends
from datetime import datetime
from typing import Dict, Any

from config import settings

router = APIRouter()


@router.get("/health")
async def health_check() -> Dict[str, Any]:
    """Basic health check endpoint."""
    return {
        "status": "healthy",
        "timestamp": datetime.utcnow().isoformat(),
        "version": settings.app_version,
        "environment": settings.environment
    }


@router.get("/health/detailed")
async def detailed_health_check() -> Dict[str, Any]:
    """Detailed health check with component statuses."""
    
    # TODO: Add actual health checks for each component
    components = {
        "api": "healthy",
        "database": "healthy",
        "redis": "healthy",
        "neo4j": "healthy",
        "mcp_servers": "healthy"
    }
    
    overall_status = "healthy" if all(
        status == "healthy" for status in components.values()
    ) else "degraded"
    
    return {
        "status": overall_status,
        "timestamp": datetime.utcnow().isoformat(),
        "version": settings.app_version,
        "environment": settings.environment,
        "components": components
    }
