"""PostgreSQL database models."""

from sqlalchemy import (
    Column, String, Float, Integer, DateTime, 
    Text, JSON, ForeignKey, Boolean, Enum
)
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from datetime import datetime
import enum

from utils.db.postgres import Base


class ResearchStatus(enum.Enum):
    """Research status enum."""
    PENDING = "pending"
    IN_PROGRESS = "in_progress"
    COMPLETED = "completed"
    FAILED = "failed"


class OldStrategyType(enum.Enum):
    """Old strategy type enum - DEPRECATED."""
    LONG_ONLY = "long_only"
    LONG_SHORT = "long_short"
    MARKET_NEUTRAL = "market_neutral"
    ARBITRAGE = "arbitrage"


class Research(Base):
    """Research analysis model."""
    __tablename__ = "research"
    
    id = Column(String, primary_key=True)
    query = Column(Text, nullable=False)
    sources = Column(JSON, default=list)
    depth = Column(String, default="comprehensive")
    status = Column(Enum(ResearchStatus), default=ResearchStatus.PENDING)
    
    # Results
    summary = Column(Text)
    key_findings = Column(JSON)
    entities_extracted = Column(JSON)
    sentiment_analysis = Column(JSON)
    
    # Metadata
    created_at = Column(DateTime, server_default=func.now())
    updated_at = Column(DateTime, onupdate=func.now())
    completed_at = Column(DateTime)
    error_message = Column(Text)
    
    # Relationships - removed old strategy reference


# DEPRECATED - Use strategy_models.Strategy instead
class OldStrategy(Base):
    """DEPRECATED - Old strategy model."""
    __tablename__ = "strategies"  # Old table name
    
    id = Column(String, primary_key=True)
    name = Column(String, nullable=False)
    description = Column(Text)
    type = Column(Enum(OldStrategyType), default=OldStrategyType.LONG_ONLY)
    
    # Other fields...
    created_at = Column(DateTime, server_default=func.now())
    updated_at = Column(DateTime, onupdate=func.now())
    
    # Foreign keys
    research_id = Column(String, ForeignKey("research.id"))


class Backtest(Base):
    """Backtest results model."""
    __tablename__ = "backtests"
    
    id = Column(String, primary_key=True)
    strategy_id = Column(String, ForeignKey("strategies_v2.id"))  # Updated to new table
    
    # Test parameters
    start_date = Column(DateTime, nullable=False)
    end_date = Column(DateTime, nullable=False)
    initial_capital = Column(Float, default=100000)
    
    # Results
    final_value = Column(Float)
    total_return = Column(Float)
    annualized_return = Column(Float)
    volatility = Column(Float)
    sharpe_ratio = Column(Float)
    max_drawdown = Column(Float)
    win_rate = Column(Float)
    
    # Detailed results
    equity_curve = Column(JSON)
    trades = Column(JSON)
    monthly_returns = Column(JSON)
    
    # Monte Carlo results
    monte_carlo_results = Column(JSON)
    confidence_intervals = Column(JSON)
    
    # Metadata
    created_at = Column(DateTime, server_default=func.now())
    completed_at = Column(DateTime)


class Report(Base):
    """Generated reports model."""
    __tablename__ = "reports"
    
    id = Column(String, primary_key=True)
    title = Column(String, nullable=False)
    type = Column(String)
    
    # Content
    executive_summary = Column(Text)
    content = Column(JSON)
    charts = Column(JSON)
    
    # References
    research_ids = Column(JSON)
    strategy_ids = Column(JSON)
    backtest_ids = Column(JSON)
    
    # Metadata
    created_at = Column(DateTime, server_default=func.now())
    generated_by = Column(String)


class User(Base):
    """User model for future multi-user support."""
    __tablename__ = "users"
    
    id = Column(String, primary_key=True)
    email = Column(String, unique=True, nullable=False)
    name = Column(String)
    
    # Preferences
    risk_tolerance = Column(String)
    investment_goals = Column(JSON)
    preferred_sectors = Column(JSON)
    
    created_at = Column(DateTime, server_default=func.now())
    
    # Relationships
    portfolios = relationship("Portfolio", back_populates="user")


class Portfolio(Base):
    """Portfolio tracking model."""
    __tablename__ = "portfolios"
    
    id = Column(String, primary_key=True)
    user_id = Column(String, ForeignKey("users.id"))
    name = Column(String, nullable=False)
    
    # Portfolio details
    positions = Column(JSON)
    cash_balance = Column(Float)
    total_value = Column(Float)
    
    # Performance
    total_return = Column(Float)
    daily_returns = Column(JSON)
    
    created_at = Column(DateTime, server_default=func.now())
    updated_at = Column(DateTime, onupdate=func.now())
    
    # Relationships
    user = relationship("User", back_populates="portfolios")
    transactions = relationship("Transaction", back_populates="portfolio")


class Transaction(Base):
    """Transaction history model."""
    __tablename__ = "transactions"
    
    id = Column(String, primary_key=True)
    portfolio_id = Column(String, ForeignKey("portfolios.id"))
    
    # Transaction details
    type = Column(String)
    symbol = Column(String)
    quantity = Column(Float)
    price = Column(Float)
    fees = Column(Float, default=0)
    
    executed_at = Column(DateTime, nullable=False)
    created_at = Column(DateTime, server_default=func.now())
    
    # Relationships
    portfolio = relationship("Portfolio", back_populates="transactions")
