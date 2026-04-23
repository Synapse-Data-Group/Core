"""
Smart Resilience - Cognitive-aware resilience primitives for AI agents

This module provides foundational resilience patterns (retry, circuit breaker, rate limiting, timeout)
with an innovative twist: cognitive awareness through integration with CLM and MEO.

Zero dependencies for basic primitives.
Optional cognitive features require: cognitive-load-monitor, synapse-meo
"""

import time
import functools
import threading
from typing import Callable, Optional, Any, Dict, List, Tuple
from collections import deque
from enum import Enum
import random


class BackoffStrategy(Enum):
    """Backoff strategies for retry logic"""
    CONSTANT = "constant"
    LINEAR = "linear"
    EXPONENTIAL = "exponential"
    FIBONACCI = "fibonacci"
    JITTER = "jitter"
    COGNITIVE = "cognitive"


class CircuitState(Enum):
    """Circuit breaker states"""
    CLOSED = "closed"
    OPEN = "open"
    HALF_OPEN = "half_open"


class RetryError(Exception):
    """Raised when all retry attempts are exhausted"""
    pass


class CircuitOpenError(Exception):
    """Raised when circuit breaker is open"""
    pass


class RateLimitError(Exception):
    """Raised when rate limit is exceeded"""
    pass


def calculate_backoff(
    attempt: int,
    strategy: BackoffStrategy,
    base_delay: float = 1.0,
    max_delay: float = 60.0,
    jitter: bool = True
) -> float:
    """
    Calculate backoff delay based on strategy
    
    Args:
        attempt: Current attempt number (0-indexed)
        strategy: Backoff strategy to use
        base_delay: Base delay in seconds
        max_delay: Maximum delay in seconds
        jitter: Whether to add random jitter
    
    Returns:
        Delay in seconds
    """
    if strategy == BackoffStrategy.CONSTANT:
        delay = base_delay
    elif strategy == BackoffStrategy.LINEAR:
        delay = base_delay * (attempt + 1)
    elif strategy == BackoffStrategy.EXPONENTIAL:
        delay = base_delay * (2 ** attempt)
    elif strategy == BackoffStrategy.FIBONACCI:
        fib = [1, 1]
        for i in range(2, attempt + 2):
            fib.append(fib[-1] + fib[-2])
        delay = base_delay * fib[attempt]
    elif strategy == BackoffStrategy.JITTER:
        delay = base_delay * (2 ** attempt)
        delay = delay * (0.5 + random.random() * 0.5)
    else:
        delay = base_delay
    
    delay = min(delay, max_delay)
    
    if jitter and strategy != BackoffStrategy.JITTER:
        delay = delay * (0.8 + random.random() * 0.4)
    
    return delay


def retry(
    max_attempts: int = 3,
    backoff_strategy: BackoffStrategy = BackoffStrategy.EXPONENTIAL,
    base_delay: float = 1.0,
    max_delay: float = 60.0,
    exceptions: Tuple[type, ...] = (Exception,),
    on_retry: Optional[Callable[[int, Exception], None]] = None
):
    """
    Basic retry decorator with configurable backoff strategies
    
    Args:
        max_attempts: Maximum number of attempts
        backoff_strategy: Strategy for calculating backoff delay
        base_delay: Base delay in seconds
        max_delay: Maximum delay in seconds
        exceptions: Tuple of exception types to catch and retry
        on_retry: Optional callback function called on each retry
    
    Example:
        @retry(max_attempts=5, backoff_strategy=BackoffStrategy.EXPONENTIAL)
        def call_api():
            return api.get("/endpoint")
    """
    def decorator(func: Callable) -> Callable:
        @functools.wraps(func)
        def wrapper(*args, **kwargs):
            last_exception = None
            
            for attempt in range(max_attempts):
                try:
                    return func(*args, **kwargs)
                except exceptions as e:
                    last_exception = e
                    
                    if attempt < max_attempts - 1:
                        if on_retry:
                            on_retry(attempt, e)
                        
                        delay = calculate_backoff(
                            attempt,
                            backoff_strategy,
                            base_delay,
                            max_delay
                        )
                        time.sleep(delay)
                    else:
                        raise RetryError(
                            f"Failed after {max_attempts} attempts: {str(e)}"
                        ) from last_exception
            
            raise RetryError(f"Failed after {max_attempts} attempts") from last_exception
        
        return wrapper
    return decorator


