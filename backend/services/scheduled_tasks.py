"""Scheduled tasks for data pre-fetching and maintenance."""

import logging
from datetime import datetime, time
from apscheduler.schedulers.asyncio import AsyncIOScheduler
from apscheduler.triggers.cron import CronTrigger
from apscheduler.triggers.interval import IntervalTrigger

from services.cache_service import cache_service
from services.enhanced_data_fetcher import enhanced_fetcher
from config import settings

logger = logging.getLogger(__name__)


class ScheduledTasks:
    """Manage scheduled background tasks."""
    
    def __init__(self):
        self.scheduler = AsyncIOScheduler()
        self.setup_tasks()
    
    def setup_tasks(self):
        """Configure all scheduled tasks."""
        
        # Pre-fetch popular stocks every 5 minutes during market hours
        self.scheduler.add_job(
            self.prefetch_popular_stocks,
            IntervalTrigger(minutes=5),
            id='prefetch_stocks',
            name='Pre-fetch popular stock data',
            misfire_grace_time=30
        )
        
        # Create daily market snapshot at market close
        self.scheduler.add_job(
            cache_service.create_daily_snapshot,
            CronTrigger(hour=16, minute=30),  # 4:30 PM ET
            id='daily_snapshot',
            name='Create daily market snapshot'
        )
        
        # Update company info weekly
        self.scheduler.add_job(
            self.update_company_info,
            CronTrigger(day_of_week=6, hour=2),  # Saturday 2 AM
            id='update_companies',
            name='Update company information'
        )
    
    async def prefetch_popular_stocks(self):
        """Pre-fetch data for popular stocks."""
        if not self.is_market_hours():
            logger.info("Skipping pre-fetch outside market hours")
            return
        
        logger.info("Starting popular stocks pre-fetch...")
        
        symbols = cache_service.get_popular_symbols()
        success_count = 0
        
        for symbol in symbols:
            try:
                # Check if we have recent cache
                cached = cache_service.get_cached_quote(symbol)
                if cached:
                    continue
                
                # Fetch fresh data
                data = enhanced_fetcher.get_yahoo_stock_data(symbol)
                if data.get('success'):
                    cache_service.cache_quote(symbol, data, 'yahoo')
                    success_count += 1
                
                # Small delay to avoid rate limits
                await asyncio.sleep(0.5)
                
            except Exception as e:
                logger.error(f"Error pre-fetching {symbol}: {e}")
        
        logger.info(f"Pre-fetched {success_count} stocks")
    
    async def update_company_info(self):
        """Update company information for cached symbols."""
        logger.info("Updating company information...")
        
        # Get unique symbols from cache
        db = next(get_db())
        try:
            symbols = db.query(MarketDataCache.symbol).distinct().all()
            
            for (symbol,) in symbols:
                try:
                    # Fetch company overview
                    # This would use Alpha Vantage or another source
                    pass
                except Exception as e:
                    logger.error(f"Error updating {symbol}: {e}")
                    
        finally:
            db.close()
    
    def is_market_hours(self) -> bool:
        """Check if currently in US market hours."""
        now = datetime.now()
        
        # Skip weekends
        if now.weekday() >= 5:
            return False
        
        # Market hours: 9:30 AM - 4:00 PM ET
        market_open = time(9, 30)
        market_close = time(16, 0)
        
        current_time = now.time()
        return market_open <= current_time <= market_close
    
    def start(self):
        """Start the scheduler."""
        self.scheduler.start()
        logger.info("Scheduled tasks started")
    
    def stop(self):
        """Stop the scheduler."""
        self.scheduler.shutdown()
        logger.info("Scheduled tasks stopped")


# Global scheduler instance
task_scheduler = ScheduledTasks()
