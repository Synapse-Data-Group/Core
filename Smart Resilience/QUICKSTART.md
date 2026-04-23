# Smart Resilience - Quick Start Guide

## Installation

```bash
# Basic (zero dependencies)
pip install smart-resilience

# With cognitive features
pip install smart-resilience[cognitive]
```

## 5-Minute Tutorial

### 1. Basic Retry (30 seconds)

```python
from smart_resilience import retry, BackoffStrategy

@retry(max_attempts=3, backoff_strategy=BackoffStrategy.EXPONENTIAL)
def call_api():
    return api.get("/endpoint")

result = call_api()  # Automatically retries on failure
```

### 2. Circuit Breaker (1 minute)

```python
from smart_resilience import circuit_breaker

@circuit_breaker(failure_threshold=5, timeout=60)
def unreliable_service():
    return service.call()

# Circuit opens after 5 failures, protecting your system
result = unreliable_service()
```

### 3. Rate Limiting (1 minute)

```python
from smart_resilience import rate_limit

@rate_limit(calls=100, period=60)  # 100 calls per minute
def api_endpoint():
    return process_request()

result = api_endpoint()  # Automatically rate limited
```

### 4. Cognitive Retry (2 minutes)

```python
from cognitive_load_monitor import CognitiveLoadMonitor
from smart_resilience import cognitive_retry

monitor = CognitiveLoadMonitor()

@cognitive_retry(clm=monitor, adaptive=True)
def complex_task():
    """Retry adapts based on cognitive load"""
    return agent.execute()

# High load → longer backoff
# Low load → faster retry
result = complex_task()
```

### 5. Production Stack (1 minute)

```python
from smart_resilience import retry, circuit_breaker, rate_limit, timeout

@retry(max_attempts=3)
@circuit_breaker(failure_threshold=5)
@rate_limit(calls=100, period=60)
@timeout(30)
def production_api():
    """Layered resilience for production"""
    return api.call()

result = production_api()
```

## Next Steps

- Read the full [README.md](README.md)
- Run examples: `python examples/basic_usage.py`
- Run tests: `pytest test_smart_resilience.py`
- Explore cognitive features: `python examples/cognitive_usage.py`

## Key Concepts

**Basic Primitives** (zero dependencies):
- `@retry` - Automatic retry with backoff
- `@circuit_breaker` - Prevent cascading failures
- `@rate_limit` - Token bucket rate limiting
- `@timeout` - Execution time limits
- `@fallback` - Fallback chains

**Cognitive Primitives** (requires CLM/MEO):
- `@cognitive_retry` - Adapts to cognitive load
- `@memory_circuit_breaker` - Learns from patterns
- `@adaptive_backoff` - Intelligent timing

## Common Patterns

### Pattern 1: Retry with Fallback
```python
@retry(max_attempts=3)
@fallback(use_cache, use_default)
def get_data():
    return api.fetch()
```

### Pattern 2: Rate-Limited Circuit Breaker
```python
@rate_limit(calls=100, period=60)
@circuit_breaker(failure_threshold=5)
def protected_api():
    return service.call()
```

### Pattern 3: Cognitive Production Stack
```python
@cognitive_retry(clm=monitor, adaptive=True)
@memory_circuit_breaker(meo=wisdom, learn_from_history=True)
@rate_limit(calls=1000, period=60)
def smart_api():
    return llm.complete(prompt)
```

## Troubleshooting

**Q: Import error for cognitive features?**
```bash
pip install cognitive-load-monitor synapse-meo
```

**Q: How to access circuit breaker state?**
```python
@circuit_breaker(failure_threshold=5)
def func():
    return service.call()

print(func.circuit_breaker.state)  # Access breaker
```

**Q: How to manually reset circuit breaker?**
```python
func.circuit_breaker.reset()
```

**Q: How to check rate limiter status?**
```python
@rate_limit(calls=100, period=60)
def func():
    return api.call()

wait_time = func.rate_limiter.wait_time()
```

## Support

- GitHub: https://github.com/synapse-data/smart-resilience
- Issues: https://github.com/synapse-data/smart-resilience/issues
- Ecosystem: https://github.com/synapse-data
