"""
Smart Resilience - Cognitive-aware resilience primitives for AI agents

A foundational package providing resilience patterns with an innovative twist:
cognitive awareness through integration with CLM and MEO.
"""

from smart_resilience import (
    retry,
    circuit_breaker,
    rate_limit,
    timeout,
    fallback,
    cognitive_retry,
    memory_circuit_breaker,
    adaptive_backoff,
    BackoffStrategy,
    CircuitState,
    CircuitBreaker,
    RateLimiter,
    MemoryCircuitBreaker,
    RetryError,
    CircuitOpenError,
    RateLimitError,
    calculate_backoff,
)

__version__ = "0.1.0"
__author__ = "Synapse Data / Ivan Lluch"
__license__ = "Apache-2.0"

__all__ = [
    "retry",
    "circuit_breaker",
    "rate_limit",
    "timeout",
    "fallback",
    "cognitive_retry",
    "memory_circuit_breaker",
    "adaptive_backoff",
    "BackoffStrategy",
    "CircuitState",
    "CircuitBreaker",
    "RateLimiter",
    "MemoryCircuitBreaker",
    "RetryError",
    "CircuitOpenError",
    "RateLimitError",
    "calculate_backoff",
]
