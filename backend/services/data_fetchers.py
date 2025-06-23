"""Data fetching services for financial data."""

import logging
from typing import Dict, Any, List, Optional
from datetime import datetime, timedelta
import requests

from config import settings
from utils.db.redis import cache_get, cache_set, get_cache_key

logger = logging.getLogger(__name__)


class AlphaVantageService:
    """Service for fetching data from Alpha Vantage."""
    
    def __init__(self):
        self.api_key = settings.alpha_vantage_api_key
        self.base_url = "https://www.alphavantage.co/query"
    
    def get_stock_data(
        self, 
        symbol: str, 
        function: str = "TIME_SERIES_DAILY"
    ) -> Dict[str, Any]:
        """Get stock data from Alpha Vantage."""
        # Check cache first
        cache_key = get_cache_key("market_data", symbol, function)
        cached_data = cache_get(cache_key)
        if cached_data:
            return cached_data
        
        # Fetch from API
        params = {
            "function": function,
            "symbol": symbol,
            "apikey": self.api_key,
            "outputsize": "compact"
        }
        
        try:
            response = requests.get(self.base_url, params=params)
            response.raise_for_status()
            data = response.json()
            
            # Cache for 5 minutes
            cache_set(cache_key, data, expire=300)
            
            return data
        except Exception as e:
            logger.error(f"Failed to fetch stock data for {symbol}: {e}")
            raise
    
    def get_company_overview(self, symbol: str) -> Dict[str, Any]:
        """Get company overview data."""
        return self.get_stock_data(symbol, "OVERVIEW")


class NewsAPIService:
    """Service for fetching financial news."""
    
    def __init__(self):
        self.api_key = settings.news_api_key
        self.base_url = "https://newsapi.org/v2"
    
    def search_news(
        self, 
        query: str, 
        days_back: int = 7,
        language: str = "en"
    ) -> List[Dict[str, Any]]:
        """Search for news articles."""
        # Check cache
        cache_key = get_cache_key("news", query, str(days_back))
        cached_data = cache_get(cache_key)
        if cached_data:
            return cached_data
        
        # Calculate date range
        to_date = datetime.utcnow()
        from_date = to_date - timedelta(days=days_back)
        
        params = {
            "q": query,
            "from": from_date.isoformat(),
            "to": to_date.isoformat(),
            "language": language,
            "sortBy": "relevancy",
            "apiKey": self.api_key
        }
        
        try:
            response = requests.get(f"{self.base_url}/everything", params=params)
            response.raise_for_status()
            data = response.json()
            
            articles = data.get("articles", [])
            
            # Cache for 1 hour
            cache_set(cache_key, articles, expire=3600)
            
            return articles
        except Exception as e:
            logger.error(f"Failed to fetch news for {query}: {e}")
            raise
