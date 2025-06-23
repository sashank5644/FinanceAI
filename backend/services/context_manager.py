"""Context manager for enriching agent responses."""

import logging
from typing import Dict, Any, List
from datetime import datetime, timedelta

logger = logging.getLogger(__name__)


class ContextManager:
    """Manage context for agent responses."""
    
    def __init__(self):
        self.market_hours = {
            'open': '9:30 AM ET',
            'close': '4:00 PM ET',
            'premarket': '4:00 AM - 9:30 AM ET',
            'afterhours': '4:00 PM - 8:00 PM ET'
        }
        
        self.market_holidays_2025 = [
            '2025-01-01',  # New Year's Day
            '2025-01-20',  # MLK Day
            '2025-02-17',  # Presidents Day
            '2025-04-18',  # Good Friday
            '2025-05-26',  # Memorial Day
            '2025-07-04',  # Independence Day
            '2025-09-01',  # Labor Day
            '2025-11-27',  # Thanksgiving
            '2025-12-25',  # Christmas
        ]
    
    def get_market_status(self) -> Dict[str, Any]:
        """Get current market status."""
        now = datetime.now()
        
        # Check if weekend
        if now.weekday() >= 5:
            return {
                'status': 'closed',
                'reason': 'weekend',
                'next_open': self._get_next_market_open()
            }
        
        # Check if holiday
        today = now.strftime('%Y-%m-%d')
        if today in self.market_holidays_2025:
            return {
                'status': 'closed',
                'reason': 'market holiday',
                'next_open': self._get_next_market_open()
            }
        
        # Check time
        current_time = now.time()
        if current_time < datetime.strptime('09:30', '%H:%M').time():
            return {
                'status': 'premarket',
                'opens_in': self._time_until_open()
            }
        elif current_time < datetime.strptime('16:00', '%H:%M').time():
            return {
                'status': 'open',
                'closes_in': self._time_until_close()
            }
        elif current_time < datetime.strptime('20:00', '%H:%M').time():
            return {
                'status': 'afterhours',
                'regular_session_closed': True
            }
        else:
            return {
                'status': 'closed',
                'reason': 'after hours',
                'next_open': self._get_next_market_open()
            }
    
    def enrich_response(self, response: str, context: Dict[str, Any]) -> str:
        """Add contextual information to responses."""
        market_status = self.get_market_status()
        
        # Add market status context
        if market_status['status'] == 'closed':
            response += f"\n\n📊 *Market Status: Closed ({market_status.get('reason', '')})*"
            if 'next_open' in market_status:
                response += f"\nNext market open: {market_status['next_open']}"
        elif market_status['status'] == 'open':
            response += f"\n\n📊 *Market Status: Open*"
            response += f"\nCloses in: {market_status['closes_in']}"
        
        # Add data freshness indicator
        if context.get('data_source'):
            if 'live' in context['data_source']:
                response += "\n✅ *Real-time data*"
            elif 'cache' in context['data_source']:
                response += "\n🕐 *Cached data (may be delayed)*"
        
        return response
    
    def _time_until_open(self) -> str:
        """Calculate time until market opens."""
        now = datetime.now()
        market_open = now.replace(hour=9, minute=30, second=0)
        if now >= market_open:
            market_open += timedelta(days=1)
        
        delta = market_open - now
        hours = delta.seconds // 3600
        minutes = (delta.seconds % 3600) // 60
        
        return f"{hours}h {minutes}m"
    
    def _time_until_close(self) -> str:
        """Calculate time until market closes."""
        now = datetime.now()
        market_close = now.replace(hour=16, minute=0, second=0)
        
        delta = market_close - now
        hours = delta.seconds // 3600
        minutes = (delta.seconds % 3600) // 60
        
        return f"{hours}h {minutes}m"
    
    def _get_next_market_open(self) -> str:
        """Get next market open time."""
        now = datetime.now()
        
        # Skip to next weekday
        days_ahead = 1
        if now.weekday() == 4:  # Friday
            days_ahead = 3
        elif now.weekday() == 5:  # Saturday
            days_ahead = 2
        
        next_open = now + timedelta(days=days_ahead)
        next_open = next_open.replace(hour=9, minute=30, second=0)
        
        return next_open.strftime('%A, %B %d at 9:30 AM ET')


# Singleton instance
context_manager = ContextManager()
