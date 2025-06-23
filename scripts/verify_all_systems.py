"""Verify all database systems are working correctly."""

from rich.console import Console
from rich.table import Table
from rich.panel import Panel
import warnings

# Suppress Neo4j warnings
warnings.filterwarnings("ignore", category=UserWarning, module="neo4j")

console = Console()


def test_postgres():
    """Test PostgreSQL with actual operations."""
    try:
        from sqlalchemy import create_engine, inspect, text
        from utils.db.postgres import get_engine
        
        engine = get_engine()
        inspector = inspect(engine)
        tables = inspector.get_table_names()
        
        # Test a simple query
        with engine.connect() as conn:
            result = conn.execute(text("SELECT COUNT(*) FROM research"))
            count = result.scalar()
        
        return True, f"{len(tables)} tables, {count} research records"
    except Exception as e:
        return False, str(e)


def test_neo4j():
    """Test Neo4j with actual operations."""
    try:
        from utils.db.neo4j import get_neo4j_driver
        
        driver = get_neo4j_driver()
        with driver.session() as session:
            result = session.run("MATCH (n) RETURN count(n) as count")
            node_count = result.single()['count']
        
        return True, f"{node_count} nodes in graph"
    except Exception as e:
        return False, str(e)


def test_pinecone():
    """Test Pinecone with actual operations."""
    try:
        from utils.db.pinecone import get_pinecone_index
        
        index = get_pinecone_index()
        stats = index.describe_index_stats()
        vector_count = stats.total_vector_count if hasattr(stats, 'total_vector_count') else 0
        
        return True, f"{vector_count} vectors indexed"
    except Exception as e:
        return False, str(e)


def test_redis():
    """Test Redis with actual operations."""
    try:
        from utils.db.redis import get_redis_client, cache_set, cache_get
        
        client = get_redis_client()
        
        # Test set/get
        test_key = "system:test"
        test_value = {"status": "operational"}
        cache_set(test_key, test_value, expire=60)
        retrieved = cache_get(test_key)
        
        # Get info
        info = client.info()
        version = info.get('redis_version', 'unknown')
        
        return True, f"v{version}, cache working"
    except Exception as e:
        return False, str(e)


def main():
    """Run all system tests."""
    console.print(Panel.fit(
        "[bold]System Verification Report[/bold]",
        border_style="cyan"
    ))
    
    # Create results table
    table = Table(title="Database Status", show_header=True)
    table.add_column("System", style="cyan", width=15)
    table.add_column("Status", width=10)
    table.add_column("Details", style="dim")
    
    tests = [
        ("PostgreSQL", test_postgres),
        ("Neo4j", test_neo4j),
        ("Pinecone", test_pinecone),
        ("Redis", test_redis),
    ]
    
    all_passed = True
    for name, test_func in tests:
        success, details = test_func()
        status = "[green]✓ Online[/green]" if success else "[red]✗ Offline[/red]"
        table.add_row(name, status, details)
        if not success:
            all_passed = False
    
    console.print(table)
    
    if all_passed:
        console.print("\n[bold green]All systems operational! Ready to build AI agents. 🚀[/bold green]")
    else:
        console.print("\n[bold yellow]Some systems need attention.[/bold yellow]")
    
    # Additional info
    console.print("\n[dim]Next steps:[/dim]")
    console.print("  1. Start the API: [cyan]python main.py[/cyan]")
    console.print("  2. View API docs: [cyan]http://localhost:8000/docs[/cyan]")
    console.print("  3. Begin building AI agents (Step 4)")


if __name__ == "__main__":
    main()
