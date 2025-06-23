"""Enhanced data fetching with multiple sources."""

import logging
from typing import Dict, Any, List, Optional
from datetime import datetime, timedelta
import yfinance as yf
import requests
from functools import lru_cache
import time

from config import settings
from utils.db.redis import cache_get, cache_set, get_cache_key

logger = logging.getLogger(__name__)


class EnhancedDataFetcher:
    """Enhanced data fetcher with multiple sources and fallbacks."""
    
    def __init__(self):
        self.alpha_vantage_key = settings.alpha_vantage_api_key
        self.news_api_key = settings.news_api_key
        self._last_yahoo_request = 0
        self._yahoo_delay = 1.0  # Delay between Yahoo requests
    
    def _rate_limit_yahoo(self):
        """Simple rate limiting for Yahoo Finance."""
        current_time = time.time()
        time_since_last = current_time - self._last_yahoo_request
        if time_since_last < self._yahoo_delay:
            time.sleep(self._yahoo_delay - time_since_last)
        self._last_yahoo_request = time.time()
    
    def get_yahoo_stock_data(self, symbol: str) -> Dict[str, Any]:
        """Get stock data from Yahoo Finance with better error handling."""
        try:
            # Check cache first
            cache_key = f"yahoo:{symbol}:quote"
            cached = cache_get(cache_key)
            if cached:
                logger.info(f"Using cached data for {symbol}")
                return cached
            
            # Apply rate limiting
            self._rate_limit_yahoo()
            
            # Clean up symbol (remove quotes if present)
            clean_symbol = symbol.strip().strip("'\"").upper()
            
            # Special handling for indices
            if clean_symbol in ["S&P 500", "S&P500", "SP500"]:
                clean_symbol = "^GSPC"
            elif clean_symbol == "NASDAQ":
                clean_symbol = "^IXIC"
            elif clean_symbol in ["DOW", "DOW JONES"]:
                clean_symbol = "^DJI"
            
            logger.info(f"Fetching Yahoo data for {clean_symbol}")
            
            # Fetch from Yahoo
            ticker = yf.Ticker(clean_symbol)
            
            # Get basic quote data first (faster, less likely to hit rate limits)
            fast_info = ticker.fast_info
            
            data = {
                "success": True,
                "source": "yahoo_finance",
                "data": {
                    "symbol": clean_symbol,
                    "name": clean_symbol,  # Will be updated if available
                    "price": float(fast_info.get('lastPrice', 0)),
                    "previousClose": float(fast_info.get('previousClose', 0)),
                    "change": float(fast_info.get('lastPrice', 0) - fast_info.get('previousClose', 0)),
                    "changePercent": ((fast_info.get('lastPrice', 0) - fast_info.get('previousClose', 0)) / fast_info.get('previousClose', 1) * 100) if fast_info.get('previousClose', 0) > 0 else 0,
                    "volume": int(fast_info.get('lastVolume', 0)),
                    "marketCap": int(fast_info.get('marketCap', 0)),
                    "dayHigh": float(fast_info.get('dayHigh', 0)),
                    "dayLow": float(fast_info.get('dayLow', 0)),
                    "52weekHigh": float(fast_info.get('fiftyTwoWeekHigh', 0)),
                    "52weekLow": float(fast_info.get('fiftyTwoWeekLow', 0))
                }
            }
            
            # Try to get additional info (but don't fail if rate limited)
            try:
                info = ticker.info
                if info:
                    data["data"]["name"] = info.get('longName', clean_symbol)
                    data["data"]["sector"] = info.get('sector', '')
                    data["data"]["industry"] = info.get('industry', '')
                    data["data"]["pe_ratio"] = float(info.get('trailingPE', 0))
                    data["data"]["dividend_yield"] = float(info.get('dividendYield', 0) * 100) if info.get('dividendYield') else 0
            except:
                # If info fails, just use what we have
                pass
            
            # Cache for 5 minutes
            cache_set(cache_key, data, expire=300)
            return data
            
        except Exception as e:
            logger.error(f"Yahoo Finance error for {symbol}: {e}")
            
            # Return a structured error response
            return {
                "success": False, 
                "error": f"Unable to fetch data for {symbol}. The symbol might be invalid or the service is temporarily unavailable.",
                "source": "yahoo_finance"
            }
    
    def get_index_data(self, index_symbol: str) -> Dict[str, Any]:
        """Get index data with proper symbol mapping."""
        # Enhanced index mapping
        index_map = {
            "S&P500": "^GSPC",
            "S&P 500": "^GSPC",
            "SP500": "^GSPC",
            "SPX": "^GSPC",
            "NASDAQ": "^IXIC",
            "NASDAQ COMPOSITE": "^IXIC",
            "DOW": "^DJI",
            "DOW JONES": "^DJI",
            "DJIA": "^DJI",
            "VIX": "^VIX",
            "VOLATILITY": "^VIX",
            "RUSSELL": "^RUT",
            "RUSSELL 2000": "^RUT",
            "RUSSELL2000": "^RUT"
        }
        
        # Clean and map the symbol
        clean_symbol = index_symbol.strip().upper()
        yahoo_symbol = index_map.get(clean_symbol, clean_symbol)
        
        logger.info(f"Fetching index data for {clean_symbol} -> {yahoo_symbol}")
        
        return self.get_yahoo_stock_data(yahoo_symbol)
    
    def get_market_summary(self) -> Dict[str, Any]:
        """Get overall market summary with better error handling."""
        try:
            # Check cache first
            cache_key = "market:summary"
            cached = cache_get(cache_key)
            if cached:
                return cached
            
            indices = {
                "S&P 500": "^GSPC",
                "NASDAQ": "^IXIC", 
                "DOW": "^DJI",
                "VIX": "^VIX"
            }
            
            summary = {}
            errors = []
            
            for name, symbol in indices.items():
                data = self.get_yahoo_stock_data(symbol)
                if data.get("success"):
                    summary[name] = {
                        "price": data["data"]["price"],
                        "change": data["data"]["change"],
                        "changePercent": round(data["data"]["changePercent"], 2),
                        "volume": data["data"]["volume"]
                    }
                else:
                    errors.append(f"{name}: {data.get('error', 'Unknown error')}")
            
            result = {
                "success": len(summary) > 0,
                "data": summary,
                "timestamp": datetime.now().isoformat()
            }
            
            if errors:
                result["errors"] = errors
            
            # Cache for 2 minutes if successful
            if result["success"]:
                cache_set(cache_key, result, expire=120)
            
            return result
            
        except Exception as e:
            logger.error(f"Market summary error: {e}")
            return {"success": False, "error": str(e)}
    
    def get_sector_performance(self) -> Dict[str, Any]:
        """Get sector performance data."""
        try:
            # Check cache
            cache_key = "market:sectors"
            cached = cache_get(cache_key)
            if cached:
                return cached
            
            # Major sector ETFs
            sectors = {
                "Technology": "XLK",
                "Healthcare": "XLV",
                "Financials": "XLF",
                "Energy": "XLE",
                "Consumer Discretionary": "XLY",
                "Industrials": "XLI",
                "Utilities": "XLU",
                "Real Estate": "XLRE",
                "Materials": "XLB",
                "Consumer Staples": "XLP"
            }
            
            performance = {}
            for sector, etf in sectors.items():
                data = self.get_yahoo_stock_data(etf)
                if data.get("success"):
                    performance[sector] = {
                        "change": round(data["data"]["changePercent"], 2),
                        "price": data["data"]["price"]
                    }
                
                # Add small delay to avoid rate limits
                time.sleep(0.5)
            
            result = {
                "success": True,
                "data": performance,
                "timestamp": datetime.now().isoformat()
            }
            
            # Cache for 5 minutes
            cache_set(cache_key, result, expire=300)
            
            return result
            
        except Exception as e:
            logger.error(f"Sector performance error: {e}")
            return {"success": False, "error": str(e)}


# Singleton instance
enhanced_fetcher = EnhancedDataFetcher()