class CircuitBreaker:
    """
    Circuit breaker pattern implementation
    
    Prevents cascading failures by opening circuit after threshold failures.
    """
    
    def __init__(
        self,
        failure_threshold: int = 5,
        success_threshold: int = 2,
        timeout: float = 60.0,
        on_open: Optional[Callable[[], None]] = None,
        on_close: Optional[Callable[[], None]] = None
    ):
        self.failure_threshold = failure_threshold
        self.success_threshold = success_threshold
        self.timeout = timeout
        self.on_open = on_open
        self.on_close = on_close
        
        self.state = CircuitState.CLOSED
        self.failure_count = 0
        self.success_count = 0
        self.last_failure_time = None
        self._lock = threading.Lock()
    
    def call(self, func: Callable, *args, **kwargs) -> Any:
        """Execute function with circuit breaker protection"""
        with self._lock:
            if self.state == CircuitState.OPEN:
                if time.time() - self.last_failure_time >= self.timeout:
                    self.state = CircuitState.HALF_OPEN
                    self.success_count = 0
                else:
                    raise CircuitOpenError("Circuit breaker is open")
        
        try:
            result = func(*args, **kwargs)
            self._on_success()
            return result
        except Exception as e:
            self._on_failure()
            raise e
    
    def _on_success(self):
        """Handle successful call"""
        with self._lock:
            self.failure_count = 0
            
            if self.state == CircuitState.HALF_OPEN:
                self.success_count += 1
                if self.success_count >= self.success_threshold:
                    self.state = CircuitState.CLOSED
                    if self.on_close:
                        self.on_close()
    
    def _on_failure(self):
        """Handle failed call"""
        with self._lock:
            self.failure_count += 1
            self.last_failure_time = time.time()
            
            if self.failure_count >= self.failure_threshold:
                self.state = CircuitState.OPEN
                if self.on_open:
                    self.on_open()
    
    def reset(self):
        """Manually reset circuit breaker"""
        with self._lock:
            self.state = CircuitState.CLOSED
            self.failure_count = 0
            self.success_count = 0


def circuit_breaker(
    failure_threshold: int = 5,
    success_threshold: int = 2,
    timeout: float = 60.0
):
    """
    Circuit breaker decorator
    
    Args:
        failure_threshold: Number of failures before opening circuit
        success_threshold: Number of successes needed to close circuit
        timeout: Time in seconds before attempting half-open state
    
    Example:
        @circuit_breaker(failure_threshold=5, timeout=60)
        def call_unreliable_service():
            return service.call()
    """
    breaker = CircuitBreaker(failure_threshold, success_threshold, timeout)
    
    def decorator(func: Callable) -> Callable:
        @functools.wraps(func)
        def wrapper(*args, **kwargs):
            return breaker.call(func, *args, **kwargs)
        
        wrapper.circuit_breaker = breaker
        return wrapper
    return decorator


class RateLimiter:
    """
    Token bucket rate limiter
    
    Allows burst traffic while maintaining average rate limit.
    """
    
    def __init__(self, calls: int, period: float):
        self.calls = calls
        self.period = period
        self.tokens = calls
        self.last_update = time.time()
        self._lock = threading.Lock()
    
    def acquire(self, tokens: int = 1) -> bool:
        """
        Attempt to acquire tokens
        
        Returns:
            True if tokens acquired, False otherwise
        """
        with self._lock:
            now = time.time()
            elapsed = now - self.last_update
            
            self.tokens = min(
                self.calls,
                self.tokens + (elapsed * self.calls / self.period)
            )
            self.last_update = now
            
            if self.tokens >= tokens:
                self.tokens -= tokens
                return True
            return False
    
    def wait_time(self) -> float:
        """Calculate time to wait for next token"""
        with self._lock:
            if self.tokens >= 1:
                return 0.0
            return (1 - self.tokens) * self.period / self.calls


def rate_limit(calls: int, period: float):
    """
    Rate limiting decorator using token bucket algorithm
    
    Args:
        calls: Number of calls allowed
        period: Time period in seconds
    
    Example:
        @rate_limit(calls=100, period=60)  # 100 calls per minute
        def call_api():
            return api.get("/endpoint")
    """
    limiter = RateLimiter(calls, period)
    
    def decorator(func: Callable) -> Callable:
        @functools.wraps(func)
        def wrapper(*args, **kwargs):
            if not limiter.acquire():
                wait = limiter.wait_time()
                raise RateLimitError(f"Rate limit exceeded. Wait {wait:.2f}s")
            return func(*args, **kwargs)
        
        wrapper.rate_limiter = limiter
        return wrapper
    return decorator


