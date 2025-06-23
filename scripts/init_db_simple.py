"""Simple database initialization."""

from rich.console import Console
from rich.panel import Panel
import warnings

# Suppress Neo4j warnings
warnings.filterwarnings("ignore", category=UserWarning, module="neo4j")

console = Console()

def init_all():
    """Initialize all databases."""
    console.print(Panel.fit(
        "[bold]Financial Research Agent - Database Initialization[/bold]",
        border_style="blue"
    ))
    
    results = {}
    
    # PostgreSQL
    console.print("\n[bold blue]Initializing PostgreSQL...[/bold blue]")
    try:
        from utils.db.postgres import init_postgres, create_tables
        init_postgres()
        create_tables()
        console.print("[green]✓ PostgreSQL initialized and tables created[/green]")
        results["PostgreSQL"] = True
    except Exception as e:
        console.print(f"[red]✗ PostgreSQL failed: {e}[/red]")
        results["PostgreSQL"] = False
    
    # Neo4j
    console.print("\n[bold blue]Initializing Neo4j...[/bold blue]")
    try:
        from utils.db.neo4j import get_neo4j_driver
        driver = get_neo4j_driver()
        if driver:
            with driver.session() as session:
                # Create constraints
                constraints = [
                    "CREATE CONSTRAINT IF NOT EXISTS FOR (c:Company) REQUIRE c.id IS UNIQUE",
                    "CREATE CONSTRAINT IF NOT EXISTS FOR (s:Sector) REQUIRE s.id IS UNIQUE",
                ]
                for constraint in constraints:
                    try:
                        session.run(constraint)
                    except:
                        pass
            console.print("[green]✓ Neo4j initialized[/green]")
            results["Neo4j"] = True
        else:
            console.print("[yellow]⚠ Neo4j skipped (not configured)[/yellow]")
            results["Neo4j"] = True
    except Exception as e:
        console.print(f"[red]✗ Neo4j failed: {e}[/red]")
        results["Neo4j"] = False
    
    # Pinecone
    console.print("\n[bold blue]Initializing Pinecone...[/bold blue]")
    try:
        from utils.db.pinecone import init_pinecone
        init_pinecone()
        console.print("[green]✓ Pinecone initialized[/green]")
        results["Pinecone"] = True
    except Exception as e:
        console.print(f"[red]✗ Pinecone failed: {e}[/red]")
        results["Pinecone"] = False
    
    # Redis
    console.print("\n[bold blue]Testing Redis...[/bold blue]")
    try:
        from utils.db.redis import get_redis_client
        client = get_redis_client()
        client.ping()
        console.print("[green]✓ Redis connected[/green]")
        results["Redis"] = True
    except Exception as e:
        console.print(f"[red]✗ Redis failed: {e}[/red]")
        results["Redis"] = False
    
    # Summary
    console.print("\n[bold]Summary:[/bold]")
    all_success = True
    for name, success in results.items():
        status = "[green]✓[/green]" if success else "[red]✗[/red]"
        console.print(f"  {status} {name}")
        if not success:
            all_success = False
    
    if all_success:
        console.print("\n[bold green]All systems initialized! 🚀[/bold green]")
    else:
        console.print("\n[bold yellow]Some systems need attention[/bold yellow]")

if __name__ == "__main__":
    init_all()
