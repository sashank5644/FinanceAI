"""Test PostgreSQL connection and print debug info."""

import os
from dotenv import load_dotenv
from sqlalchemy import create_engine, text
from rich.console import Console

console = Console()

# Load environment variables
load_dotenv()

postgres_url = os.getenv("POSTGRES_URL")
console.print(f"[blue]PostgreSQL URL:[/blue] {postgres_url[:50]}...")

try:
    # Create engine
    engine = create_engine(postgres_url)
    
    # Test connection
    with engine.connect() as conn:
        result = conn.execute(text("SELECT version()"))
        version = result.fetchone()
        console.print(f"[green]✓ Connected to PostgreSQL![/green]")
        console.print(f"Version: {version[0]}")
        
        # List existing tables
        result = conn.execute(text("""
            SELECT table_name 
            FROM information_schema.tables 
            WHERE table_schema = 'public'
        """))
        tables = result.fetchall()
        
        console.print(f"\nExisting tables: {len(tables)}")
        for table in tables:
            console.print(f"  - {table[0]}")
        
except Exception as e:
    console.print(f"[red]✗ Connection failed: {e}[/red]")
    import traceback
    traceback.print_exc()
