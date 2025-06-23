"""Enhanced models for backtesting."""

from sqlalchemy import Column, String, Float, Integer, DateTime, JSON, Boolean, Enum, ForeignKey
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from datetime import datetime
import enum

from utils.db.postgres import Base


class BacktestStatus(enum.Enum):
    """Backtest status."""
    PENDING = "pending"
    RUNNING = "running"
    COMPLETED = "completed"
    FAILED = "failed"


class BacktestResult(Base):
    """Enhanced backtest results model."""
    __tablename__ = "backtest_results"
    
    id = Column(String, primary_key=True)
    strategy_id = Column(String, ForeignKey("strategies_v2.id"))
    
    # Test parameters
    start_date = Column(DateTime, nullable=False)
    end_date = Column(DateTime, nullable=False)
    initial_capital = Column(Float, default=100000)
    commission = Column(Float, default=0.001)  # 0.1% per trade
    slippage = Column(Float, default=0.0005)  # 0.05% slippage
    
    # Status
    status = Column(Enum(BacktestStatus), default=BacktestStatus.PENDING)
    progress = Column(Float, default=0.0)  # 0-100%
    
    # Performance metrics
    final_value = Column(Float)
    total_return = Column(Float)
    annualized_return = Column(Float)
    volatility = Column(Float)
    sharpe_ratio = Column(Float)
    sortino_ratio = Column(Float)
    max_drawdown = Column(Float)
    max_drawdown_duration = Column(Integer)  # Days
    
    # Trade statistics
    total_trades = Column(Integer)
    winning_trades = Column(Integer)
    losing_trades = Column(Integer)
    win_rate = Column(Float)
    average_win = Column(Float)
    average_loss = Column(Float)
    profit_factor = Column(Float)
    
    # Risk metrics
    var_95 = Column(Float)  # Value at Risk 95%
    cvar_95 = Column(Float)  # Conditional VaR 95%
    beta = Column(Float)
    alpha = Column(Float)
    
    # Time series data
    equity_curve = Column(JSON)  # Daily portfolio values
    returns_series = Column(JSON)  # Daily returns
    drawdown_series = Column(JSON)  # Drawdown series
    trades = Column(JSON)  # All executed trades
    
    # Benchmark comparison
    benchmark_symbol = Column(String, default="SPY")
    benchmark_return = Column(Float)
    excess_return = Column(Float)
    information_ratio = Column(Float)
    
    # Monte Carlo results
    monte_carlo_runs = Column(Integer, default=0)
    mc_mean_return = Column(Float)
    mc_median_return = Column(Float)
    mc_percentile_5 = Column(Float)
    mc_percentile_95 = Column(Float)
    mc_var_95 = Column(Float)
    
    # Metadata
    created_at = Column(DateTime, server_default=func.now())
    completed_at = Column(DateTime)
    error_message = Column(String)
    
    # Relationships
    strategy = relationship("Strategy", backref="backtest_results")


class BacktestTrade(Base):
    """Individual trades in a backtest."""
    __tablename__ = "backtest_trades"
    
    id = Column(Integer, primary_key=True)
    backtest_id = Column(String, ForeignKey("backtest_results.id"))
    
    # Trade details
    symbol = Column(String, nullable=False)
    side = Column(String)  # 'buy' or 'sell'
    quantity = Column(Float)
    entry_price = Column(Float)
    exit_price = Column(Float)
    entry_date = Column(DateTime)
    exit_date = Column(DateTime)
    
    # P&L
    gross_pnl = Column(Float)
    commission_paid = Column(Float)
    net_pnl = Column(Float)
    return_pct = Column(Float)
    
    # Trade metadata
    entry_reason = Column(String)
    exit_reason = Column(String)
    holding_period = Column(Integer)  # Days
    
    # Relationships
    backtest = relationship("BacktestResult", backref="individual_trades")
