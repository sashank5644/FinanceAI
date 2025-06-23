"""Manually create PostgreSQL tables."""

from sqlalchemy import create_engine
from utils.db.postgres import Base
from rich.console import Console
import os
from dotenv import load_dotenv

console = Console()

# Load environment variables
load_dotenv()

# Import all models to register them with Base
from models.postgres_models import (
    Research, Strategy, Backtest, Report,
    User, Portfolio, Transaction
)

try:
    # Create engine directly
    postgres_url = os.getenv("POSTGRES_URL")
    if not postgres_url:
        raise Exception("POSTGRES_URL not found in environment")
    
    console.print(f"[blue]Creating tables with URL:[/blue] {postgres_url[:50]}...")
    
    engine = create_engine(postgres_url, echo=True)
    
    # Create all tables
    Base.metadata.create_all(bind=engine)
    
    console.print("[green]✓ All tables created successfully![/green]")
    
    # List created tables
    from sqlalchemy import inspect
    inspector = inspect(engine)
    tables = inspector.get_table_names()
    
    console.print(f"\n[bold]Created {len(tables)} tables:[/bold]")
    for table in tables:
        console.print(f"  ✓ {table}")
        
except Exception as e:
    console.print(f"[red]✗ Table creation failed: {e}[/red]")
    import traceback
    traceback.print_exc()
