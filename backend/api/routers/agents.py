"""Agent-related API endpoints with rate limiting."""

from fastapi import APIRouter, HTTPException, BackgroundTasks
from pydantic import BaseModel
from datetime import datetime, timedelta
from typing import List, Optional, Dict, Any
import asyncio

from agents.research_agent import ResearchAgent
from utils.rate_limiter import agent_rate_limiter

router = APIRouter()

# Global agent instances (in production, use proper state management)
research_agent = None

class AgentRequest(BaseModel):
    """Agent execution request."""
    query: str
    agent_type: str = "research"
    parameters: Dict[str, Any] = {}

class AgentResponse(BaseModel):
    """Agent execution response."""
    request_id: str
    status: str
    result: Optional[Dict[str, Any]] = None
    error: Optional[str] = None
    rate_limit_info: Optional[Dict[str, Any]] = None

@router.post("/execute", response_model=AgentResponse)
async def execute_agent(request: AgentRequest):
    """Execute an agent with the given query."""
    global research_agent
    
    # Rate limiting - using a simple key for now (in production, use user ID)
    rate_limit_key = "global"  # You could use user IP or auth token
    
    is_allowed, wait_seconds = agent_rate_limiter.is_allowed(rate_limit_key)
    remaining = agent_rate_limiter.get_remaining(rate_limit_key)
    
    if not is_allowed:
        return AgentResponse(
            request_id=f"agent_{datetime.utcnow().timestamp()}",
            status="rate_limited",
            error=f"Rate limit exceeded. Please wait {wait_seconds} seconds before trying again.",
            rate_limit_info={
                "requests_remaining": 0,
                "reset_in_seconds": wait_seconds,
                "limit": 4,
                "window": 60
            }
        )
    
    try:
        if request.agent_type == "research":
            if research_agent is None:
                research_agent = ResearchAgent(mcp_servers=[])
                await research_agent.initialize()
            
            result = await research_agent.run(request.query)
            
            # Exclude intermediate_steps to avoid serialization issues
            sanitized_result = {
                "success": result.get("success", False),
                "output": result.get("output", ""),
                "error": result.get("error", None)
            }
            
            return AgentResponse(
                request_id=f"agent_{datetime.utcnow().timestamp()}",
                status="completed",
                result=sanitized_result,
                rate_limit_info={
                    "requests_remaining": remaining - 1,
                    "limit": 4,
                    "window": 60
                }
            )
        else:
            raise ValueError(f"Unknown agent type: {request.agent_type}")
            
    except Exception as e:
        return AgentResponse(
            request_id=f"agent_{datetime.utcnow().timestamp()}",
            status="failed",
            error=str(e),
            rate_limit_info={
                "requests_remaining": remaining - 1,
                "limit": 4,
                "window": 60
            }
        )

@router.get("/available")
async def list_available_agents():
    """List available agents and their capabilities."""
    return {
        "agents": [
            {
                "type": "research",
                "name": "Research Agent",
                "description": "Conducts financial research and analysis",
                "capabilities": [
                    "Stock price analysis",
                    "Company overview",
                    "Financial news search",
                    "Market sentiment analysis"
                ],
                "rate_limit": {
                    "requests_per_minute": 4,
                    "info": "Free tier rate limit to avoid API restrictions"
                }
            }
        ]
    }

@router.get("/rate-limit-status")
async def get_rate_limit_status():
    """Get current rate limit status."""
    rate_limit_key = "global"
    remaining = agent_rate_limiter.get_remaining(rate_limit_key)
    
    return {
        "requests_remaining": remaining,
        "limit": 4,
        "window_seconds": 60,
        "resets_at": datetime.utcnow() + timedelta(seconds=60)
    }