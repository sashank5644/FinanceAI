"""Models for caching financial data."""

from sqlalchemy import Column, String, Float, Integer, DateTime, JSON, Boolean, Index
from sqlalchemy.sql import func
from datetime import datetime

from utils.db.postgres import Base


class MarketDataCache(Base):
    """Cache for market data including stocks and indices."""
    __tablename__ = "market_data_cache"
    
    id = Column(Integer, primary_key=True)
    symbol = Column(String, nullable=False)
    data_type = Column(String, nullable=False)  # 'quote', 'company', 'index'
    
    # Price data
    price = Column(Float)
    open = Column(Float)
    high = Column(Float)
    low = Column(Float)
    close = Column(Float)
    volume = Column(Integer)
    change = Column(Float)
    change_percent = Column(Float)
    
    # Additional data
    market_cap = Column(Integer)
    pe_ratio = Column(Float)
    dividend_yield = Column(Float)
    
    # Metadata
    data_json = Column(JSON)  # Store complete response
    source = Column(String)  # 'alpha_vantage', 'yahoo', etc.
    
    # Timestamps
    created_at = Column(DateTime, server_default=func.now())
    updated_at = Column(DateTime, onupdate=func.now())
    data_timestamp = Column(DateTime)  # When the data is from
    
    # Indexes for fast lookup
    __table_args__ = (
        Index('idx_symbol_type', 'symbol', 'data_type'),
        Index('idx_updated_at', 'updated_at'),
    )


class NewsCache(Base):
    """Cache for financial news articles."""
    __tablename__ = "news_cache"
    
    id = Column(Integer, primary_key=True)
    article_id = Column(String, unique=True)  # Unique identifier
    
    # Article data
    title = Column(String)
    description = Column(String)
    content = Column(String)
    source = Column(String)
    author = Column(String)
    url = Column(String)
    
    # Metadata
    published_at = Column(DateTime)
    keywords = Column(JSON)  # List of keywords/tickers mentioned
    sentiment_score = Column(Float)  # -1 to 1
    
    # Cache metadata
    created_at = Column(DateTime, server_default=func.now())
    query_terms = Column(JSON)  # What queries returned this article
    
    # Index for search
    __table_args__ = (
        Index('idx_published_at', 'published_at'),
        Index('idx_keywords', 'keywords'),
    )


class MarketSnapshot(Base):
    """Daily market snapshots for historical tracking."""
    __tablename__ = "market_snapshots"
    
    id = Column(Integer, primary_key=True)
    snapshot_date = Column(DateTime, nullable=False)
    
    # Major indices
    sp500 = Column(Float)
    nasdaq = Column(Float)
    dow = Column(Float)
    vix = Column(Float)
    
    # Market stats
    advancing_stocks = Column(Integer)
    declining_stocks = Column(Integer)
    total_volume = Column(Integer)
    
    # Sector performance (JSON)
    sector_performance = Column(JSON)
    
    # Top movers
    top_gainers = Column(JSON)  # List of {symbol, change_percent}
    top_losers = Column(JSON)
    most_active = Column(JSON)
    
    created_at = Column(DateTime, server_default=func.now())
    
    # Unique constraint on date
    __table_args__ = (
        Index('idx_snapshot_date', 'snapshot_date', unique=True),
    )
