"""Quick test to verify system is working."""

import requests
import asyncio
from rich.console import Console

console = Console()

def test_api():
    """Quick API test."""
    try:
        # Test health
        r = requests.get("http://localhost:8000/health")
        if r.status_code == 200:
            console.print("✅ API is running")
            return True
        else:
            console.print("❌ API returned error")
            return False
    except:
        console.print("❌ API is not running. Start with: python main.py")
        return False

async def test_agent():
    """Quick agent test."""
    from agents.research_agent import ResearchAgent
    
    try:
        agent = ResearchAgent(mcp_servers=[])
        await agent.initialize()
        result = await agent.run("What is Apple trading at?")
        
        if result["success"]:
            console.print("✅ Agent working")
            console.print(f"Response: {result['output'][:100]}...")
        else:
            console.print(f"❌ Agent error: {result.get('error')}")
    except Exception as e:
        console.print(f"❌ Agent failed: {str(e)}")

if __name__ == "__main__":
    console.print("[bold]Quick System Test[/bold]\n")
    
    # Test 1: API
    if test_api():
        # Test 2: Agent
        console.print("\nTesting agent...")
        asyncio.run(test_agent())
    else:
        console.print("\n⚠️  Please start the API first with: python main.py")
