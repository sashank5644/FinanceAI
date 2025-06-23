# test_mcp.py
"""Test MCP integration."""

import asyncio
import logging
from mcp.client import MCPClient

logging.basicConfig(level=logging.INFO)


async def test_mcp_connection():
    """Test basic MCP functionality."""
    
    print("🔧 Testing MCP Integration...\n")
    
    # Test Financial Data Server
    print("1️⃣ Testing Financial Data Server (port 8081)")
    financial_client = MCPClient("ws://localhost:8081")
    
    try:
        connected = await financial_client.connect()
        if connected:
            print("✅ Connected to Financial Data Server")
            
            # Discover tools
            tools = await financial_client.discover_tools()
            print(f"📦 Discovered {len(tools)} tools:")
            for tool in tools:
                print(f"   - {tool['id']}: {tool['description']}")
            
            # Test stock quote tool
            print("\n🔍 Testing get_stock_quote tool...")
            result = await financial_client.invoke_tool(
                "get_stock_quote",
                {"symbol": "AAPL", "include_extended": True}
            )
            if result.get("success"):
                data = result["data"]
                print(f"   AAPL Price: ${data.get('price', 'N/A')}")
                print(f"   Change: {data.get('change_percent', 'N/A')}%")
            else:
                print(f"   Error: {result.get('error')}")
                
        else:
            print("❌ Failed to connect to Financial Data Server")
            
    except Exception as e:
        print(f"❌ Error: {e}")
    finally:
        await financial_client.disconnect()
    
    print("\n" + "="*50 + "\n")
    
    # Test Knowledge Graph Server
    print("2️⃣ Testing Knowledge Graph Server (port 8082)")
    graph_client = MCPClient("ws://localhost:8082")
    
    try:
        connected = await graph_client.connect()
        if connected:
            print("✅ Connected to Knowledge Graph Server")
            
            # Discover tools
            tools = await graph_client.discover_tools()
            print(f"📦 Discovered {len(tools)} tools:")
            for tool in tools:
                print(f"   - {tool['id']}: {tool['description']}")
            
            # Test find related entities
            print("\n🔍 Testing find_related_entities tool...")
            result = await graph_client.invoke_tool(
                "find_related_entities",
                {"node_id": "company_aapl", "max_depth": 1}
            )
            if result.get("success"):
                data = result["data"]
                print(f"   Related entities: {data.get('related_entities', 0)}")
                print(f"   Relationships: {data.get('relationships', 0)}")
            else:
                print(f"   Error: {result.get('error')}")
                
        else:
            print("❌ Failed to connect to Knowledge Graph Server")
            
    except Exception as e:
        print(f"❌ Error: {e}")
    finally:
        await graph_client.disconnect()
    
    print("\n✨ MCP Integration test complete!")


async def test_agent_with_mcp():
    """Test an agent using MCP tools."""
    print("\n3️⃣ Testing Research Agent with MCP Integration...")
    
    from agents.research_agent import ResearchAgent
    
    agent = ResearchAgent()
    await agent.initialize()
    
    # List available tools
    tools = agent.list_available_tools()
    print(f"\n📋 Agent has {len(tools)} tools available:")
    
    # Group by source
    custom_tools = [t for t in tools if t["source"] == "custom"]
    mcp_tools = [t for t in tools if t["source"].startswith("MCP")]
    
    print(f"\n   Custom tools: {len(custom_tools)}")
    for tool in custom_tools[:3]:
        print(f"      - {tool['name']}")
    
    print(f"\n   MCP tools: {len(mcp_tools)}")
    for tool in mcp_tools[:5]:
        print(f"      - {tool['name']} ({tool['source']})")
    
    # Test a query that uses MCP tools
    print("\n🤖 Testing agent query...")
    result = await agent.run(
        "What is the current stock price of Apple and how is it connected to other tech companies?"
    )
    
    if result["success"]:
        print("\n📊 Agent Response:")
        print(result["output"][:500] + "..." if len(result["output"]) > 500 else result["output"])
    else:
        print(f"\n❌ Error: {result['error']}")
    
    await agent.cleanup()


if __name__ == "__main__":
    print("🚀 MCP Integration Test Suite\n")
    
    # Run tests
    asyncio.run(test_mcp_connection())
    
    # Uncomment to test agent integration
    # asyncio.run(test_agent_with_mcp())