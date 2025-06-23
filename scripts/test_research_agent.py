"""Test the research agent."""

import asyncio
from rich.console import Console
from agents.research_agent import ResearchAgent

console = Console()

async def test_research_agent():
   """Test research agent functionality."""
   console.print("[bold]Testing Research Agent[/bold]")
   
   # Create research agent (without MCP for now)
   agent = ResearchAgent(mcp_servers=[])
   
   # Initialize the agent
   console.print("Initializing agent...")
   await agent.initialize()
   console.print(f"✓ Agent initialized with {len(agent.tools)} tools")
   
   # Test queries
   test_queries = [
       "What is the current stock price of Apple (AAPL)?",
       "Find recent news about semiconductor industry",
       "Analyze the sentiment of recent Tesla news",
   ]
   
   for query in test_queries:
       console.print(f"\n[blue]Query:[/blue] {query}")
       
       result = await agent.run(query)
       
       if result["success"]:
           console.print(f"[green]Response:[/green] {result['output']}")
       else:
           console.print(f"[red]Error:[/red] {result['error']}")
   
   # Cleanup
   await agent.cleanup()


if __name__ == "__main__":
   asyncio.run(test_research_agent())