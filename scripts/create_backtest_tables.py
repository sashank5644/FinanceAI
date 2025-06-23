"""Create backtest tables."""

from sqlalchemy import create_engine, text
from config import settings

engine = create_engine(settings.postgres_url)

# Create tables
create_tables_sql = """
-- Drop existing tables
DROP TABLE IF EXISTS backtest_trades CASCADE;
DROP TABLE IF EXISTS backtest_results CASCADE;

-- Create backtest results table
CREATE TABLE backtest_results (
    id VARCHAR PRIMARY KEY,
    strategy_id VARCHAR REFERENCES strategies_v2(id),
    start_date TIMESTAMP NOT NULL,
    end_date TIMESTAMP NOT NULL,
    initial_capital FLOAT DEFAULT 100000,
    commission FLOAT DEFAULT 0.001,
    slippage FLOAT DEFAULT 0.0005,
    status VARCHAR DEFAULT 'pending',
    progress FLOAT DEFAULT 0,
    
    -- Performance metrics
    final_value FLOAT,
    total_return FLOAT,
    annualized_return FLOAT,
    volatility FLOAT,
    sharpe_ratio FLOAT,
    sortino_ratio FLOAT,
    max_drawdown FLOAT,
    max_drawdown_duration INTEGER,
    
    -- Trade statistics
    total_trades INTEGER,
    winning_trades INTEGER,
    losing_trades INTEGER,
    win_rate FLOAT,
    average_win FLOAT,
    average_loss FLOAT,
    profit_factor FLOAT,
    
    -- Risk metrics
    var_95 FLOAT,
    cvar_95 FLOAT,
    beta FLOAT,
    alpha FLOAT,
    
    -- Time series data
    equity_curve JSON,
    returns_series JSON,
    drawdown_series JSON,
    trades JSON,
    
    -- Benchmark comparison
    benchmark_symbol VARCHAR DEFAULT 'SPY',
    benchmark_return FLOAT,
    excess_return FLOAT,
    information_ratio FLOAT,
    
    -- Monte Carlo
    monte_carlo_runs INTEGER DEFAULT 0,
    mc_mean_return FLOAT,
    mc_median_return FLOAT,
    mc_percentile_5 FLOAT,
    mc_percentile_95 FLOAT,
    mc_var_95 FLOAT,
    
    -- Metadata
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    completed_at TIMESTAMP,
    error_message TEXT
);

-- Create index
CREATE INDEX idx_backtest_strategy ON backtest_results(strategy_id);
CREATE INDEX idx_backtest_status ON backtest_results(status);
"""

with engine.connect() as conn:
    conn.execute(text(create_tables_sql))
    conn.commit()

print("✓ Backtest tables created successfully!")
