"""Test agent functionality via API."""

import requests
import json
from rich.console import Console
from rich.table import Table
from rich.panel import Panel
import time

console = Console()

API_BASE = "http://localhost:8000/api/v1"


def test_agent_queries():
    """Test various agent queries."""
    
    test_cases = [
        {
            "name": "Stock Price Query",
            "query": "What is the current stock price and market cap of Apple (AAPL)?",
            "expected": ["price", "AAPL", "market"]
        },
        {
            "name": "Market News",
            "query": "Find recent news about the semiconductor industry",
            "expected": ["news", "semiconductor"]
        },
        {
            "name": "Company Analysis",
            "query": "Analyze Microsoft's recent performance and give me key metrics",
            "expected": ["Microsoft", "performance"]
        },
        {
            "name": "Sentiment Analysis",
            "query": "What is the market sentiment around Tesla based on recent news?",
            "expected": ["sentiment", "Tesla", "news"]
        }
    ]
    
    results = []
    
    for test in test_cases:
        console.print(f"\n[bold blue]Testing: {test['name']}[/bold blue]")
        console.print(f"Query: {test['query']}")
        
        # Make request
        response = requests.post(
            f"{API_BASE}/agents/execute",
            json={
                "query": test["query"],
                "agent_type": "research"
            }
        )
        
        if response.status_code == 200:
            data = response.json()
            
            if data["status"] == "completed" and data["result"]["success"]:
                output = data["result"]["output"]
                console.print(f"[green]✓ Success[/green]")
                console.print(f"Response preview: {output[:200]}...")
                
                # Check if expected terms are in response
                found_terms = [term for term in test["expected"] if term.lower() in output.lower()]
                results.append({
                    "test": test["name"],
                    "status": "✓ Passed",
                    "found_terms": len(found_terms),
                    "expected_terms": len(test["expected"])
                })
            else:
                console.print(f"[red]✗ Failed: {data.get('error', 'Unknown error')}[/red]")
                results.append({
                    "test": test["name"],
                    "status": "✗ Failed",
                    "found_terms": 0,
                    "expected_terms": len(test["expected"])
                })
        else:
            console.print(f"[red]✗ HTTP Error: {response.status_code}[/red]")
            results.append({
                "test": test["name"],
                "status": "✗ Error",
                "found_terms": 0,
                "expected_terms": len(test["expected"])
            })
        
        time.sleep(2)  # Rate limiting
    
    # Display results table
    console.print("\n")
    table = Table(title="Agent Test Results")
    table.add_column("Test Case", style="cyan")
    table.add_column("Status", justify="center")
    table.add_column("Terms Found", justify="center")
    
    for result in results:
        status_style = "green" if "Passed" in result["status"] else "red"
        table.add_row(
            result["test"],
            f"[{status_style}]{result['status']}[/{status_style}]",
            f"{result['found_terms']}/{result['expected_terms']}"
        )
    
    console.print(table)


def test_research_workflow():
    """Test a complete research workflow."""
    console.print(Panel.fit("[bold]Testing Complete Research Workflow[/bold]"))
    
    # Step 1: Initial research
    console.print("\n[bold]Step 1: Initial Research[/bold]")
    response = requests.post(
        f"{API_BASE}/research/analyze",
        json={
            "query": "Analyze the electric vehicle market trends in 2024",
            "sources": ["news", "market_data"],
            "depth": "comprehensive"
        }
    )
    
    if response.status_code == 200:
        research_data = response.json()
        research_id = research_data["research_id"]
        console.print(f"✓ Research created: {research_id}")
    else:
        console.print(f"✗ Failed to create research: {response.status_code}")
        return
    
    # Step 2: Check knowledge graph
    console.print("\n[bold]Step 2: Knowledge Graph Stats[/bold]")
    response = requests.get(f"{API_BASE}/knowledge-graph/stats")
    
    if response.status_code == 200:
        stats = response.json()
        console.print(f"✓ Graph stats retrieved")
        console.print(f"  Total nodes: {stats['total_nodes']}")
        console.print(f"  Total edges: {stats['total_edges']}")
    
    # Step 3: Generate strategy (placeholder)
    console.print("\n[bold]Step 3: Strategy Generation[/bold]")
    console.print("  [dim]Strategy generation will be implemented next[/dim]")


if __name__ == "__main__":
    console.print(Panel.fit(
        "[bold]Financial Research Agent - API Test Suite[/bold]",
        border_style="blue"
    ))
    
    # Test agent queries
    test_agent_queries()
    
    # Test research workflow
    console.print("\n" + "="*50 + "\n")
    test_research_workflow()
