# agents/backtest_agent.py
"""Backtest agent for strategy evaluation."""

import logging
from typing import List, Dict, Any, Optional
from datetime import datetime, timedelta
import uuid
import pandas as pd
import numpy as np
import json
import requests

from langchain.tools import Tool

from .base_agent import BaseAgent
from models.strategy_models import Strategy
from models.backtest_models import BacktestResult, BacktestStatus
from config import settings
from utils.db import get_db
from utils.db.redis import cache_get, cache_set, cache_exists, cache_delete, get_cache_key

logger = logging.getLogger(__name__)

class BacktestAgent(BaseAgent):
    """Agent for backtesting investment strategies."""
    
    def __init__(self, mcp_servers: Optional[List[str]] = None):
        super().__init__(
            name="BacktestAgent",
            description="Tests investment strategies against historical data",
            model_name="gemini-1.5-flash",
            mcp_servers=mcp_servers or settings.mcp_servers
        )
    
    def get_system_prompt(self) -> str:
        """System prompt for backtest agent."""
        return """You are a quantitative analyst specializing in backtesting trading strategies.

Your role:
1. Explain backtesting results
2. Highlight performance metrics
3. Identify strategy issues
4. Suggest improvements
5. Compare to benchmarks

Key metrics:
- Returns: Total, annualized
- Risk: Volatility, max drawdown
- Efficiency: Sharpe ratio
- Trading: Win rate, total trades"""
    
    async def get_custom_tools(self) -> List[Tool]:
        """Get backtest-specific tools."""
        
        def fetch_historical_data(params: Any) -> Dict[str, Any]:
            """Fetch historical price data for backtesting."""
            cache_key = None
            try:
                # Handle string input (e.g., JSON string from agent executor)
                if isinstance(params, str):
                    params = json.loads(params)
                
                symbol = params.get('ticker', '') or params.get('symbol', '')
                start_date = params.get('start_date', '')
                end_date = params.get('end_date', '')
                
                if not all([symbol, start_date, end_date]):
                    return {"success": False, "error": "Missing parameters"}
                
                cache_key = get_cache_key("market_data", symbol, "historical")
                if cache_exists(cache_key):
                    cached = cache_get(cache_key)
                    return cached
                
                # Fetch data from Alpha Vantage
                api_key = settings.alpha_vantage_api_key
                url = f"https://www.alphavantage.co/query?function=TIME_SERIES_DAILY_ADJUSTED&symbol={symbol}&outputsize=full&apikey={api_key}"
                response = requests.get(url)
                data = response.json()
                
                if "Time Series (Daily)" not in data:
                    return {"success": False, "error": f"API error: {data.get('Error Message', 'Unknown error')}"}
                
                # Convert to DataFrame
                time_series = data["Time Series (Daily)"]
                df = pd.DataFrame.from_dict(time_series, orient='index', dtype=float)
                df.index = pd.to_datetime(df.index)
                df = df.loc[start_date:end_date][['4. close', '1. open', '2. high', '3. low', '6. volume']]
                df.columns = ['Close', 'Open', 'High', 'Low', 'Volume']
                
                # Prepare response
                price_data = {
                    "symbol": symbol,
                    "start_date": start_date,
                    "end_date": end_date,
                    "data_points": len(df),
                    "columns": list(df.columns),
                    "summary": {
                        "first_close": float(df['Close'].iloc[-1]),
                        "last_close": float(df['Close'].iloc[0]),
                        "min_price": float(df['Low'].min()),
                        "max_price": float(df['High'].max()),
                        "total_return": float((df['Close'].iloc[0] / df['Close'].iloc[-1] - 1) * 100)
                    }
                }
                
                result = {"success": True, "data": price_data}
                cache_set(cache_key, result, expire=86400)
                return result
                
            except Exception as e:
                logger.error(f"Error fetching data: {e}")
                if cache_key:
                    cache_delete(cache_key)
                return {"success": False, "error": str(e)}
        
        def analyze_strategy_robustness(
            strategy_id: str,
            backtest_results: Dict[str, Any]
        ) -> Dict[str, Any]:
            """Analyze strategy robustness."""
            metrics = backtest_results.get("metrics", {})
            
            robustness_score = 0
            issues = []
            strengths = []
            
            sharpe = metrics.get("sharpe_ratio", 0)
            if sharpe > 1.5:
                robustness_score += 25
                strengths.append("Excellent risk-adjusted returns")
            elif sharpe > 0.75:
                robustness_score += 15
                strengths.append("Good risk-adjusted returns")
            else:
                issues.append("Low Sharpe ratio")
            
            win_rate = metrics.get("win_rate", 0)
            if win_rate > 55:
                robustness_score += 20
                strengths.append("High win rate")
            elif win_rate < 45:
                issues.append("Low win rate")
            
            max_dd = abs(metrics.get("max_drawdown", 0))
            if max_dd < 10:
                robustness_score += 25
                strengths.append("Low max drawdown")
            elif max_dd > 25:
                issues.append("High max drawdown")
            
            total_trades = metrics.get("total_trades", 0)
            if total_trades < 20:
                issues.append("Too few trades")
            elif total_trades > 200:
                robustness_score += 10
                strengths.append("Large trade sample")
            
            return {
                "success": True,
                "robustness_score": robustness_score,
                "grade": "A" if robustness_score > 70 else "B" if robustness_score > 50 else "C" if robustness_score > 30 else "D",
                "strengths": strengths,
                "issues": issues,
                "recommendations": ["Test different periods", "Add position sizing", "Consider costs"]
            }
        
        def compare_to_benchmark(
            strategy_metrics: Dict[str, Any]
        ) -> Dict[str, Any]:
            """Compare strategy to benchmark."""
            try:
                benchmark_annual_return = 10
                benchmark_volatility = 15
                benchmark_sharpe = 0.5
                
                strategy_return = strategy_metrics.get("annualized_return", 0)
                strategy_vol = strategy_metrics.get("volatility", 0)
                strategy_sharpe = strategy_metrics.get("sharpe_ratio", 0)
                
                return {
                    "success": True,
                    "comparison": {
                        "excess_return": round(strategy_return - benchmark_annual_return, 2),
                        "relative_volatility": round(strategy_vol / max(1, benchmark_volatility), 2),
                        "sharpe_difference": round(strategy_sharpe - benchmark_sharpe, 2),
                        "outperformance": strategy_return > benchmark_annual_return,
                        "risk_adjusted_outperformance": strategy_sharpe > benchmark_sharpe
                    },
                    "summary": f"Strategy {'outperforms' if strategy_return > benchmark_annual_return else 'underperforms'} benchmark"
                }
                
            except Exception as e:
                logger.error(f"Error comparing benchmark: {e}")
                return {"success": False, "error": str(e)}
        
        return [
            Tool(
                name="fetch_historical_data",
                func=fetch_historical_data,
                description="Fetch historical price data."
            ),
            Tool(
                name="analyze_strategy_robustness",
                func=analyze_strategy_robustness,
                description="Analyze strategy robustness."
            ),
            Tool(
                name="compare_to_benchmark",
                func=compare_to_benchmark,
                description="Compare strategy to benchmark."
            )
        ]
    
    def _to_dict(self, obj: Any) -> Any:
        """Convert objects to JSON-serializable format."""
        if isinstance(obj, pd.Timestamp):
            return obj.isoformat()
        elif isinstance(obj, list):
            return [self._to_dict(item) for item in obj]
        elif isinstance(obj, dict):
            return {key: self._to_dict(value) for key, value in obj.items()}
        return obj
    
    async def run_backtest(
        self,
        strategy_id: str,
        start_date: datetime,
        end_date: datetime,
        initial_capital: float = 100000
    ) -> str:
        """Run a backtest for a strategy."""
        db = next(get_db())
        backtest_id = f"backtest_{uuid.uuid4().hex[:8]}"
        
        try:
            strategy = db.query(Strategy).filter_by(id=strategy_id).first()
            if not strategy:
                raise ValueError(f"Strategy {strategy_id} not found")
            
            if not strategy.instruments:
                strategy.instruments = ["DEMO1", "DEMO2", "DEMO3"]
                logger.info(f"Using default instruments: {strategy.instruments}")
            
            backtest = BacktestResult(
                id=backtest_id,
                strategy_id=strategy_id,
                start_date=start_date,
                end_date=end_date,
                initial_capital=initial_capital,
                status=BacktestStatus.RUNNING,
                benchmark_symbol="SPY"
            )
            db.add(backtest)
            db.commit()
            
            # Fetch real data from Alpha Vantage
            symbols = strategy.instruments[:3]
            all_data = pd.DataFrame()
            for symbol in symbols:
                url = f"https://www.alphavantage.co/query?function=TIME_SERIES_DAILY_ADJUSTED&symbol={symbol}&outputsize=full&apikey={settings.alpha_vantage_api_key}"
                response = requests.get(url)
                data = response.json()
                
                if "Time Series (Daily)" not in data:
                    logger.warning(f"No data for {symbol}: {data.get('Error Message', 'Unknown error')}")
                    continue
                
                df = pd.DataFrame.from_dict(data["Time Series (Daily)"], orient='index', dtype=float)
                df.index = pd.to_datetime(df.index)
                df = df.loc[start_date:end_date][['4. close', '1. open', '2. high', '3. low', '6. volume']]
                df.columns = [f"{symbol}_Close", f"{symbol}_Open", f"{symbol}_High", f"{symbol}_Low", f"{symbol}_Volume"]
                all_data = all_data.join(df, how='outer') if not all_data.empty else df
            
            if all_data.empty:
                raise ValueError("No data available for backtest")
            
            strategy_dict = {
                "type": strategy.strategy_type.value if strategy.strategy_type else "momentum",
                "instruments": symbols,
                "rules": strategy.entry_rules or {}
            }
            
            results = self._run_simple_backtest(
                strategy_dict,
                all_data,
                initial_capital
            )
            
            backtest.status = BacktestStatus.COMPLETED
            backtest.completed_at = datetime.utcnow()
            
            metrics = results.get("metrics", {})
            backtest.final_value = metrics.get("final_value", initial_capital)
            backtest.total_return = metrics.get("total_return", 0)
            backtest.annualized_return = metrics.get("annualized_return", 0)
            backtest.volatility = metrics.get("volatility", 0)
            backtest.sharpe_ratio = metrics.get("sharpe_ratio", 0)
            backtest.max_drawdown = metrics.get("max_drawdown", 0)
            backtest.total_trades = metrics.get("total_trades", 0)
            backtest.win_rate = metrics.get("win_rate", 0)
            
            backtest.equity_curve = results.get("equity_curve", [])
            backtest.trades = self._to_dict(results.get("trades", []))  # Serialize trades for DB
            
            cache_key = get_cache_key("backtest", backtest_id)
            serialized_results = self._to_dict(results)
            cache_set(cache_key, serialized_results, expire=86400)
            db.commit()
            
            logger.info(f"Backtest {backtest_id} completed successfully")
            return backtest_id
            
        except Exception as e:
            logger.error(f"Backtest failed: {e}")
            if 'backtest' in locals():
                backtest.status = BacktestStatus.FAILED
                backtest.error_message = str(e)
                db.commit()
            raise
            
        finally:
            db.close()
    
    def _run_simple_backtest(
        self,
        strategy: Dict[str, Any],
        data: pd.DataFrame,
        initial_capital: float
    ) -> Dict[str, Any]:
        """Run a simple momentum backtest."""
        capital = initial_capital
        positions = {}
        trades = []
        equity_curve = [initial_capital]
        
        for i in range(20, len(data)):
            date = data.index[i]
            
            for symbol in strategy["instruments"]:
                close_col = f"{symbol}_Close"
                if close_col not in data.columns:
                    continue
                
                current_price = data[close_col].iloc[i]
                ma_20 = data[close_col].iloc[i-20:i].mean()
                
                if symbol not in positions and current_price > ma_20 * 1.02:
                    position_size = capital * 0.2
                    if capital >= position_size:
                        shares = position_size / current_price
                        positions[symbol] = {
                            "shares": shares,
                            "entry_price": current_price,
                            "entry_date": date
                        }
                        capital -= position_size
                
                elif symbol in positions and current_price < ma_20 * 0.98:
                    position = positions[symbol]
                    exit_value = position["shares"] * current_price
                    pnl = exit_value - (position["shares"] * position["entry_price"])
                    
                    trades.append({
                        "symbol": symbol,
                        "entry_date": position["entry_date"],
                        "exit_date": date,
                        "entry_price": position["entry_price"],
                        "exit_price": current_price,
                        "pnl": pnl,
                        "return_pct": (current_price / position["entry_price"] - 1) * 100
                    })
                    
                    capital += exit_value
                    del positions[symbol]
            
            portfolio_value = capital
            for symbol, position in positions.items():
                close_col = f"{symbol}_Close"
                if close_col in data.columns:
                    portfolio_value += position["shares"] * data[close_col].iloc[i]
            
            equity_curve.append(portfolio_value)
        
        returns = [(equity_curve[i] - equity_curve[i-1]) / equity_curve[i-1] 
                  for i in range(1, len(equity_curve))]
        
        total_return = (equity_curve[-1] - initial_capital) / initial_capital * 100
        
        winning_trades = [t for t in trades if t["pnl"] > 0]
        win_rate = len(winning_trades) / len(trades) * 100 if trades else 0
        
        return {
            "metrics": {
                "final_value": equity_curve[-1],
                "total_return": total_return,
                "annualized_return": total_return * 252 / len(data) if len(data) > 0 else 0,
                "volatility": pd.Series(returns).std() * (252 ** 0.5) * 100 if returns else 0,
                "sharpe_ratio": (total_return / 100) / (pd.Series(returns).std() * (252 ** 0.5)) if returns and pd.Series(returns).std() > 0 else 0,
                "max_drawdown": self._calculate_max_drawdown(equity_curve),
                "total_trades": len(trades),
                "win_rate": win_rate
            },
            "trades": trades,
            "equity_curve": equity_curve
        }
    
    def _calculate_max_drawdown(self, equity_curve: List[float]) -> float:
        """Calculate maximum drawdown."""
        if len(equity_curve) < 2:
            return 0
        
        peak = equity_curve[0]
        max_dd = 0
        
        for value in equity_curve[1:]:
            if value > peak:
                peak = value
            drawdown = (peak - value) / peak * 100
            max_dd = max(max_dd, drawdown)
        
        return -max_dd