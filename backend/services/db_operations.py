import asyncio
import logging
from rich.console import Console
from rich.panel import Panel

from utils.logger import setup_logger
from utils.db import (
    init_postgres, 
    get_neo4j_driver, 
    init_pinecone,
    get_redis_client
)
from utils.db.postgres import Base, engine, init_postgres as init_pg
from models.graph_models import CYPHER_TEMPLATES

logger = setup_logger(__name__)
console = Console()


def init_postgresql():
    """Initialize PostgreSQL database and create tables."""
    console.print("[bold blue]Initializing PostgreSQL...[/bold blue]")
    
    try:
        # Initialize connection first
        init_pg()
        
        # Import models to ensure they're registered with Base
        from models import postgres_models
        
        # Now create tables using the initialized engine
        if engine is not None:
            Base.metadata.create_all(bind=engine)
            console.print("[green]✓ PostgreSQL tables created successfully[/green]")
            return True
        else:
            console.print("[red]✗ PostgreSQL engine not initialized[/red]")
            return False
            
    except Exception as e:
        console.print(f"[red]✗ PostgreSQL initialization failed: {e}[/red]")
        logger.error(f"PostgreSQL error details: {e}", exc_info=True)
        return False


def init_neo4j():
    """Initialize Neo4j database and create constraints/indexes."""
    console.print("[bold blue]Initializing Neo4j...[/bold blue]")
    
    try:
        driver = get_neo4j_driver()
        if not driver:
            console.print("[yellow]⚠ Neo4j not configured, skipping[/yellow]")
            return True
        
        with driver.session() as session:
            # Create constraints
            constraints = [
                "CREATE CONSTRAINT IF NOT EXISTS FOR (c:Company) REQUIRE c.id IS UNIQUE",
                "CREATE CONSTRAINT IF NOT EXISTS FOR (s:Sector) REQUIRE s.id IS UNIQUE",
                "CREATE CONSTRAINT IF NOT EXISTS FOR (i:Indicator) REQUIRE i.id IS UNIQUE",
                "CREATE CONSTRAINT IF NOT EXISTS FOR (e:Event) REQUIRE e.id IS UNIQUE",
            ]
            
            for constraint in constraints:
                try:
                    session.run(constraint)
                except Exception as e:
                    # Constraint might already exist
                    logger.debug(f"Constraint creation note: {e}")
            
            # Create indexes
            indexes = [
                "CREATE INDEX IF NOT EXISTS FOR (c:Company) ON (c.symbol)",
                "CREATE INDEX IF NOT EXISTS FOR (c:Company) ON (c.sector)",
                "CREATE INDEX IF NOT EXISTS FOR (e:Event) ON (e.date)",
                "CREATE INDEX IF NOT EXISTS FOR (e:Event) ON (e.event_type)",
            ]
            
            for index in indexes:
                try:
                    session.run(index)
                except Exception as e:
                    # Index might already exist
                    logger.debug(f"Index creation note: {e}")
        
        console.print("[green]✓ Neo4j constraints and indexes created[/green]")
        return True
    except Exception as e:
        console.print(f"[red]✗ Neo4j initialization failed: {e}[/red]")
        return False


def init_pinecone_db():
    """Initialize Pinecone vector database."""
    console.print("[bold blue]Initializing Pinecone...[/bold blue]")
    
    try:
        client = init_pinecone()
        if not client:
            console.print("[yellow]⚠ Pinecone not configured, skipping[/yellow]")
            return True
        
        console.print("[green]✓ Pinecone index ready[/green]")
        return True
    except Exception as e:
        console.print(f"[red]✗ Pinecone initialization failed: {e}[/red]")
        return False


def init_redis_db():
    """Test Redis connection."""
    console.print("[bold blue]Testing Redis connection...[/bold blue]")
    
    try:
        client = get_redis_client()
        client.ping()
        console.print("[green]✓ Redis connection successful[/green]")
        return True
    except Exception as e:
        console.print(f"[red]✗ Redis connection failed: {e}[/red]")
        return False


def main():
    """Run all database initializations."""
    console.print(Panel.fit(
        "[bold]Financial Research Agent - Database Initialization[/bold]",
        border_style="blue"
    ))
    
    results = {
        "PostgreSQL": init_postgresql(),
        "Neo4j": init_neo4j(),
        "Pinecone": init_pinecone_db(),
        "Redis": init_redis_db(),
    }
    
    console.print("\n[bold]Initialization Summary:[/bold]")
    for db, success in results.items():
        status = "[green]✓ Success[/green]" if success else "[red]✗ Failed[/red]"
        console.print(f"  {db}: {status}")
    
    if all(results.values()):
        console.print("\n[bold green]All databases initialized successfully![/bold green]")
    else:
        console.print("\n[bold yellow]Some databases failed to initialize. Check the logs.[/bold yellow]")


if __name__ == "__main__":
    main()