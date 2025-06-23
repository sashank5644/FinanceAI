# update_strategy_instruments.py
"""Update existing strategies with default instruments."""

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from models.strategy_models import Strategy
from config import settings

# Create engine and session
engine = create_engine(settings.postgres_url)
Session = sessionmaker(bind=engine)
session = Session()

# Default instruments for each strategy type
default_instruments = {
    "momentum": ["AAPL", "MSFT", "NVDA", "TSLA", "META", "GOOGL", "AMZN"],
    "value": ["BRK-B", "JPM", "BAC", "WMT", "JNJ", "PG", "XOM"],
    "growth": ["NVDA", "META", "AMZN", "CRM", "ADBE", "NOW", "SHOP"],
    "market_neutral": ["SPY", "QQQ", "IWM", "DIA", "VTI"],
    "mean_reversion": ["AAPL", "MSFT", "GOOGL", "AMZN", "META"]
}

try:
    # Get all strategies
    strategies = session.query(Strategy).all()
    
    for strategy in strategies:
        # Check if strategy has no instruments or empty list
        if not strategy.instruments or len(strategy.instruments) == 0:
            strategy_type = strategy.strategy_type.value if strategy.strategy_type else "momentum"
            
            # Assign default instruments
            strategy.instruments = default_instruments.get(
                strategy_type, 
                default_instruments["momentum"]
            )
            
            print(f"Updated {strategy.name} ({strategy_type}) with instruments: {strategy.instruments}")
    
    # Commit changes
    session.commit()
    print("\n✅ All strategies updated successfully!")
    
except Exception as e:
    print(f"❌ Error updating strategies: {e}")
    session.rollback()
finally:
    session.close()