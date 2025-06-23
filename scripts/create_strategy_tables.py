"""Create strategy tables."""

from utils.db.postgres import init_postgres, Base, get_engine
from models.strategy_models import Strategy, StrategyAllocation, TradingSignal

# Initialize connection
init_postgres()

# Create tables
Base.metadata.create_all(bind=get_engine(), tables=[
   Strategy.__table__,
   StrategyAllocation.__table__,
   TradingSignal.__table__
])

print("Strategy tables created successfully!")

