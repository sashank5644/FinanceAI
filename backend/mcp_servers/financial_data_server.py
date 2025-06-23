# mcp_servers/financial_data_server.py
"""MCP Server for financial data access."""

import logging
from typing import Dict, Any
import yfinance as yf
import requests
from datetime import datetime, timedelta
import time
import json

from mcp.server import MCPServer
from config import settings
from services.cache_service import cache_service

logger = logging.getLogger(__name__)

class FinancialDataMCPServer(MCPServer):
    """MCP Server providing financial data tools."""
    
    def __init__(self):
        if not settings.alpha_vantage_api_key:
            logger.error("Alpha Vantage API key is missing")
            raise ValueError("Alpha Vantage API key not configured")
        logger.info(f"Using Alpha Vantage API key: {settings.alpha_vantage_api_key[:4]}...")
        super().__init__(host="0.0.0.0", port=8081)
        self.register_financial_tools()
    
    def register_financial_tools(self):
        """Register all financial data tools."""
        
        # Stock quote tool
        self.register_tool("get_stock_quote", {
            "name": "Get Stock Quote",
            "description": "Get real-time stock quote data",
            "category": "financial_data",
            "parameters": {
                "symbol": {"type": "string", "required": True, "description": "Stock symbol"},
                "include_extended": {"type": "boolean", "default": False}
            },
            "handler": self.get_stock_quote,
            "capabilities": ["real-time", "cached"]
        })
        
        # Historical data tool
        self.register_tool("get_historical_data", {
            "name": "Get Historical Data",
            "description": "Fetch historical price data for analysis",
            "category": "financial_data",
            "parameters": {
                "symbol": {"type": "string", "required": True},
                "start_date": {"type": "string", "required": True, "format": "YYYY-MM-DD"},
                "end_date": {"type": "string", "required": True, "format": "YYYY-MM-DD"},
                "interval": {"type": "string", "default": "1d", "enum": ["1d", "1wk", "1mo"]}
            },
            "handler": self.get_historical_data,
            "capabilities": ["historical", "cached"]
        })
        
        # Market indices tool
        self.register_tool("get_market_indices", {
            "name": "Get Market Indices",
            "description": "Get major market index values",
            "category": "financial_data",
            "parameters": {},
            "handler": self.get_market_indices,
            "capabilities": ["real-time", "indices"]
        })
        
        # Company fundamentals tool
        self.register_tool("get_company_fundamentals", {
            "name": "Get Company Fundamentals",
            "description": "Fetch company fundamental data",
            "category": "financial_data",
            "parameters": {
                "symbol": {"type": "string", "required": True}
            },
            "handler": self.get_company_fundamentals,
            "capabilities": {"fundamentals": "cached"}
        })
        
        # Economic indicators tool
        self.register_tool("get_economic_indicators", {
            "name": "Get Economic Indicators",
            "description": "Fetch key economic indicators",
            "category": "financial_data",
            "parameters": {
                "indicator": {"type": "string", "required": True, 
                            "enum": ["GDP", "CPI", "UNEMPLOYMENT", "INTEREST_RATE"]}
            },
            "handler": self.get_economic_indicators,
            "capabilities": ["economic", "macro"]
        })
    
    async def get_stock_quote(self, symbol: str, include_extended: bool = False) -> Dict[str, Any]:
        """Get real-time stock quote."""
        try:
            # Try Alpha Vantage first if we have a key
            logger.info(f"Fetching quote for {symbol} from Alpha Vantage")
            url = "https://www.alphavantage.co/query"
            params = {
                "function": "GLOBAL_QUOTE",
                "symbol": symbol,
                "apikey": settings.alpha_vantage_api_key
            }
            
            start_time = time.time()
            response = requests.get(url, params=params, timeout=10)
            elapsed_time = time.time() - start_time
            logger.info(f"Alpha Vantage request for {symbol} took {elapsed_time:.2f} seconds")
            
            response.raise_for_status()
            try:
                data = response.json()
            except json.JSONDecodeError as e:
                logger.error(f"JSON decode error for {symbol}: {e}")
                return {"success": False, "error": "Invalid response from Alpha Vantage"}
            
            if "Global Quote" in data and data["Global Quote"]:
                quote = data["Global Quote"]
                quote_data = {
                    "symbol": symbol,
                    "price": float(quote.get("05. price", 0)),
                    "change": float(quote.get("09. change", 0)),
                    "change_percent": float(quote.get("10. change percent", "0%").replace("%", "")),
                    "volume": int(quote.get("06. volume", 0)),
                    "timestamp": datetime.utcnow().isoformat(),
                    "source": "alpha_vantage"
                }
                
                # Get company overview for market cap
                overview_params = {
                    "function": "OVERVIEW",
                    "symbol": symbol,
                    "apikey": settings.alpha_vantage_api_key
                }
                overview_start_time = time.time()
                overview_response = requests.get(url, params=overview_params, timeout=10)
                overview_elapsed_time = time.time() - overview_start_time
                logger.info(f"Alpha Vantage overview request for {symbol} took {overview_elapsed_time:.2f} seconds")
                
                try:
                    overview_data = overview_response.json()
                except json.JSONDecodeError as e:
                    logger.error(f"JSON decode error for {symbol}: {e}")
                    return {"success": False, "error": "Invalid overview response"}
                
                if "MarketCapitalization" in overview_data:
                    quote_data["market_cap"] = int(overview_data.get("MarketCapitalization", 0))
                    quote_data["pe_ratio"] = float(overview_data.get("PERatio", 0)) if overview_data.get("PERatio") != "None" else None
                
                # Cache the result
                cache_service.cache_quote(symbol, quote_data)
                
                # Respect Alpha Vantage rate limits (5 calls/minute)
                time.sleep(13)
                
                return {"success": True, "data": quote_data}
            
            logger.warning(f"No valid Alpha Vantage data for {symbol}, falling back to yfinance")
            
            # Fallback to yfinance
            ticker = yf.Ticker(symbol)
            start_time = time.time()
            try:
                info = ticker.info
            except Exception as e:
                logger.error(f"yfinance error for {symbol}: {e}")
                return {"success": False, "error": f"yfinance error: {str(e)}"}
            elapsed_time = time.time() - start_time
            logger.info(f"yfinance request for {symbol} took {elapsed_time:.2f} seconds")
            
            quote_data = {
                "symbol": symbol,
                "price": info.get("currentPrice", info.get("regularMarketPrice", 0)),
                "change": info.get("regularMarketChange", 0),
                "change_percent": info.get("regularMarketChangePercent", 0),
                "volume": info.get("volume", 0),
                "market_cap": info.get("marketCap", 0),
                "pe_ratio": info.get("trailingPE", None),
                "dividend_yield": info.get("dividendYield", None),
                "timestamp": datetime.utcnow().isoformat(),
                "source": "yfinance"
            }
            
            if include_extended:
                quote_data.update({
                    "pre_market": info.get("preMarketPrice", None),
                    "post_market": info.get("postMarketPrice", None),
                    "52_week_high": info.get("fiftyTwoWeekHigh", None),
                    "52_week_low": info.get("fiftyTwoWeekLow", None)
                })
            
            # Cache the result
            cache_service.cache_quote(symbol, quote_data)
            
            # Avoid yfinance rate limits
            time.sleep(1)
            
            return {"success": True, "data": quote_data}
            
        except requests.exceptions.RequestException as e:
            logger.error(f"Network error fetching quote for {symbol}: {e}")
            return {"success": False, "error": f"Network error: {str(e)}"}
        except Exception as e:
            logger.error(f"Error fetching quote for {symbol}: {e}")
            return {"success": False, "error": str(e)}
    
    async def get_historical_data(
        self, 
        symbol: str, 
        start_date: str, 
        end_date: str, 
        interval: str = "1d"
    ) -> Dict[str, Any]:
        """Get historical price data."""
        try:
            ticker = yf.Ticker(symbol)
            data = ticker.history(start=start_date, end=end_date, interval=interval)
            
            if data.empty:
                return {"success": False, "error": "No data available"}
            
            # Convert to list of records
            records = []
            for date, row in data.iterrows():
                records.append({
                    "date": date.isoformat(),
                    "open": float(row["Open"]),
                    "high": float(row["High"]),
                    "low": float(row["Low"]),
                    "close": float(row["Close"]),
                    "volume": int(row["Volume"])
                })
            
            return {
                "success": True,
                "data": {
                    "symbol": symbol,
                    "start_date": start_date,
                    "end_date": end_date,
                    "interval": interval,
                    "records": records,
                    "count": len(records)
                }
            }
            
        except Exception as e:
            logger.error(f"Error fetching historical data: {e}")
            return {"success": False, "error": str(e)}
    
    async def get_market_indices(self) -> Dict[str, Any]:
        """Get major market indices."""
        indices = {
            "^GSPC": "S&P 500",
            "^DJI": "Dow Jones",
            "^IXIC": "NASDAQ",
            "^VIX": "VIX"
        }
        
        result = {}
        
        # Try to get all at once using threading for parallel execution
        import concurrent.futures
        import yfinance as yf
        
        def fetch_index(symbol, name):
            try:
                ticker = yf.Ticker(symbol)
                history = ticker.history(period="2d")  # Get 2 days for comparison
                
                if not history.empty and len(history) >= 2:
                    latest = history.iloc[-1]
                    previous = history.iloc[-2]
                    return name, {
                        "value": float(latest["Close"]),
                        "change": float(latest["Close"] - previous["Close"]),
                        "change_percent": float((latest["Close"] - previous["Close"]) / previous["Close"] * 100)
                    }
            except Exception as e:
                logger.error(f"Error fetching {name}: {e}")
                return name, {"error": str(e)}
            return name, {"error": "No data"}
        
        # Use ThreadPoolExecutor for parallel fetching
        with concurrent.futures.ThreadPoolExecutor(max_workers=4) as executor:
            futures = {executor.submit(fetch_index, symbol, name): (symbol, name) 
                    for symbol, name in indices.items()}
            
            for future in concurrent.futures.as_completed(futures, timeout=10):
                try:
                    name, data = future.result()
                    result[name] = data
                except Exception as e:
                    symbol, name = futures[future]
                    result[name] = {"error": str(e)}
        
        return {"success": True, "data": result}
    
    async def get_company_fundamentals(self, symbol: str) -> Dict[str, Any]:
        """Get company fundamental data."""
        try:
            logger.info(f"Fetching fundamentals for {symbol}")
            ticker = yf.Ticker(symbol)
            start_time = time.time()
            info = ticker.info
            elapsed_time = time.time() - start_time
            logger.info(f"yfinance fundamentals request for {symbol} took {elapsed_time:.2f} seconds")
            
            fundamentals = {
                "symbol": symbol,
                "company_name": info.get("longName", ""),
                "sector": info.get("sector", ""),
                "industry": info.get("industry", ""),
                "market_cap": info.get("marketCap", 0),
                "pe_ratio": info.get("trailingPE", None),
                "forward_pe": info.get("forwardPE", None),
                "peg_ratio": info.get("pegRatio", None),
                "price_to_book": info.get("priceToBook", None),
                "revenue": info.get("totalRevenue", 0),
                "profit_margin": info.get("profitMargins", None),
                "operating_margin": info.get("operatingMargins", None),
                "roe": info.get("returnOnEquity", None),
                "debt_to_equity": info.get("debtToEquity", None),
                "current_ratio": info.get("currentRatio", None),
                "dividend_yield": info.get("dividendYield", None),
                "beta": info.get("beta", None)
            }
            
            # Avoid yfinance rate limits
            time.sleep(1)
            
            return {"success": True, "data": fundamentals}
            
        except Exception as e:
            logger.error(f"Error fetching fundamentals for {symbol}: {e}")
            return {"success": False, "error": str(e)}
    
    async def get_economic_indicators(self, indicator: str) -> Dict[str, Any]:
        """Get economic indicators (mock data for demo)."""
        # In production, connect to FRED API or similar
        mock_data = {
            "GDP": {"value": 25462.7, "change": 2.1, "unit": "billion USD"},
            "CPI": {"value": 310.3, "change": 3.7, "unit": "index"},
            "UNEMPLOYMENT": {"value": 3.7, "change": -0.1, "unit": "percent"},
            "INTEREST_RATE": {"value": 5.5, "change": 0.0, "unit": "percent"}
        }
        
        if indicator in mock_data:
            return {
                "success": True,
                "data": {
                    "indicator": indicator,
                    "current": mock_data[indicator],
                    "last_updated": datetime.utcnow().isoformat()
                }
            }
        else:
            return {"success": False, "error": f"Unknown indicator: {indicator}"}