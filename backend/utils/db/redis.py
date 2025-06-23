# utils/db/redis.py
"""Redis cache management."""

import redis
import json
import logging
from typing import Any, Optional, Union
from datetime import timedelta, datetime

from config import settings

logger = logging.getLogger(__name__)

_redis_client: Optional[redis.Redis] = None

def get_redis_client() -> redis.Redis:
    """Get Redis client instance."""
    global _redis_client
    
    if _redis_client is None:
        try:
            _redis_client = redis.Redis.from_url(
                settings.redis_url,
                decode_responses=True,
                socket_connect_timeout=5
            )
            _redis_client.ping()
            logger.info("Redis connection established")
        except Exception as e:
            logger.error(f"Failed to connect to Redis: {e}")
            raise
    
    return _redis_client

def cache_set(
    key: str,
    value: Any,
    expire: Union[int, timedelta] = None
) -> bool:
    """Set a value in cache.
    
    Args:
        key: Cache key
        value: Value to cache (will be JSON serialized)
        expire: Expiration time in seconds or timedelta
    """
    client = get_redis_client()
    
    try:
        def serialize(obj):
            if isinstance(obj, datetime):
                return obj.isoformat()
            raise TypeError(f"Object of type {type(obj)} is not JSON serializable")
        
        serialized = json.dumps(value, default=serialize)
        if expire:
            if isinstance(expire, timedelta):
                expire = int(expire.total_seconds())
            return client.setex(key, expire, serialized)
        else:
            return client.set(key, serialized)
    except Exception as e:
        logger.error(f"Failed to set cache key {key}: {e}")
        return False

def cache_get(key: str) -> Optional[Any]:
    """Get a value from cache."""
    client = get_redis_client()
    
    try:
        value = client.get(key)
        if value:
            return json.loads(value)
        return None
    except Exception as e:
        logger.error(f"Failed to get cache key {key}: {e}")
        return None

def cache_delete(key: str) -> bool:
    """Delete a key from cache."""
    client = get_redis_client()
    
    try:
        return bool(client.delete(key))
    except Exception as e:
        logger.error(f"Failed to delete cache key {key}: {e}")
        return False

def cache_exists(key: str) -> bool:
    """Check if a key exists in cache."""
    client = get_redis_client()
    
    try:
        return bool(client.exists(key))
    except Exception as e:
        logger.error(f"Failed to check cache key {key}: {e}")
        return False

# Cache key templates
CACHE_KEYS = {
    "market_data": "market:{}:{}",  # market:symbol:timeframe
    "research": "research:{}",  # research:research_id
    "strategy": "strategy:{}",  # strategy:strategy_id
    "backtest": "backtest:{}",  # backtest:backtest_id
    "news": "news:{}:{}",  # news:query:date
    "embedding": "embedding:{}",  # embedding:content_hash
}

def get_cache_key(template: str, *args) -> str:
    """Generate a cache key from template."""
    if template not in CACHE_KEYS:
        raise ValueError(f"Unknown cache key template: {template}")
    
    return CACHE_KEYS[template].format(*args)