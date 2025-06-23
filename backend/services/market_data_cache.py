"""Market data cache with fallback values."""

from datetime import datetime
from typing import Dict, Any

# Fallback market data (updated periodically)
MARKET_FALLBACK_DATA = {
    "indices": {
        "S&P 500": {
            "symbol": "^GSPC",
            "typical_range": "4000-5000",
            "description": "The S&P 500 is a market-cap-weighted index of 500 large US companies"
        },
        "NASDAQ": {
            "symbol": "^IXIC",
            "typical_range": "12000-16000",
            "description": "The NASDAQ Composite includes over 3,000 stocks listed on the NASDAQ exchange"
        },
        "DOW": {
            "symbol": "^DJI",
            "typical_range": "32000-38000",
            "description": "The Dow Jones Industrial Average tracks 30 large US companies"
        }
    },
    "market_cap_ranges": {
        "Small Cap": "Under $2 billion",
        "Mid Cap": "$2 billion - $10 billion",
        "Large Cap": "$10 billion - $200 billion",
        "Mega Cap": "Over $200 billion"
    },
    "mega_cap_examples": [
        {"symbol": "AAPL", "name": "Apple", "approx_market_cap": "$3 trillion"},
        {"symbol": "MSFT", "name": "Microsoft", "approx_market_cap": "$2.8 trillion"},
        {"symbol": "GOOGL", "name": "Alphabet", "approx_market_cap": "$1.7 trillion"},
        {"symbol": "AMZN", "name": "Amazon", "approx_market_cap": "$1.5 trillion"},
        {"symbol": "NVDA", "name": "NVIDIA", "approx_market_cap": "$1.2 trillion"}
    ]
}

def get_fallback_market_info() -> Dict[str, Any]:
    """Get fallback market information when APIs are unavailable."""
    return {
        "success": True,
        "source": "fallback_data",
        "data": MARKET_FALLBACK_DATA,
        "note": "Using general market information. For real-time data, please try again later.",
        "timestamp": datetime.now().isoformat()
    }
