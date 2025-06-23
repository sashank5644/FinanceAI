"""MCP server base implementation."""

import asyncio
import json
import logging
from typing import Dict, Any, List, Optional, Callable
import websockets
from abc import ABC, abstractmethod

from .types import Tool, ToolResult, ToolRequest, ToolResponse

logger = logging.getLogger(__name__)


class MCPServer(ABC):
    """Base class for MCP servers."""
    
    def __init__(self, name: str, host: str = "localhost", port: int = 8080):
        self.name = name
        self.host = host
        self.port = port
        self.tools: Dict[str, Tool] = {}
        
    @abstractmethod
    def register_tools(self) -> Dict[str, Tool]:
        """Register available tools. Must be implemented by subclasses."""
        pass
    
    @abstractmethod
    async def handle_tool_request(self, request: ToolRequest) -> ToolResult:
        """Handle tool execution request. Must be implemented by subclasses."""
        pass
    
    async def start(self):
        """Start the MCP server."""
        self.tools = self.register_tools()
        logger.info(f"Starting {self.name} on ws://{self.host}:{self.port}")
        
        async with websockets.serve(
            self.handle_client,
            self.host,
            self.port
        ):
            await asyncio.Future()  # Run forever
    
    async def handle_client(self, websocket, path):
        """Handle client connections."""
        logger.info(f"Client connected to {self.name}")
        
        try:
            async for message in websocket:
                await self.process_message(websocket, message)
        except websockets.exceptions.ConnectionClosed:
            logger.info("Client disconnected")
        except Exception as e:
            logger.error(f"Error handling client: {e}")
    
    async def process_message(self, websocket, message: str):
        """Process incoming messages."""
        try:
            data = json.loads(message)
            
            if data.get("type") == "tool_list_request":
                response = {
                    "id": data["id"],
                    "type": "tool_list_response",
                    "tools": [tool.dict() for tool in self.tools.values()]
                }
                await websocket.send(json.dumps(response))
            
            elif data.get("type") == "tool_request":
                request = ToolRequest(**data)
                result = await self.handle_tool_request(request)
                response = ToolResponse(
                    id=request.id,
                    timestamp=request.timestamp,
                    result=result
                )
                await websocket.send(response.json())
                
        except Exception as e:
            logger.error(f"Error processing message: {e}")
            error_response = {
                "type": "error",
                "error": str(e)
            }
            await websocket.send(json.dumps(error_response))