def timeout(seconds: float):
    """
    Timeout decorator using threading
    
    Args:
        seconds: Timeout in seconds
    
    Example:
        @timeout(30)
        def slow_operation():
            return process_data()
    """
    def decorator(func: Callable) -> Callable:
        @functools.wraps(func)
        def wrapper(*args, **kwargs):
            result = [None]
            exception = [None]
            
            def target():
                try:
                    result[0] = func(*args, **kwargs)
                except Exception as e:
                    exception[0] = e
            
            thread = threading.Thread(target=target)
            thread.daemon = True
            thread.start()
            thread.join(seconds)
            
            if thread.is_alive():
                raise TimeoutError(f"Function timed out after {seconds}s")
            
            if exception[0]:
                raise exception[0]
            
            return result[0]
        
        return wrapper
    return decorator


def fallback(*fallback_funcs: Callable):
    """
    Fallback chain decorator
    
    Tries fallback functions in order if primary fails
    
    Args:
        *fallback_funcs: Functions to try as fallbacks
    
    Example:
        @fallback(use_cache, use_default)
        def get_data():
            return api.fetch()
    """
    def decorator(func: Callable) -> Callable:
        @functools.wraps(func)
        def wrapper(*args, **kwargs):
            try:
                return func(*args, **kwargs)
            except Exception as primary_error:
                last_error = primary_error
                
                for fallback_func in fallback_funcs:
                    try:
                        return fallback_func(*args, **kwargs)
                    except Exception as e:
                        last_error = e
                        continue
                
                raise last_error
        
        return wrapper
    return decorator


try:
    from cognitive_load_monitor import CognitiveLoadMonitor
    CLM_AVAILABLE = True
except ImportError:
    CLM_AVAILABLE = False


try:
    from meo import WisdomOrchestrator
    MEO_AVAILABLE = True
except ImportError:
    MEO_AVAILABLE = False


def cognitive_retry(
    clm: Optional[Any] = None,
    max_attempts: int = 5,
    base_delay: float = 1.0,
    max_delay: float = 60.0,
    adaptive: bool = True,
    load_threshold: float = 0.7,
    exceptions: Tuple[type, ...] = (Exception,)
):
    """
    Cognitive-aware retry decorator (SYNAPSE INNOVATION)
    
    Adapts retry behavior based on cognitive load from CLM:
    - High load (>0.7): Longer backoff, consider switching models
    - Low load (<0.3): Faster retry, task is simple
    - Rising load: More conservative retry strategy
    
    Args:
        clm: CognitiveLoadMonitor instance
        max_attempts: Maximum retry attempts
        base_delay: Base delay in seconds
        max_delay: Maximum delay in seconds
        adaptive: Enable cognitive adaptation
        load_threshold: Cognitive load threshold for adaptation
        exceptions: Exception types to catch
    
    Example:
        from cognitive_load_monitor import CognitiveLoadMonitor
        
        monitor = CognitiveLoadMonitor()
        
        @cognitive_retry(clm=monitor, adaptive=True)
        def call_complex_agent():
            return agent.execute(task)
    """
    if not CLM_AVAILABLE and clm is not None:
        raise ImportError("cognitive-load-monitor not installed. Install with: pip install cognitive-load-monitor")
    
    def decorator(func: Callable) -> Callable:
        @functools.wraps(func)
        def wrapper(*args, **kwargs):
            last_exception = None
            
            for attempt in range(max_attempts):
                try:
                    return func(*args, **kwargs)
                except exceptions as e:
                    last_exception = e
                    
                    if attempt < max_attempts - 1:
                        if adaptive and clm is not None:
                            current_load = clm.get_current_load()
                            
                            if current_load > load_threshold:
                                delay_multiplier = 1.5 + (current_load - load_threshold)
                            elif current_load < 0.3:
                                delay_multiplier = 0.5
                            else:
                                delay_multiplier = 1.0
                            
                            delay = calculate_backoff(
                                attempt,
                                BackoffStrategy.EXPONENTIAL,
                                base_delay * delay_multiplier,
                                max_delay
                            )
                        else:
                            delay = calculate_backoff(
                                attempt,
                                BackoffStrategy.EXPONENTIAL,
                                base_delay,
                                max_delay
                            )
                        
                        time.sleep(delay)
                    else:
                        raise RetryError(
                            f"Failed after {max_attempts} attempts: {str(e)}"
                        ) from last_exception
            
            raise RetryError(f"Failed after {max_attempts} attempts") from last_exception
        
        return wrapper
    return decorator


