"""Test the cache system."""

from services.cache_service import cache_service
from services.enhanced_data_fetcher import enhanced_fetcher

# Test caching a quote
print("Testing cache system...")

# Fetch Apple data
data = enhanced_fetcher.get_yahoo_stock_data("AAPL")
if data.get('success'):
    cache_service.cache_quote("AAPL", data, "yahoo")
    print("✓ Cached AAPL data")

# Try to get from cache
cached = cache_service.get_cached_quote("AAPL")
if cached:
    print(f"✓ Retrieved from cache: ${cached['data']['price']}")
else:
    print("✗ Cache retrieval failed")

# Test market snapshot
snapshot = cache_service.get_market_snapshot()
print(f"Market snapshot: {snapshot}")

print("\nCache system test complete!")
