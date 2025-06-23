"""Service for managing financial data cache."""

import logging
from typing import Dict, Any, List, Optional
from datetime import datetime, timedelta
from sqlalchemy import and_, or_, desc

from models.cache_models import MarketDataCache, NewsCache, MarketSnapshot
from utils.db import get_db
from services.enhanced_data_fetcher import enhanced_fetcher

logger = logging.getLogger(__name__)


class CacheService:
    """Service for caching and retrieving financial data."""
    
    def __init__(self):
        self.cache_duration = {
            'quote': timedelta(minutes=5),
            'company': timedelta(hours=24),
            'index': timedelta(minutes=5),
            'news': timedelta(hours=1)
        }
    
    def get_cached_quote(self, symbol: str) -> Optional[Dict[str, Any]]:
        """Get cached quote data if fresh enough."""
        db = next(get_db())
        try:
            # Look for recent cache entry
            cutoff_time = datetime.utcnow() - self.cache_duration['quote']
            
            cache_entry = db.query(MarketDataCache).filter(
                and_(
                    MarketDataCache.symbol == symbol.upper(),
                    MarketDataCache.data_type == 'quote',
                    MarketDataCache.updated_at >= cutoff_time
                )
            ).order_by(desc(MarketDataCache.updated_at)).first()
            
            if cache_entry:
                logger.info(f"Cache hit for {symbol}")
                return {
                    "success": True,
                    "source": f"cache_{cache_entry.source}",
                    "data": {
                        "symbol": cache_entry.symbol,
                        "price": cache_entry.price,
                        "change": cache_entry.change,
                        "change_percent": cache_entry.change_percent,
                        "volume": cache_entry.volume,
                        "high": cache_entry.high,
                        "low": cache_entry.low,
                        "market_cap": cache_entry.market_cap,
                        "updated_at": cache_entry.updated_at.isoformat()
                    },
                    "cached": True
                }
            
            return None
            
        except Exception as e:
            logger.error(f"Cache retrieval error: {e}")
            return None
        finally:
            db.close()
    
    def cache_quote(self, symbol: str, data: Dict[str, Any], source: str):
        """Cache quote data."""
        db = next(get_db())
        try:
            # Check if entry exists
            existing = db.query(MarketDataCache).filter(
                and_(
                    MarketDataCache.symbol == symbol.upper(),
                    MarketDataCache.data_type == 'quote'
                )
            ).first()
            
            quote_data = data.get('data', {})
            
            if existing:
                # Update existing entry
                existing.price = quote_data.get('price')
                existing.change = quote_data.get('change')
                existing.change_percent = quote_data.get('changePercent', quote_data.get('change_percent'))
                existing.volume = quote_data.get('volume')
                existing.high = quote_data.get('high', quote_data.get('dayHigh'))
                existing.low = quote_data.get('low', quote_data.get('dayLow'))
                existing.market_cap = quote_data.get('marketCap', quote_data.get('market_cap'))
                existing.data_json = data
                existing.source = source
                existing.data_timestamp = datetime.utcnow()
            else:
                # Create new entry
                cache_entry = MarketDataCache(
                    symbol=symbol.upper(),
                    data_type='quote',
                    price=quote_data.get('price'),
                    change=quote_data.get('change'),
                    change_percent=quote_data.get('changePercent', quote_data.get('change_percent')),
                    volume=quote_data.get('volume'),
                    high=quote_data.get('high', quote_data.get('dayHigh')),
                    low=quote_data.get('low', quote_data.get('dayLow')),
                    market_cap=quote_data.get('marketCap', quote_data.get('market_cap')),
                    data_json=data,
                    source=source,
                    data_timestamp=datetime.utcnow()
                )
                db.add(cache_entry)
            
            db.commit()
            logger.info(f"Cached quote for {symbol}")
            
        except Exception as e:
            logger.error(f"Cache storage error: {e}")
            db.rollback()
        finally:
            db.close()
    
    def get_market_snapshot(self, date: Optional[datetime] = None) -> Optional[Dict[str, Any]]:
        """Get market snapshot for a specific date."""
        db = next(get_db())
        try:
            if not date:
                date = datetime.utcnow().date()
            
            snapshot = db.query(MarketSnapshot).filter(
                MarketSnapshot.snapshot_date == date
            ).first()
            
            if snapshot:
                return {
                    "date": snapshot.snapshot_date.isoformat(),
                    "indices": {
                        "sp500": snapshot.sp500,
                        "nasdaq": snapshot.nasdaq,
                        "dow": snapshot.dow,
                        "vix": snapshot.vix
                    },
                    "market_breadth": {
                        "advancing": snapshot.advancing_stocks,
                        "declining": snapshot.declining_stocks
                    },
                    "sector_performance": snapshot.sector_performance,
                    "top_movers": {
                        "gainers": snapshot.top_gainers,
                        "losers": snapshot.top_losers,
                        "most_active": snapshot.most_active
                    }
                }
            
            return None
            
        except Exception as e:
            logger.error(f"Snapshot retrieval error: {e}")
            return None
        finally:
            db.close()
    
    def create_daily_snapshot(self):
        """Create a daily market snapshot."""
        logger.info("Creating daily market snapshot...")
        
        db = next(get_db())
        try:
            # Check if today's snapshot exists
            today = datetime.utcnow().date()
            existing = db.query(MarketSnapshot).filter(
                MarketSnapshot.snapshot_date == today
            ).first()
            
            if existing:
                logger.info("Today's snapshot already exists")
                return
            
            # Gather market data
            market_data = enhanced_fetcher.get_market_summary()
            sector_data = enhanced_fetcher.get_sector_performance()
            
            if market_data.get('success') and sector_data.get('success'):
                indices = market_data.get('data', {})
                
                snapshot = MarketSnapshot(
                    snapshot_date=today,
                    sp500=indices.get('S&P 500', {}).get('price'),
                    nasdaq=indices.get('NASDAQ', {}).get('price'),
                    dow=indices.get('DOW', {}).get('price'),
                    vix=indices.get('VIX', {}).get('price'),
                    sector_performance=sector_data.get('data'),
                    # TODO: Add top movers data
                    top_gainers=[],
                    top_losers=[],
                    most_active=[]
                )
                
                db.add(snapshot)
                db.commit()
                logger.info("Daily snapshot created successfully")
            
        except Exception as e:
            logger.error(f"Snapshot creation error: {e}")
            db.rollback()
        finally:
            db.close()
    
    def get_popular_symbols(self) -> List[str]:
        """Get list of popular symbols to pre-cache."""
        # Top tech stocks
        tech_stocks = ['AAPL', 'MSFT', 'GOOGL', 'AMZN', 'META', 'NVDA', 'TSLA']
        
        # Major indices ETFs
        index_etfs = ['SPY', 'QQQ', 'DIA', 'IWM']
        
        # Popular stocks
        popular = ['BRK.B', 'JPM', 'V', 'JNJ', 'WMT', 'PG', 'MA', 'UNH', 'HD', 'DIS']
        
        return tech_stocks + index_etfs + popular


# Singleton instance
cache_service = CacheService()
