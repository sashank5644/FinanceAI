# agents/base_agent.py
"""Base agent with enhanced capabilities."""

import logging
from typing import List, Dict, Any, Optional
import asyncio
import json
import warnings
from langchain.agents import initialize_agent, AgentType
from langchain_core._api.deprecation import LangChainDeprecationWarning
from langchain_google_genai import ChatGoogleGenerativeAI

from mcp.client import MCPClient
from config import settings

logger = logging.getLogger(__name__)

class BaseAgent:
    """Enhanced base agent with MCP integration."""
    
    def __init__(
        self,
        name: str,
        description: str,
        model_name: str = "gemini-1.5-flash",
        mcp_servers: Optional[List[str]] = None
    ):
        self.name = name
        self.description = description
        self.model_name = model_name
        self.mcp_servers = mcp_servers or []
        self.mcp_client = None
        self.llm = None
        self.agent_executor = None
        logger.info(f"Initializing {self.name} with MCP servers: {self.mcp_servers}")
    
    async def initialize(self):
        """Initialize the agent with LLM and MCP connections."""
        try:
            warnings.filterwarnings("ignore", category=LangChainDeprecationWarning)
            
            self.llm = ChatGoogleGenerativeAI(
                model=self.model_name,
                google_api_key=settings.google_api_key,
                temperature=0.3,
                top_p=0.9
            )
            
            tools = await self.get_custom_tools()
            logger.info(f"Creating agent with {len(tools)} tools")
            for tool in tools:
                logger.info(f"  Tool: {tool.name} - {tool.description[:50]}...")
            
            self.agent_executor = initialize_agent(
                tools,
                self.llm,
                agent=AgentType.ZERO_SHOT_REACT_DESCRIPTION,
                verbose=True,
                max_iterations=5,
                early_stopping_method="force"
            )
            
            await self._connect_mcp_servers()
            logger.info(f"{self.name} initialized with {len(tools)} tools")
            
        except Exception as e:
            logger.error(f"Failed to initialize {self.name}: {e}")
            raise
    
    async def _connect_mcp_servers(self):
        """Connect to MCP servers."""
        if not self.mcp_servers:
            logger.warning("No MCP servers configured")
            return
        
        for server in self.mcp_servers:
            try:
                logger.debug(f"Connecting to MCP server: {server}")
                mcp_client = MCPClient(server_urls=[server])  # Pass as list
                connected = await mcp_client.connect()
                if connected:
                    self.mcp_client = mcp_client
                    logger.info(f"Connected to MCP server: {server}")
                else:
                    logger.warning(f"Failed to connect to MCP server: {server}")
            except Exception as e:
                logger.warning(f"Failed to connect to MCP server: {server} - {e}")
    
    async def run(self, query: str) -> Dict[str, Any]:
        """Execute a query with the agent."""
        logger.info(f"Agent {self.name} processing query: {query[:50]}...")
        logger.info(f"Available tools: {[tool.name for tool in self.agent_executor.tools]}")
        
        try:
            result = await asyncio.get_event_loop().run_in_executor(
                None,
                lambda: self.agent_executor.run(query)
            )
            
            parsed_result = self._parse_result(result)
            return {
                "success": True,
                "output": parsed_result,
                "intermediate_steps": getattr(self.agent_executor, "intermediate_steps", [])
            }
            
        except Exception as e:
            logger.error(f"Agent execution error: {e}")
            return {
                "success": False,
                "error": str(e),
                "intermediate_steps": getattr(self.agent_executor, "intermediate_steps", [])
            }
    
    async def get_custom_tools(self) -> List[Any]:
        """Override to define custom tools."""
        return []
    
    def get_system_prompt(self) -> str:
        """Override to define system prompt."""
        return f"You are {self.name}, a specialized AI for {self.description}."
    
    def list_available_tools(self) -> List[Dict[str, str]]:
        """List available tools with descriptions."""
        if not self.agent_executor:
            return []
        return [
            {"name": tool.name, "description": tool.description}
            for tool in self.agent_executor.tools
        ]
    
    def _parse_result(self, result: Any) -> Any:
        """Parse agent result into structured format."""
        try:
            if isinstance(result, str):
                try:
                    return json.loads(result)
                except json.JSONDecodeError:
                    return {"text": result}
            return result
        except Exception as e:
            logger.error(f"Error parsing result: {e}")
            return {"error": str(e)}
    
    async def cleanup(self):
        """Clean up resources."""
        if self.mcp_client:
            await self.mcp_client.disconnect()
            logger.info(f"{self.name} MCP client disconnected")