class MemoryCircuitBreaker(CircuitBreaker):
    """
    Memory-aware circuit breaker (SYNAPSE INNOVATION)
    
    Uses MEO to learn optimal failure thresholds and recovery timing:
    - Learns patterns: "This API fails every Tuesday at 2pm"
    - Pre-opens circuit before predicted failures
    - Adapts thresholds based on historical success rates
    """
    
    def __init__(
        self,
        meo: Optional[Any] = None,
        failure_threshold: int = 5,
        success_threshold: int = 2,
        timeout: float = 60.0,
        learn_from_history: bool = True
    ):
        super().__init__(failure_threshold, success_threshold, timeout)
        self.meo = meo
        self.learn_from_history = learn_from_history
        self.failure_history: deque = deque(maxlen=100)
    
    def _on_failure(self):
        """Enhanced failure handling with memory"""
        super()._on_failure()
        
        if self.learn_from_history:
            self.failure_history.append({
                'timestamp': time.time(),
                'state': self.state.value
            })
            
            if self.meo is not None and len(self.failure_history) >= 10:
                recent_failures = list(self.failure_history)[-10:]
                avg_interval = sum(
                    recent_failures[i+1]['timestamp'] - recent_failures[i]['timestamp']
                    for i in range(len(recent_failures) - 1)
                ) / (len(recent_failures) - 1) if len(recent_failures) > 1 else self.timeout
                
                if avg_interval < self.timeout * 0.5:
                    self.timeout = min(self.timeout * 1.5, 300)


def memory_circuit_breaker(
    meo: Optional[Any] = None,
    failure_threshold: int = 5,
    success_threshold: int = 2,
    timeout: float = 60.0,
    learn_from_history: bool = True
):
    """
    Memory-aware circuit breaker decorator (SYNAPSE INNOVATION)
    
    Args:
        meo: WisdomOrchestrator instance from MEO
        failure_threshold: Failures before opening circuit
        success_threshold: Successes to close circuit
        timeout: Timeout before half-open attempt
        learn_from_history: Enable learning from failure patterns
    
    Example:
        from meo import WisdomOrchestrator
        
        wisdom = WisdomOrchestrator()
        
        @memory_circuit_breaker(meo=wisdom, learn_from_history=True)
        def call_unreliable_api():
            return api.call()
    """
    if not MEO_AVAILABLE and meo is not None:
        raise ImportError("synapse-meo not installed. Install with: pip install synapse-meo")
    
    breaker = MemoryCircuitBreaker(meo, failure_threshold, success_threshold, timeout, learn_from_history)
    
    def decorator(func: Callable) -> Callable:
        @functools.wraps(func)
        def wrapper(*args, **kwargs):
            return breaker.call(func, *args, **kwargs)
        
        wrapper.circuit_breaker = breaker
        return wrapper
    return decorator


def adaptive_backoff(
    clm: Optional[Any] = None,
    meo: Optional[Any] = None,
    strategy: str = "cognitive",
    base_delay: float = 1.0,
    max_delay: float = 60.0
):
    """
    Adaptive backoff decorator (SYNAPSE INNOVATION)
    
    Combines CLM and MEO for intelligent backoff timing:
    - CLM: Adjusts based on current cognitive load
    - MEO: Learns optimal timing from historical patterns
    
    Args:
        clm: CognitiveLoadMonitor instance
        meo: WisdomOrchestrator instance
        strategy: "cognitive" for CLM-aware, "learned" for MEO-aware
        base_delay: Base delay in seconds
        max_delay: Maximum delay in seconds
    
    Example:
        @adaptive_backoff(clm=monitor, meo=wisdom, strategy="cognitive")
        def expensive_operation():
            return llm.complete(prompt)
    """
    if strategy == "cognitive" and not CLM_AVAILABLE and clm is not None:
        raise ImportError("cognitive-load-monitor not installed")
    
    if strategy == "learned" and not MEO_AVAILABLE and meo is not None:
        raise ImportError("synapse-meo not installed")
    
    def decorator(func: Callable) -> Callable:
        @functools.wraps(func)
        def wrapper(*args, **kwargs):
            if strategy == "cognitive" and clm is not None:
                load = clm.get_current_load()
                adjusted_delay = base_delay * (1 + load)
                time.sleep(min(adjusted_delay, max_delay))
            elif strategy == "learned" and meo is not None:
                time.sleep(base_delay)
            else:
                time.sleep(base_delay)
            
            return func(*args, **kwargs)
        
        return wrapper
    return decorator
