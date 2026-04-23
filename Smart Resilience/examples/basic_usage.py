"""
Basic usage examples for Smart Resilience primitives
"""

import time
import random
from smart_resilience import (
    retry,
    circuit_breaker,
    rate_limit,
    timeout,
    fallback,
    BackoffStrategy,
    RetryError,
    CircuitOpenError,
    RateLimitError
)


print("=" * 60)
print("BASIC RESILIENCE PRIMITIVES - EXAMPLES")
print("=" * 60)


print("\n1. RETRY WITH EXPONENTIAL BACKOFF")
print("-" * 60)

@retry(max_attempts=3, backoff_strategy=BackoffStrategy.EXPONENTIAL, base_delay=0.5)
def unreliable_api_call():
    """Simulates an API that fails randomly"""
    if random.random() < 0.7:
        raise ConnectionError("API temporarily unavailable")
    return {"status": "success", "data": "Hello World"}

try:
    result = unreliable_api_call()
    print(f"✓ Success: {result}")
except RetryError as e:
    print(f"✗ Failed after retries: {e}")


print("\n2. CIRCUIT BREAKER")
print("-" * 60)

@circuit_breaker(failure_threshold=3, timeout=5)
def flaky_service():
    """Simulates a service that fails frequently"""
    if random.random() < 0.8:
        raise Exception("Service error")
    return "Service response"

for i in range(10):
    try:
        result = flaky_service()
        print(f"  Call {i+1}: ✓ {result}")
    except CircuitOpenError:
        print(f"  Call {i+1}: ⚠ Circuit is OPEN (protecting system)")
        time.sleep(1)
    except Exception as e:
        print(f"  Call {i+1}: ✗ {str(e)}")


print("\n3. RATE LIMITING")
print("-" * 60)

@rate_limit(calls=3, period=2)
def api_endpoint():
    """Simulates an API with rate limits"""
    return f"Response at {time.time():.2f}"

print("Making 5 rapid calls (limit: 3 per 2 seconds):")
for i in range(5):
    try:
        result = api_endpoint()
        print(f"  Call {i+1}: ✓ {result}")
    except RateLimitError as e:
        print(f"  Call {i+1}: ⚠ {e}")
        time.sleep(1)


print("\n4. TIMEOUT")
print("-" * 60)

@timeout(2)
def slow_operation():
    """Simulates a slow operation"""
    time.sleep(3)
    return "Completed"

try:
    result = slow_operation()
    print(f"✓ {result}")
except TimeoutError as e:
    print(f"✗ {e}")


print("\n5. FALLBACK CHAIN")
print("-" * 60)

def primary_source():
    """Primary data source (fails)"""
    raise Exception("Primary source unavailable")

def cache_source():
    """Cache fallback (fails)"""
    raise Exception("Cache miss")

def default_source():
    """Default fallback (succeeds)"""
    return {"data": "default value"}

@fallback(cache_source, default_source)
def get_data():
    return primary_source()

result = get_data()
print(f"✓ Got data from fallback: {result}")


print("\n6. COMBINING PRIMITIVES")
print("-" * 60)

@retry(max_attempts=3, backoff_strategy=BackoffStrategy.EXPONENTIAL)
@circuit_breaker(failure_threshold=5, timeout=10)
@rate_limit(calls=10, period=1)
def production_api_call():
    """Production-ready API call with multiple resilience layers"""
    if random.random() < 0.3:
        raise Exception("Transient error")
    return {"status": "ok", "timestamp": time.time()}

print("Making production calls with layered resilience:")
for i in range(5):
    try:
        result = production_api_call()
        print(f"  Call {i+1}: ✓ Success")
        time.sleep(0.2)
    except Exception as e:
        print(f"  Call {i+1}: ✗ {type(e).__name__}")


print("\n" + "=" * 60)
print("BASIC EXAMPLES COMPLETE")
print("=" * 60)
