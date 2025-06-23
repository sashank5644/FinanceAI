# test_tools.py
import asyncio
import logging
from datetime import datetime, timedelta
import uuid
import pandas as pd

from agents.research_agent import ResearchAgent
from agents.backtest_agent import BacktestAgent
from models.strategy_models import Strategy
from models.backtest_models import BacktestResult, BacktestStatus
from utils.db import get_db, init_postgres
from utils.db.redis import cache_delete, get_cache_key

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

async def test_research_agent():
    print("🧪 Testing ResearchAgent...")
    
    # Clear cache
    for sym in ["AAPL", "MSFT", "SPY"]:
        cache_delete(get_cache_key("market_data", sym, "daily"))
    cache_delete(get_cache_key("market_data", "indices", "overview"))
    
    # Initialize ResearchAgent
    agent = ResearchAgent()
    await agent.initialize()
    
    print(f"✅ Research Agent initialized with {len(agent.agent_executor.tools)} tools\n")
    print("📋 Available tools:")
    for tool in agent.list_available_tools():
        print(f"   - {tool['name']}: {tool['description']}")
    print("\n")
    
    # Test stock quote
    print("Testing stock quote for AAPL:")
    try:
        result = await agent.run("Get the current stock price for AAPL")
        if result["success"] and "text" in result["output"]:
            price = result["output"]["text"].split("$")[-1].rstrip(".")
            print(f"✅ Success! Price: {price}")
        else:
            print(f"❌ Failed: {result.get('error', 'Unknown error')}")
    except Exception as e:
        print(f"❌ Failed: {str(e)}")
    
    # Test queries
    print("\nTesting ResearchAgent queries...\n")
    queries = [
        ("Simple stock price", "What is Apple's current stock price?"),
        ("Market overview", "Give me an overview of today's market indices")
    ]
    
    for i, (title, query) in enumerate(queries, 1):
        print(f"Test {i}: {title}")
        try:
            result = await agent.run(query)
            if result["success"]:
                print(f"✅ Success!")
                print(f"📝 Response: {str(result['output'])[:100]}...")
                print(f"🔧 Used {len(result['intermediate_steps'])} steps")
            else:
                print(f"❌ Failed: {result['error']}")
        except Exception as e:
            print(f"❌ Error: {str(e)}")
        print()
    
    await agent.cleanup()

async def test_backtest_agent():
    print("🧪 Testing BacktestAgent...\n")
    
    # Clear cache
    cache_delete(get_cache_key("market_data", "SPY", "historical"))
    
    # Initialize BacktestAgent
    agent = BacktestAgent()
    await agent.initialize()
    
    print(f"✅ BacktestAgent initialized with {len(agent.agent_executor.tools)} tools\n")
    print("📋 Available tools:")
    for tool in agent.list_available_tools():
        print(f"   - {tool['name']}: {tool['description']}")
    print("\n")
    
    # Skip synthetic data test since we're using real data
    
    # Test historical data
    print("Testing historical data fetch for SPY:")
    try:
        result = await agent.run("Fetch historical data for SPY from 2024-01-01 to 2024-12-31")
        if result["success"] and "data" in result["output"]:
            print(f"✅ Success! Fetched {result['output']['data']['data_points']} data points")
        else:
            print(f"❌ Failed: {result.get('error', 'Unknown error')}")
    except Exception as e:
        print(f"❌ Failed: {str(e)}")
    
    # Test run_backtest
    print("\nTesting run_backtest:")
    try:
        db = next(get_db())
        strategy = Strategy(
            id=f"strategy_{uuid.uuid4().hex[:8]}",
            name="Momentum Test Strategy",
            strategy_type="momentum",
            instruments=["AAPL", "MSFT", "SPY"],  # Use real symbols
            entry_rules={"type": "momentum", "params": {"ma_window": 20}},
            exit_rules={"type": "stop_loss", "params": {"stop_loss_pct": 0.02}}
        )
        db.add(strategy)
        db.commit()
        
        start_date = datetime.now() - timedelta(days=365)
        end_date = datetime.now()
        result = await agent.run_backtest(strategy.id, start_date, end_date)
        backtest = db.query(BacktestResult).filter_by(id=result).first()
        if backtest and backtest.status == BacktestStatus.COMPLETED:
            print(f"✅ Success! Backtest ID: {result}, Final Value: {backtest.final_value}")
        else:
            print(f"❌ Failed: Backtest not completed")
        db.delete(strategy)
        db.commit()
    except Exception as e:
        print(f"❌ Failed: {str(e)}")
    finally:
        db.close()
    
    await agent.cleanup()

async def main():
    init_postgres()
    await test_research_agent()
    print("\n✅ ResearchAgent tests completed!\n")
    await test_backtest_agent()
    print("\n✅ All tests completed!")

if __name__ == "__main__":
    asyncio.run(main())