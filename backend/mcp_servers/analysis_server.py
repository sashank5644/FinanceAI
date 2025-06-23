# mcp_servers/analysis_server.py
"""MCP Server for analysis and backtesting tools."""

import logging
from typing import Dict, Any, List
import pandas as pd
import numpy as np
from datetime import datetime, timedelta

from mcp.server import MCPServer
from services.backtest_engine import BacktestEngine
from services.strategy_service import strategy_service

logger = logging.getLogger(__name__)


class AnalysisMCPServer(MCPServer):
    """MCP Server providing analysis and backtesting tools."""
    
    def __init__(self):
        super().__init__(host="0.0.0.0", port=8083)
        self.register_analysis_tools()
        self.backtest_engine = BacktestEngine()
    
    def register_analysis_tools(self):
        """Register all analysis tools."""
        
        # Technical analysis tool
        self.register_tool("calculate_technical_indicators", {
            "name": "Calculate Technical Indicators",
            "description": "Calculate technical indicators for a stock",
            "category": "analysis",
            "parameters": {
                "symbol": {"type": "string", "required": True},
                "indicators": {"type": "array", "items": {"type": "string"}, 
                             "default": ["SMA", "RSI", "MACD"]}
            },
            "handler": self.calculate_technical_indicators,
            "capabilities": ["technical", "analysis"]
        })
        
        # Risk analysis tool
        self.register_tool("analyze_risk_metrics", {
            "name": "Analyze Risk Metrics",
            "description": "Calculate risk metrics for a portfolio or stock",
            "category": "analysis",
            "parameters": {
                "symbols": {"type": "array", "items": {"type": "string"}, "required": True},
                "period": {"type": "integer", "default": 252}
            },
            "handler": self.analyze_risk_metrics,
            "capabilities": ["risk", "analysis"]
        })
        
        # Performance analysis
        self.register_tool("analyze_performance", {
            "name": "Analyze Performance",
            "description": "Analyze historical performance metrics",
            "category": "analysis",
            "parameters": {
                "symbol": {"type": "string", "required": True},
                "benchmark": {"type": "string", "default": "SPY"},
                "period": {"type": "string", "default": "1y"}
            },
            "handler": self.analyze_performance,
            "capabilities": ["performance", "analysis"]
        })
        
        # Correlation analysis
        self.register_tool("analyze_correlation", {
            "name": "Analyze Correlation",
            "description": "Calculate correlation between assets",
            "category": "analysis",
            "parameters": {
                "symbols": {"type": "array", "items": {"type": "string"}, "required": True},
                "period": {"type": "string", "default": "6m"}
            },
            "handler": self.analyze_correlation,
            "capabilities": ["correlation", "analysis"]
        })
        
        # Simple backtest tool
        self.register_tool("run_simple_backtest", {
            "name": "Run Simple Backtest",
            "description": "Run a simple strategy backtest",
            "category": "analysis",
            "parameters": {
                "strategy_type": {"type": "string", "required": True,
                                "enum": ["momentum", "mean_reversion", "buy_hold"]},
                "symbol": {"type": "string", "required": True},
                "start_date": {"type": "string", "required": True},
                "end_date": {"type": "string", "required": True}
            },
            "handler": self.run_simple_backtest,
            "capabilities": ["backtest", "analysis"]
        })
    
    async def calculate_technical_indicators(
        self,
        symbol: str,
        indicators: List[str] = ["SMA", "RSI", "MACD"]
    ) -> Dict[str, Any]:
        """Calculate technical indicators."""
        try:
            import yfinance as yf
            
            # Fetch data
            ticker = yf.Ticker(symbol)
            data = ticker.history(period="3mo")
            
            if data.empty:
                return {"success": False, "error": "No data available"}
            
            results = {}
            
            # Simple Moving Average
            if "SMA" in indicators:
                data["SMA_20"] = data["Close"].rolling(window=20).mean()
                data["SMA_50"] = data["Close"].rolling(window=50).mean()
                results["SMA"] = {
                    "SMA_20": float(data["SMA_20"].iloc[-1]) if not pd.isna(data["SMA_20"].iloc[-1]) else None,
                    "SMA_50": float(data["SMA_50"].iloc[-1]) if not pd.isna(data["SMA_50"].iloc[-1]) else None,
                    "trend": "bullish" if data["Close"].iloc[-1] > data["SMA_20"].iloc[-1] else "bearish"
                }
            
            # RSI
            if "RSI" in indicators:
                delta = data["Close"].diff()
                gain = (delta.where(delta > 0, 0)).rolling(window=14).mean()
                loss = (-delta.where(delta < 0, 0)).rolling(window=14).mean()
                rs = gain / loss
                rsi = 100 - (100 / (1 + rs))
                results["RSI"] = {
                    "value": float(rsi.iloc[-1]) if not pd.isna(rsi.iloc[-1]) else None,
                    "signal": "oversold" if rsi.iloc[-1] < 30 else "overbought" if rsi.iloc[-1] > 70 else "neutral"
                }
            
            # MACD
            if "MACD" in indicators:
                exp1 = data["Close"].ewm(span=12, adjust=False).mean()
                exp2 = data["Close"].ewm(span=26, adjust=False).mean()
                macd = exp1 - exp2
                signal = macd.ewm(span=9, adjust=False).mean()
                results["MACD"] = {
                    "macd": float(macd.iloc[-1]) if not pd.isna(macd.iloc[-1]) else None,
                    "signal": float(signal.iloc[-1]) if not pd.isna(signal.iloc[-1]) else None,
                    "histogram": float(macd.iloc[-1] - signal.iloc[-1]) if not pd.isna(macd.iloc[-1]) else None,
                    "trend": "bullish" if macd.iloc[-1] > signal.iloc[-1] else "bearish"
                }
            
            return {
                "success": True,
                "data": {
                    "symbol": symbol,
                    "indicators": results,
                    "last_price": float(data["Close"].iloc[-1]),
                    "timestamp": datetime.utcnow().isoformat()
                }
            }
            
        except Exception as e:
            logger.error(f"Error calculating indicators: {e}")
            return {"success": False, "error": str(e)}
    
    async def analyze_risk_metrics(
        self,
        symbols: List[str],
        period: int = 252
    ) -> Dict[str, Any]:
        """Analyze risk metrics."""
        try:
            import yfinance as yf
            
            # Fetch data for all symbols
            data = yf.download(symbols, period="1y", progress=False)["Close"]
            
            if data.empty:
                return {"success": False, "error": "No data available"}
            
            # Calculate returns
            returns = data.pct_change().dropna()
            
            # Risk metrics
            results = {}
            for symbol in symbols:
                if symbol in returns.columns:
                    symbol_returns = returns[symbol]
                    results[symbol] = {
                        "volatility": float(symbol_returns.std() * np.sqrt(252)),
                        "var_95": float(np.percentile(symbol_returns, 5)),
                        "max_drawdown": float((symbol_returns + 1).cumprod().div((symbol_returns + 1).cumprod().cummax()).min() - 1),
                        "sharpe_ratio": float((symbol_returns.mean() * 252) / (symbol_returns.std() * np.sqrt(252))) if symbol_returns.std() > 0 else 0
                    }
            
            # Portfolio metrics if multiple symbols
            if len(symbols) > 1:
                portfolio_returns = returns.mean(axis=1)
                results["portfolio"] = {
                    "volatility": float(portfolio_returns.std() * np.sqrt(252)),
                    "correlation_matrix": returns.corr().to_dict(),
                    "diversification_ratio": float(returns.std().mean() / portfolio_returns.std()) if portfolio_returns.std() > 0 else 1
                }
            
            return {"success": True, "data": results}
            
        except Exception as e:
            logger.error(f"Error analyzing risk: {e}")
            return {"success": False, "error": str(e)}
    
    async def analyze_performance(
        self,
        symbol: str,
        benchmark: str = "SPY",
        period: str = "1y"
    ) -> Dict[str, Any]:
        """Analyze performance metrics."""
        try:
            import yfinance as yf
            
            # Fetch data
            data = yf.download([symbol, benchmark], period=period, progress=False)["Close"]
            
            if data.empty:
                return {"success": False, "error": "No data available"}
            
            # Calculate returns
            symbol_returns = data[symbol].pct_change().dropna()
            benchmark_returns = data[benchmark].pct_change().dropna()
            
            # Performance metrics
            total_return = (data[symbol].iloc[-1] / data[symbol].iloc[0] - 1)
            benchmark_return = (data[benchmark].iloc[-1] / data[benchmark].iloc[0] - 1)
            
            # Calculate beta
            covariance = symbol_returns.cov(benchmark_returns)
            benchmark_variance = benchmark_returns.var()
            beta = covariance / benchmark_variance if benchmark_variance > 0 else 1
            
            # Calculate alpha (simplified)
            alpha = (total_return - benchmark_return * beta) * 100
            
            return {
                "success": True,
                "data": {
                    "symbol": symbol,
                    "benchmark": benchmark,
                    "period": period,
                    "total_return": float(total_return),
                    "benchmark_return": float(benchmark_return),
                    "excess_return": float(total_return - benchmark_return),
                    "beta": float(beta),
                    "alpha": float(alpha),
                    "tracking_error": float((symbol_returns - benchmark_returns).std() * np.sqrt(252)),
                    "information_ratio": float((total_return - benchmark_return) / ((symbol_returns - benchmark_returns).std() * np.sqrt(252))) if (symbol_returns - benchmark_returns).std() > 0 else 0
                }
            }
            
        except Exception as e:
            logger.error(f"Error analyzing performance: {e}")
            return {"success": False, "error": str(e)}
    
    async def analyze_correlation(
        self,
        symbols: List[str],
        period: str = "6m"
    ) -> Dict[str, Any]:
        """Analyze correlation between assets."""
        try:
            import yfinance as yf
            
            # Fetch data
            data = yf.download(symbols, period=period, progress=False)["Close"]
            
            if data.empty:
                return {"success": False, "error": "No data available"}
            
            # Calculate correlation
            correlation_matrix = data.corr()
            
            # Find highest and lowest correlations
            correlations = []
            for i in range(len(symbols)):
                for j in range(i+1, len(symbols)):
                    correlations.append({
                        "pair": f"{symbols[i]}-{symbols[j]}",
                        "correlation": float(correlation_matrix.iloc[i, j])
                    })
            
            correlations.sort(key=lambda x: abs(x["correlation"]), reverse=True)
            
            return {
                "success": True,
                "data": {
                    "correlation_matrix": correlation_matrix.to_dict(),
                    "highest_correlation": correlations[0] if correlations else None,
                    "lowest_correlation": correlations[-1] if correlations else None,
                    "average_correlation": float(correlation_matrix.values[np.triu_indices_from(correlation_matrix.values, k=1)].mean())
                }
            }
            
        except Exception as e:
            logger.error(f"Error analyzing correlation: {e}")
            return {"success": False, "error": str(e)}
    
    async def run_simple_backtest(
        self,
        strategy_type: str,
        symbol: str,
        start_date: str,
        end_date: str
    ) -> Dict[str, Any]:
        """Run a simple backtest."""
        try:
            # This would use the backtest engine
            # For now, return mock results
            return {
                "success": True,
                "data": {
                    "strategy": strategy_type,
                    "symbol": symbol,
                    "period": f"{start_date} to {end_date}",
                    "total_return": 15.2,
                    "sharpe_ratio": 1.2,
                    "max_drawdown": -8.5,
                    "win_rate": 58.3,
                    "total_trades": 42,
                    "summary": f"The {strategy_type} strategy would have generated a 15.2% return"
                }
            }
            
        except Exception as e:
            logger.error(f"Error running backtest: {e}")
            return {"success": False, "error": str(e)}