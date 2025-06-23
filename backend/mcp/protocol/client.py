"""MCP client for connecting to MCP servers."""

import asyncio
import json
import logging
from typing import Dict, Any, List, Optional, Callable
import websockets
from datetime import datetime
import uuid

from .types import Tool, ToolResult, ToolRequest, ToolResponse, ToolListRequest, ToolListResponse

logger = logging.getLogger(__name__)


class MCPClient:
    """Client for connecting to MCP servers."""
    
    def __init__(self, server_url: str, name: str = "financial-agent"):
        self.server_url = server_url
        self.name = name
        self.tools: Dict[str, Tool] = {}
        self.websocket = None
        self.connected = False
        self._response_handlers: Dict[str, asyncio.Future] = {}
        
    async def connect(self):
        """Connect to MCP server."""
        try:
            self.websocket = await websockets.connect(self.server_url)
            self.connected = True
            logger.info(f"Connected to MCP server: {self.server_url}")
            
            # Start message handler
            asyncio.create_task(self._handle_messages())
            
            # Discover available tools
            await self.discover_tools()
            
        except Exception as e:
            logger.error(f"Failed to connect to MCP server: {e}")
            raise
    
    async def disconnect(self):
        """Disconnect from MCP server."""
        if self.websocket:
            await self.websocket.close()
            self.connected = False
            logger.info("Disconnected from MCP server")
    
    async def discover_tools(self) -> List[Tool]:
        """Discover available tools from the server."""
        request = ToolListRequest(
            id=str(uuid.uuid4()),
            timestamp=datetime.utcnow().isoformat()
        )
        
        response = await self._send_and_wait(request)
        
        if isinstance(response, ToolListResponse):
            self.tools = {tool.id: tool for tool in response.tools}
            logger.info(f"Discovered {len(self.tools)} tools")
            return response.tools
        
        return []
    
    async def execute_tool(
        self, 
        tool_id: str, 
        parameters: Dict[str, Any]
    ) -> ToolResult:
        """Execute a tool on the MCP server."""
        if tool_id not in self.tools:
            raise ValueError(f"Unknown tool: {tool_id}")
        
        request = ToolRequest(
            id=str(uuid.uuid4()),
            timestamp=datetime.utcnow().isoformat(),
            tool_id=tool_id,
            parameters=parameters
        )
        
        response = await self._send_and_wait(request)
        
        if isinstance(response, ToolResponse):
            return response.result
        
        raise Exception(f"Unexpected response type: {type(response)}")
    
    async def _send_and_wait(self, message: Any) -> Any:
        """Send a message and wait for response."""
        if not self.connected:
            raise Exception("Not connected to MCP server")
        
        # Create future for response
        future = asyncio.Future()
        self._response_handlers[message.id] = future
        
        # Send message
        await self.websocket.send(message.json())
        
        # Wait for response
        try:
            response = await asyncio.wait_for(future, timeout=30.0)
            return response
        except asyncio.TimeoutError:
            raise Exception(f"Timeout waiting for response to {message.id}")
        finally:
            self._response_handlers.pop(message.id, None)
    
    async def _handle_messages(self):
        """Handle incoming messages from the server."""
        try:
            async for message in self.websocket:
                data = json.loads(message)
                
                # Route to appropriate handler
                if data.get("type") == "tool_response":
                    response = ToolResponse(**data)
                    if response.id in self._response_handlers:
                        self._response_handlers[response.id].set_result(response)
                
                elif data.get("type") == "tool_list_response":
                    response = ToolListResponse(**data)
                    if response.id in self._response_handlers:
                        self._response_handlers[response.id].set_result(response)
                
        except Exception as e:
            logger.error(f"Error handling messages: {e}")
            self.connected = False
    
    def get_langchain_tools(self) -> List[Dict[str, Any]]:
        """Get tools in LangChain format."""
        return [tool.to_langchain_tool() for tool in self.tools.values()]
