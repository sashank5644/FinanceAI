# test_mcp_direct.py
"""Test MCP tools directly without the agent."""

import asyncio
import logging
from mcp.client import MCPClient

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


async def test_direct_tool_call():
    """Test calling MCP tools directly."""
    print("🔍 Testing Direct MCP Tool Calls\n")
    
    # Connect to financial data server
    client = MCPClient("ws://localhost:8081", timeout=60.0)  # Increased timeout
    
    try:
        print("1. Connecting to financial_data server...")
        connected = await client.connect()
        if not connected:
            print("❌ Failed to connect")
            return
        print("✅ Connected\n")
        
        # Wait for tool discovery
        await asyncio.sleep(1)
        
        print("2. Available tools:")
        tools = client.list_tools()
        for tool in tools:
            print(f"   - {tool['id']}")
        print()
        
        print("3. Testing get_stock_quote tool...")
        print("   Calling with symbol='AAPL'")
        
        try:
            # Direct tool invocation
            result = await client.invoke_tool('get_stock_quote', {'symbol': 'AAPL'})
            print(f"   ✅ Result: {result}")
        except asyncio.TimeoutError:
            print("   ❌ Tool call timed out")
        except Exception as e:
            print(f"   ❌ Error: {e}")
            import traceback
            traceback.print_exc()
            
    finally:
        print("\n4. Disconnecting...")
        await client.disconnect()
        print("   ✅ Done")


async def test_custom_tools():
    """Test the custom (non-MCP) tools."""
    print("\n\n🔧 Testing Custom Tools\n")
    
    from agents.research_agent import ResearchAgent
    
    # Get just the custom tools without initializing MCP
    agent = ResearchAgent()
    custom_tools = await agent.get_custom_tools()
    
    print(f"Found {len(custom_tools)} custom tools:")
    for tool in custom_tools:
        print(f"\n📌 {tool.name}:")
        print(f"   Description: {tool.description}")
        
        # Test the get_stock_quote custom tool
        if tool.name == "get_stock_quote":
            print("   Testing with AAPL...")
            try:
                result = tool.func("AAPL")
                print(f"   Result: {result}")
            except Exception as e:
                print(f"   Error: {e}")


if __name__ == "__main__":
    print("="*60)
    print("MCP Tool Testing")
    print("="*60)
    
    # Test direct MCP calls
    asyncio.run(test_direct_tool_call())
    
    # Test custom tools
    asyncio.run(test_custom_tools())