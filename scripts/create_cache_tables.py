# create_cache_table.py
"""Create the missing market_data_cache table."""

from sqlalchemy import create_engine, text
from config import settings

def create_cache_table():
    """Create the market_data_cache table."""
    # Create engine
    engine = create_engine(settings.postgres_url)
    
    # SQL to create the table
    create_table_sql = """
    CREATE TABLE IF NOT EXISTS market_data_cache (
        id SERIAL PRIMARY KEY,
        symbol VARCHAR(10) NOT NULL,
        data_type VARCHAR(50) NOT NULL,
        price FLOAT,
        open FLOAT,
        high FLOAT,
        low FLOAT,
        close FLOAT,
        volume BIGINT,
        change FLOAT,
        change_percent FLOAT,
        market_cap BIGINT,
        pe_ratio FLOAT,
        dividend_yield FLOAT,
        data_json JSONB,
        source VARCHAR(50),
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        data_timestamp TIMESTAMP,
        UNIQUE(symbol, data_type)
    );
    
    -- Create indexes
    CREATE INDEX IF NOT EXISTS idx_market_data_cache_symbol ON market_data_cache(symbol);
    CREATE INDEX IF NOT EXISTS idx_market_data_cache_updated_at ON market_data_cache(updated_at);
    """
    
    # Execute the SQL
    with engine.connect() as conn:
        conn.execute(text(create_table_sql))
        conn.commit()
    
    print("✅ Created market_data_cache table successfully!")

if __name__ == "__main__":
    create_cache_table()