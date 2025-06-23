# mcp/server.py
"""MCP Server implementation for Financial Research Agent."""

import asyncio
import json
import logging
from typing import Dict, Any, List, Optional, Callable
from datetime import datetime
import websockets
from websockets.server import WebSocketServerProtocol

from config import settings

logger = logging.getLogger(__name__)

class MCPServer:
    """Model Context Protocol Server for tool orchestration."""
    
    def __init__(self, host: str = "0.0.0.0", port: int = 8080):
        self.host = host
        self.port = port
        self.clients: Dict[str, WebSocketServerProtocol] = {}
        self.tools: Dict[str, Dict[str, Any]] = {}
        self.handlers: Dict[str, Callable] = {}
        
        # Register default handlers
        self._register_default_handlers()
    
    def _register_default_handlers(self):
        """Register default MCP protocol handlers."""
        self.handlers["discover"] = self.handle_discover
        self.handlers["invoke"] = self.handle_invoke
        self.handlers["subscribe"] = self.handle_subscribe
        self.handlers["unsubscribe"] = self.handle_unsubscribe
        self.handlers["health"] = self.handle_health
    
    async def start(self):
        """Start the MCP server."""
        logger.info(f"Starting MCP server on {self.host}:{self.port}")
        async with websockets.serve(self.handle_connection, self.host, self.port):
            await asyncio.Future()
    
    async def handle_connection(self, websocket: WebSocketServerProtocol, path: str):
        """Handle new client connections."""
        client_id = f"{websocket.remote_address[0]}:{websocket.remote_address[1]}"
        self.clients[client_id] = websocket
        logger.info(f"New MCP client connected: {client_id}")
        
        try:
            async for message in websocket:
                await self.handle_message(client_id, message)
        except websockets.exceptions.ConnectionClosed:
            logger.info(f"Client disconnected: {client_id}")
        finally:
            del self.clients[client_id]
    
    async def handle_message(self, client_id: str, message: str):
        """Handle incoming messages from clients."""
        try:
            data = json.loads(message)
            message_type = data.get("type")
            message_id = data.get("id")
            
            if message_type in self.handlers:
                response = await self.handlers[message_type](data)
                response["id"] = message_id
                await self.send_response(client_id, response)
            else:
                await self.send_error(client_id, message_id, f"Unknown message type: {message_type}")
                
        except json.JSONDecodeError:
            await self.send_error(client_id, None, "Invalid JSON")
        except Exception as e:
            logger.error(f"Error handling message: {e}")
            await self.send_error(client_id, message_id, str(e))
    
    async def send_response(self, client_id: str, response: Dict[str, Any]):
        """Send response to a specific client."""
        if client_id in self.clients:
            await self.clients[client_id].send(json.dumps(response))
    
    async def send_error(self, client_id: str, message_id: Optional[str], error: str):
        """Send error response to a client."""
        response = {
            "type": "error",
            "id": message_id,
            "error": error,
            "timestamp": datetime.utcnow().isoformat()
        }
        await self.send_response(client_id, response)
    
    async def broadcast(self, message: Dict[str, Any]):
        """Broadcast message to all connected clients."""
        message_str = json.dumps(message)
        tasks = [client.send(message_str) for client in self.clients.values()]
        await asyncio.gather(*tasks, return_exceptions=True)
    
    def register_tool(self, tool_id: str, tool_config: Dict[str, Any]):
        """Register a tool with the MCP server."""
        self.tools[tool_id] = {
            "id": tool_id,
            "name": tool_config.get("name", tool_id),
            "description": tool_config.get("description", ""),
            "parameters": tool_config.get("parameters", {}),
            "handler": tool_config.get("handler"),
            "category": tool_config.get("category", "general"),
            "version": tool_config.get("version", "1.0.0"),
            "capabilities": tool_config.get("capabilities", [])
        }
        logger.info(f"Registered tool: {tool_id}")
    
    async def handle_discover(self, message: Dict[str, Any]) -> Dict[str, Any]:
        """Handle tool discovery requests."""
        category = message.get("category")
        
        tools = self.tools.values()
        if category:
            tools = [t for t in tools if t["category"] == category]
        
        return {
            "type": "discover_response",
            "tools": [
                {
                    "id": t["id"],
                    "name": t["name"],
                    "description": t["description"],
                    "category": t["category"],
                    "parameters": t["parameters"],
                    "capabilities": t["capabilities"]
                }
                for t in tools
            ],
            "server_info": {
                "version": "1.0.0",
                "name": "Financial Research MCP Server",
                "capabilities": ["tools", "streaming", "subscriptions"]
            }
        }
    
    async def handle_invoke(self, message: Dict[str, Any]) -> Dict[str, Any]:
        """Handle tool invocation requests."""
        tool_id = message.get("tool_id")
        parameters = message.get("parameters", {})
        
        if tool_id not in self.tools:
            return {
                "type": "invoke_response",
                "error": f"Tool not found: {tool_id}"
            }
        
        tool = self.tools[tool_id]
        handler = tool.get("handler")
        
        if not handler:
            return {
                "type": "invoke_response",
                "error": f"No handler for tool: {tool_id}"
            }
        
        # Map 'input' to 'symbol' if required
        if "input" in parameters and "symbol" in tool["parameters"]:
            parameters["symbol"] = parameters.pop("input")
        
        try:
            result = await handler(**parameters) if asyncio.iscoroutinefunction(handler) else handler(**parameters)
            return {
                "type": "invoke_response",
                "tool_id": tool_id,
                "result": result,
                "success": True
            }
        except TypeError as e:
            logger.error(f"Error invoking tool {tool_id}: {e}")
            return {
                "type": "invoke_response",
                "tool_id": tool_id,
                "error": f"Parameter error: {str(e)}",
                "success": False
            }
        except Exception as e:
            logger.error(f"Error invoking tool {tool_id}: {e}")
            return {
                "type": "invoke_response",
                "tool_id": tool_id,
                "error": str(e),
                "success": False
            }
    
    async def handle_subscribe(self, message: Dict[str, Any]) -> Dict[str, Any]:
        """Handle event subscription requests."""
        event_type = message.get("event_type")
        return {
            "type": "subscribe_response",
            "event_type": event_type,
            "subscribed": True
        }
    
    async def handle_unsubscribe(self, message: Dict[str, Any]) -> Dict[str, Any]:
        """Handle event unsubscription requests."""
        event_type = message.get("event_type")
        return {
            "type": "unsubscribe_response",
            "event_type": event_type,
            "unsubscribed": True
        }
    
    async def handle_health(self, message: Dict[str, Any]) -> Dict[str, Any]:
        """Handle health check requests."""
        return {
            "type": "health_response",
            "status": "healthy",
            "timestamp": datetime.utcnow().isoformat(),
            "connected_clients": len(self.clients),
            "registered_tools": len(self.tools)
        }

# Global MCP server instance
mcp_server = MCPServer(
    host=settings.mcp_server_host,
    port=settings.mcp_server_port
)