"""Fix strategy enum types in PostgreSQL."""

from sqlalchemy import create_engine, text
from config import settings

engine = create_engine(settings.postgres_url)

# First, drop the table if it exists with wrong types
drop_sql = """
DROP TABLE IF EXISTS trading_signals CASCADE;
DROP TABLE IF EXISTS strategy_allocations CASCADE;
DROP TABLE IF EXISTS strategies_v2 CASCADE;
"""

# Create the enum types
create_enums_sql = """
-- Drop existing types if they exist
DROP TYPE IF EXISTS strategytype CASCADE;
DROP TYPE IF EXISTS risklevel CASCADE;
DROP TYPE IF EXISTS strategystatus CASCADE;

-- Create enum types
CREATE TYPE strategytype AS ENUM (
    'long_only',
    'long_short',
    'market_neutral',
    'momentum',
    'value',
    'growth',
    'mean_reversion',
    'pairs_trading'
);

CREATE TYPE risklevel AS ENUM (
    'conservative',
    'moderate',
    'aggressive'
);

CREATE TYPE strategystatus AS ENUM (
    'draft',
    'active',
    'paused',
    'archived'
);
"""

# Recreate tables with proper types
create_tables_sql = """
CREATE TABLE strategies_v2 (
    id VARCHAR PRIMARY KEY,
    name VARCHAR NOT NULL,
    description VARCHAR,
    strategy_type strategytype NOT NULL,
    risk_level risklevel DEFAULT 'moderate',
    status strategystatus DEFAULT 'draft',
    instruments JSON,
    sectors JSON,
    market_cap_range JSON,
    entry_rules JSON,
    exit_rules JSON,
    position_sizing JSON,
    max_positions INTEGER DEFAULT 10,
    max_position_size FLOAT DEFAULT 0.1,
    stop_loss FLOAT,
    take_profit FLOAT,
    max_drawdown_limit FLOAT DEFAULT 0.2,
    target_return FLOAT,
    target_volatility FLOAT,
    target_sharpe FLOAT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP,
    created_by VARCHAR,
    research_id VARCHAR REFERENCES research(id)
);

CREATE TABLE strategy_allocations (
    id SERIAL PRIMARY KEY,
    strategy_id VARCHAR REFERENCES strategies_v2(id),
    symbol VARCHAR NOT NULL,
    allocation_percent FLOAT NOT NULL,
    min_allocation FLOAT DEFAULT 0.01,
    max_allocation FLOAT DEFAULT 0.25,
    rebalance_trigger FLOAT DEFAULT 0.05,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE trading_signals (
    id SERIAL PRIMARY KEY,
    strategy_id VARCHAR REFERENCES strategies_v2(id),
    symbol VARCHAR NOT NULL,
    signal_type VARCHAR,
    strength FLOAT,
    current_price FLOAT,
    target_price FLOAT,
    stop_price FLOAT,
    reasons JSON,
    confidence FLOAT,
    is_active BOOLEAN DEFAULT TRUE,
    executed BOOLEAN DEFAULT FALSE,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    expires_at TIMESTAMP
);
"""

try:
    with engine.connect() as conn:
        # Drop existing tables
        conn.execute(text(drop_sql))
        conn.commit()
        print("✓ Dropped existing tables")
        
        # Create enum types
        conn.execute(text(create_enums_sql))
        conn.commit()
        print("✓ Created enum types")
        
        # Create tables
        conn.execute(text(create_tables_sql))
        conn.commit()
        print("✓ Created tables with proper enum types")
        
        # Verify enums
        result = conn.execute(text("""
            SELECT typname, enumlabel 
            FROM pg_enum e 
            JOIN pg_type t ON e.enumtypid = t.oid 
            WHERE typname IN ('strategytype', 'risklevel', 'strategystatus')
            ORDER BY typname, enumsortorder;
        """))
        
        print("\nEnum values:")
        current_type = None
        for row in result:
            if row[0] != current_type:
                current_type = row[0]
                print(f"\n{current_type}:")
            print(f"  - {row[1]}")
            
except Exception as e:
    print(f"Error: {e}")
    raise

print("\n✓ All done! Strategy tables are ready.")
