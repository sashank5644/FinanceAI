# debug_mcp.py
"""Debug script to test MCP connections directly."""

import asyncio
import logging
from mcp.client import MCPClient

# Set up logging
logging.basicConfig(
    level=logging.DEBUG,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)

logger = logging.getLogger(__name__)


async def test_mcp_server(server_name: str, server_url: str):
    """Test a single MCP server."""
    print(f"\n{'='*50}")
    print(f"Testing {server_name} at {server_url}")
    print('='*50)
    
    client = MCPClient(server_url, timeout=5.0)
    
    try:
        # Test connection
        print(f"1. Connecting to {server_name}...")
        connected = await client.connect()
        
        if not connected:
            print(f"   ❌ Failed to connect to {server_name}")
            return
        
        print(f"   ✅ Connected successfully")
        
        # Wait a moment for tool discovery
        await asyncio.sleep(1)
        
        # Test tool discovery
        print(f"\n2. Discovering tools...")
        tools = client.list_tools()
        
        if not tools:
            print(f"   ❌ No tools discovered")
        else:
            print(f"   ✅ Found {len(tools)} tools:")
            for tool in tools:
                print(f"      - {tool['id']}: {tool.get('description', 'No description')}")
        
        # Test health check
        print(f"\n3. Health check...")
        health = await client.health_check()
        print(f"   Response: {health}")
        
        # Test a simple tool if available
        if tools and server_name == "financial_data":
            print(f"\n4. Testing get_stock_quote tool...")
            for tool in tools:
                if tool['id'] == 'get_stock_quote':
                    try:
                        result = await client.invoke_tool(
                            'get_stock_quote',
                            {'symbol': 'AAPL'}
                        )
                        print(f"   ✅ Tool result: {result}")
                    except Exception as e:
                        print(f"   ❌ Tool error: {e}")
                    break
        
    except Exception as e:
        print(f"\n❌ Error testing {server_name}: {e}")
        import traceback
        traceback.print_exc()
    
    finally:
        print(f"\n5. Disconnecting...")
        await client.disconnect()
        print(f"   ✅ Disconnected")


async def main():
    """Test all MCP servers."""
    servers = [
        ("financial_data", "ws://localhost:8081"),
        ("knowledge_graph", "ws://localhost:8082"),
        ("analysis", "ws://localhost:8083"),
        ("document", "ws://localhost:8084"),
    ]
    
    print("🔍 MCP Server Diagnostics")
    print("========================")
    
    for server_name, server_url in servers:
        await test_mcp_server(server_name, server_url)
    
    print(f"\n{'='*50}")
    print("✅ Diagnostics complete")


if __name__ == "__main__":
    asyncio.run(main())