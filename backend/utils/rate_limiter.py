"""Rate limiting utility for API endpoints."""

from datetime import datetime, timedelta
from collections import defaultdict, deque
from typing import Dict, Deque
import threading

class RateLimiter:
    """Simple in-memory rate limiter."""
    
    def __init__(self, max_requests: int = 4, window_seconds: int = 60):
        self.max_requests = max_requests
        self.window_seconds = window_seconds
        self.requests: Dict[str, Deque[datetime]] = defaultdict(deque)
        self.lock = threading.Lock()
    
    def is_allowed(self, key: str) -> tuple[bool, int]:
        """Check if request is allowed for the given key.
        
        Returns:
            Tuple of (is_allowed, seconds_until_next_allowed)
        """
        with self.lock:
            now = datetime.now()
            window_start = now - timedelta(seconds=self.window_seconds)
            
            # Remove old requests outside the window
            while self.requests[key] and self.requests[key][0] < window_start:
                self.requests[key].popleft()
            
            # Check if under limit
            if len(self.requests[key]) < self.max_requests:
                self.requests[key].append(now)
                return True, 0
            else:
                # Calculate when the next request will be allowed
                oldest_request = self.requests[key][0]
                next_allowed = oldest_request + timedelta(seconds=self.window_seconds)
                seconds_until_allowed = max(0, int((next_allowed - now).total_seconds()))
                return False, seconds_until_allowed
    
    def get_remaining(self, key: str) -> int:
        """Get remaining requests for the given key."""
        with self.lock:
            now = datetime.now()
            window_start = now - timedelta(seconds=self.window_seconds)
            
            # Remove old requests
            while self.requests[key] and self.requests[key][0] < window_start:
                self.requests[key].popleft()
            
            return max(0, self.max_requests - len(self.requests[key]))

# Global rate limiter instance
agent_rate_limiter = RateLimiter(max_requests=4, window_seconds=60)
