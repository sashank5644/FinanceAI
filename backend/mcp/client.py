# mcp/client.py
import logging
import asyncio
import json
import uuid
from typing import Any, Dict, List, Optional
from urllib.parse import urljoin, urlparse

import websockets
from websockets.exceptions import ConnectionClosed
from tenacity import retry, stop_after_attempt, wait_exponential

from config import settings

logger = logging.getLogger(__name__)

class MCPClient:
    """Client for interacting with MCP servers."""
    
    def __init__(self, server_urls: Optional[List[str]] = None):
        if isinstance(server_urls, str):
            logger.debug(f"Converting string server_urls to list: {server_urls}")
            server_urls = [server_urls]
        self.server_urls = server_urls or settings.mcp_servers or []
        if not isinstance(self.server_urls, list):
            logger.error(f"server_urls must be a list, got {type(self.server_urls)}")
            self.server_urls = []
        logger.debug(f"Initialized MCPClient with server_urls: {self.server_urls}")
        self.tools: Dict[str, Dict] = {}
        self.websocket_connections: Dict[str, websockets.WebSocketClientProtocol] = {}
        self.client_id = f"client_{uuid.uuid4().hex[:8]}"
        self.timeout = 60
        
    async def connect(self) -> bool:
        """Connect to all MCP servers and discover tools."""
        if not self.server_urls:
            logger.warning("No MCP server URLs provided")
            return False
            
        connected = False
        for server_url in self.server_urls:
            if not isinstance(server_url, str):
                logger.error(f"Invalid server URL: {server_url}")
                continue
            parsed = urlparse(server_url)
            if parsed.scheme not in ("ws", "wss"):
                logger.error(f"Invalid URI scheme for {server_url}: {parsed.scheme}")
                continue
            try:
                await self._connect_to_server(server_url)
                connected = True
            except Exception as e:
                logger.error(f"Failed to connect to {server_url}: {e}")
        return connected
    
    async def _connect_to_server(self, server_url: str):
        """Connect to a single MCP server."""
        ws_url = urljoin(server_url, "/ws").replace("http", "ws")
        try:
            websocket = await websockets.connect(ws_url, ping_interval=30)
            self.websocket_connections[server_url] = websocket
            logger.info(f"Connected to {server_url}")
            
            # Subscribe to tool updates
            subscribe_msg = {
                "type": "subscribe",
                "client_id": self.client_id,
                "event": "tool_update"
            }
            await websocket.send(json.dumps(subscribe_msg))
            
            # Start listening for messages
            asyncio.create_task(self._listen(server_url, websocket))
            
        except Exception as e:
            logger.error(f"Error connecting to {server_url}: {e}")
            raise
    
    async def _listen(self, server_url: str, websocket: websockets.WebSocketClientProtocol):
        """Listen for messages from the server."""
        try:
            async for message in websocket:
                try:
                    data = json.loads(message)
                    if data.get("type") == "tool_update":
                        self.tools.update(data.get("tools", {}))
                        logger.info(f"Updated tools from {server_url}: {list(self.tools.keys())}")
                except json.JSONDecodeError:
                    logger.error(f"Invalid JSON from {server_url}: {message}")
        except ConnectionClosed:
            logger.warning(f"WebSocket connection closed for {server_url}")
            await self._reconnect(server_url)
            
    async def _reconnect(self, server_url: str):
        """Reconnect to a server after connection loss."""
        max_attempts = 5
        for attempt in range(max_attempts):
            try:
                await self._connect_to_server(server_url)
                logger.info(f"Reconnected to {server_url}")
                return
            except Exception as e:
                wait = 2 ** attempt
                logger.warning(f"Reconnect attempt {attempt + 1} failed for {server_url}: {e}. Retrying in {wait}s")
                await asyncio.sleep(wait)
        logger.error(f"Failed to reconnect to {server_url} after {max_attempts} attempts")
        
    @retry(
        stop=stop_after_attempt(3),
        wait=wait_exponential(multiplier=1, min=1, max=10),
        before_sleep=lambda retry_state: logger.warning(
            f"Retrying tool invocation (attempt {retry_state.attempt_number}) after error: {retry_state.outcome.exception()}"
        )
    )
    async def invoke_tool(self, tool_name: str, parameters: Dict[str, Any]) -> Dict[str, Any]:
        """Invoke a tool on an MCP server with retry logic."""
        if tool_name not in self.tools:
            raise ValueError(f"Tool {tool_name} not found")
            
        tool_info = self.tools[tool_name]
        server_url = tool_info["server_url"]
        
        if server_url not in self.websocket_connections:
            raise ValueError(f"No connection to server {server_url}")
            
        request_id = f"req_{uuid.uuid4().hex[:8]}"
        message = {
            "type": "tool_invocation",
            "request_id": request_id,
            "tool_name": tool_name,
            "parameters": parameters,
            "client_id": self.client_id
        }
        
        try:
            websocket = self.websocket_connections[server_url]
            await websocket.send(json.dumps(message))
            
            start_time = asyncio.get_event_loop().time()
            while True:
                try:
                    response = await asyncio.wait_for(websocket.recv(), timeout=self.timeout)
                    response_data = json.loads(response)
                    if response_data.get("request_id") == request_id:
                        if response_data.get("status") == "success":
                            return response_data.get("result", {})
                        else:
                            raise ValueError(f"Tool invocation failed: {response_data.get('error')}")
                except asyncio.TimeoutError:
                    logger.error(f"Timeout waiting for response to {request_id} on {server_url}")
                    raise
                except ConnectionClosed:
                    logger.warning(f"Connection closed during invocation of {tool_name}")
                    await self._reconnect(server_url)
                    raise
                if asyncio.get_event_loop().time() - start_time > self.timeout:
                    logger.error(f"Total invocation timeout for {request_id}")
                    raise asyncio.TimeoutError(f"Tool {tool_name} invocation timed out")
                    
        except Exception as e:
            logger.error(f"Error invoking tool {tool_name}: {e}")
            raise
            
    async def disconnect(self):
        """Disconnect from all MCP servers."""
        for server_url, websocket in list(self.websocket_connections.items()):
            try:
                await websocket.close()
                logger.info(f"Disconnected from {server_url}")
            except Exception as e:
                logger.error(f"Error disconnecting from {server_url}: {e}")
        self.websocket_connections.clear()