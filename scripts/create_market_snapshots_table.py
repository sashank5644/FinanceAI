# create_market_snapshots_table.py
"""Create the missing market_snapshots table."""

from sqlalchemy import create_engine, text
from config import settings

def create_market_snapshots_table():
    """Create the market_snapshots table."""
    # Create engine
    engine = create_engine(settings.postgres_url)
    
    # SQL to create the table
    create_table_sql = """
    CREATE TABLE IF NOT EXISTS market_snapshots (
        id SERIAL PRIMARY KEY,
        snapshot_date DATE UNIQUE NOT NULL,
        sp500 FLOAT,
        nasdaq FLOAT,
        dow FLOAT,
        vix FLOAT,
        advancing_stocks INTEGER,
        declining_stocks INTEGER,
        total_volume BIGINT,
        sector_performance JSONB,
        top_gainers JSONB,
        top_losers JSONB,
        most_active JSONB,
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    );
    
    -- Create index on snapshot_date
    CREATE INDEX IF NOT EXISTS idx_market_snapshots_date ON market_snapshots(snapshot_date);
    """
    
    # Execute the SQL
    with engine.connect() as conn:
        conn.execute(text(create_table_sql))
        conn.commit()
    
    print("✅ Created market_snapshots table successfully!")

if __name__ == "__main__":
    create_market_snapshots_table()