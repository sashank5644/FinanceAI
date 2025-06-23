"""MCP protocol type definitions."""

from typing import Dict, Any, List, Optional, Union
from pydantic import BaseModel, Field
from enum import Enum


class ToolParameterType(str, Enum):
    """Parameter types supported by MCP."""
    STRING = "string"
    NUMBER = "number"
    BOOLEAN = "boolean"
    OBJECT = "object"
    ARRAY = "array"


class ToolParameter(BaseModel):
    """Tool parameter definition."""
    name: str
    type: ToolParameterType
    description: str
    required: bool = True
    default: Optional[Any] = None
    enum: Optional[List[Any]] = None


class Tool(BaseModel):
    """Tool definition in MCP."""
    id: str
    name: str
    description: str
    parameters: List[ToolParameter] = []
    category: Optional[str] = None
    
    def to_langchain_tool(self) -> Dict[str, Any]:
        """Convert to LangChain tool format."""
        return {
            "name": self.name,
            "description": self.description,
            "parameters": {
                "type": "object",
                "properties": {
                    param.name: {
                        "type": param.type.value,
                        "description": param.description,
                        "default": param.default
                    }
                    for param in self.parameters
                },
                "required": [p.name for p in self.parameters if p.required]
            }
        }


class ToolResult(BaseModel):
    """Result from tool execution."""
    tool_id: str
    success: bool
    data: Optional[Any] = None
    error: Optional[str] = None
    metadata: Dict[str, Any] = {}


class MCPMessage(BaseModel):
    """Base MCP message."""
    id: str
    type: str
    timestamp: str
    

class ToolRequest(MCPMessage):
    """Request to execute a tool."""
    type: str = "tool_request"
    tool_id: str
    parameters: Dict[str, Any]


class ToolResponse(MCPMessage):
    """Response from tool execution."""
    type: str = "tool_response"
    result: ToolResult


class ToolListRequest(MCPMessage):
    """Request to list available tools."""
    type: str = "tool_list_request"
    category: Optional[str] = None


class ToolListResponse(MCPMessage):
    """Response with available tools."""
    type: str = "tool_list_response"
    tools: List[Tool]
