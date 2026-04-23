"""
Test suite for Smart Resilience package
"""

import time
import pytest
from smart_resilience import (
    retry,
    circuit_breaker,
    rate_limit,
    timeout,
    fallback,
    BackoffStrategy,
    calculate_backoff,
    CircuitBreaker,
    RateLimiter,
    RetryError,
    CircuitOpenError,
    RateLimitError
)


class TestBackoffCalculation:
    """Test backoff calculation strategies"""
    
    def test_constant_backoff(self):
        delay = calculate_backoff(0, BackoffStrategy.CONSTANT, base_delay=2.0, jitter=False)
        assert delay == 2.0
        
        delay = calculate_backoff(5, BackoffStrategy.CONSTANT, base_delay=2.0, jitter=False)
        assert delay == 2.0
    
    def test_linear_backoff(self):
        delay = calculate_backoff(0, BackoffStrategy.LINEAR, base_delay=1.0, jitter=False)
        assert delay == 1.0
        
        delay = calculate_backoff(2, BackoffStrategy.LINEAR, base_delay=1.0, jitter=False)
        assert delay == 3.0
    
    def test_exponential_backoff(self):
        delay = calculate_backoff(0, BackoffStrategy.EXPONENTIAL, base_delay=1.0, jitter=False)
        assert delay == 1.0
        
        delay = calculate_backoff(3, BackoffStrategy.EXPONENTIAL, base_delay=1.0, jitter=False)
        assert delay == 8.0
    
    def test_max_delay_cap(self):
        delay = calculate_backoff(10, BackoffStrategy.EXPONENTIAL, base_delay=1.0, max_delay=10.0, jitter=False)
        assert delay <= 10.0
    
    def test_jitter_adds_randomness(self):
        delays = [
            calculate_backoff(3, BackoffStrategy.EXPONENTIAL, base_delay=1.0, jitter=True)
            for _ in range(10)
        ]
        assert len(set(delays)) > 1


class TestRetryDecorator:
    """Test retry decorator"""
    
    def test_successful_call_no_retry(self):
        call_count = [0]
        
        @retry(max_attempts=3)
        def success_func():
            call_count[0] += 1
            return "success"
        
        result = success_func()
        assert result == "success"
        assert call_count[0] == 1
    
    def test_retry_until_success(self):
        call_count = [0]
        
        @retry(max_attempts=3, base_delay=0.1)
        def eventually_succeeds():
            call_count[0] += 1
            if call_count[0] < 3:
                raise ValueError("Not yet")
            return "success"
        
        result = eventually_succeeds()
        assert result == "success"
        assert call_count[0] == 3
    
    def test_retry_exhaustion(self):
        call_count = [0]
        
        @retry(max_attempts=3, base_delay=0.1)
        def always_fails():
            call_count[0] += 1
            raise ValueError("Always fails")
        
        with pytest.raises(RetryError):
            always_fails()
        
        assert call_count[0] == 3
    
    def test_specific_exceptions_only(self):
        @retry(max_attempts=3, exceptions=(ValueError,), base_delay=0.1)
        def raises_type_error():
            raise TypeError("Wrong exception type")
        
        with pytest.raises(TypeError):
            raises_type_error()
    
    def test_on_retry_callback(self):
        retry_attempts = []
        
        def on_retry_callback(attempt, exception):
            retry_attempts.append(attempt)
        
        @retry(max_attempts=3, base_delay=0.1, on_retry=on_retry_callback)
        def fails_twice():
            if len(retry_attempts) < 2:
                raise ValueError("Fail")
            return "success"
        
        result = fails_twice()
        assert result == "success"
        assert retry_attempts == [0, 1]


class TestCircuitBreaker:
    """Test circuit breaker"""
    
    def test_circuit_starts_closed(self):
        breaker = CircuitBreaker(failure_threshold=3)
        assert breaker.state.value == "closed"
    
    def test_circuit_opens_after_threshold(self):
        breaker = CircuitBreaker(failure_threshold=3, timeout=1)
        
        def failing_func():
            raise ValueError("Fail")
        
        for _ in range(3):
            try:
                breaker.call(failing_func)
            except ValueError:
                pass
        
        assert breaker.state.value == "open"
    
    def test_circuit_rejects_when_open(self):
        breaker = CircuitBreaker(failure_threshold=2, timeout=10)
        
        def failing_func():
            raise ValueError("Fail")
        
        for _ in range(2):
            try:
                breaker.call(failing_func)
            except ValueError:
                pass
        
        with pytest.raises(CircuitOpenError):
            breaker.call(failing_func)
    
    def test_circuit_half_open_after_timeout(self):
        breaker = CircuitBreaker(failure_threshold=2, timeout=0.5)
        
        def failing_func():
            raise ValueError("Fail")
        
        for _ in range(2):
            try:
                breaker.call(failing_func)
            except ValueError:
                pass
        
        time.sleep(0.6)
        
        try:
            breaker.call(failing_func)
        except ValueError:
            pass
        
        assert breaker.state.value in ["half_open", "open"]
    
    def test_circuit_closes_after_success_threshold(self):
        breaker = CircuitBreaker(failure_threshold=2, success_threshold=2, timeout=0.5)
        
        def failing_func():
            raise ValueError("Fail")
        
        def success_func():
            return "success"
        
        for _ in range(2):
            try:
                breaker.call(failing_func)
            except ValueError:
                pass
        
        time.sleep(0.6)
        
        for _ in range(2):
            breaker.call(success_func)
        
        assert breaker.state.value == "closed"


class TestRateLimiter:
    """Test rate limiter"""
    
    def test_allows_calls_within_limit(self):
        limiter = RateLimiter(calls=5, period=1.0)
        
        for _ in range(5):
            assert limiter.acquire() is True
    
    def test_blocks_calls_over_limit(self):
        limiter = RateLimiter(calls=3, period=1.0)
        
        for _ in range(3):
            limiter.acquire()
        
        assert limiter.acquire() is False
    
    def test_tokens_refill_over_time(self):
        limiter = RateLimiter(calls=2, period=0.5)
        
        limiter.acquire()
        limiter.acquire()
        assert limiter.acquire() is False
        
        time.sleep(0.3)
        assert limiter.acquire() is True
    
    def test_wait_time_calculation(self):
        limiter = RateLimiter(calls=2, period=1.0)
        
        limiter.acquire()
        limiter.acquire()
        
        wait = limiter.wait_time()
        assert wait > 0


class TestRateLimitDecorator:
    """Test rate limit decorator"""
    
    def test_rate_limit_allows_within_limit(self):
        @rate_limit(calls=3, period=1.0)
        def limited_func():
            return "success"
        
        for _ in range(3):
            assert limited_func() == "success"
    
    def test_rate_limit_raises_over_limit(self):
        @rate_limit(calls=2, period=1.0)
        def limited_func():
            return "success"
        
        limited_func()
        limited_func()
        
        with pytest.raises(RateLimitError):
            limited_func()


class TestTimeoutDecorator:
    """Test timeout decorator"""
    
    def test_completes_within_timeout(self):
        @timeout(1.0)
        def fast_func():
            return "success"
        
        result = fast_func()
        assert result == "success"
    
    def test_raises_on_timeout(self):
        @timeout(0.5)
        def slow_func():
            time.sleep(1.0)
            return "success"
        
        with pytest.raises(TimeoutError):
            slow_func()


class TestFallbackDecorator:
    """Test fallback decorator"""
    
    def test_uses_primary_when_successful(self):
        def primary():
            return "primary"
        
        def fallback1():
            return "fallback1"
        
        @fallback(fallback1)
        def func():
            return primary()
        
        assert func() == "primary"
    
    def test_uses_fallback_on_primary_failure(self):
        def primary():
            raise ValueError("Primary failed")
        
        def fallback1():
            return "fallback1"
        
        @fallback(fallback1)
        def func():
            return primary()
        
        assert func() == "fallback1"
    
    def test_tries_multiple_fallbacks(self):
        def primary():
            raise ValueError("Primary failed")
        
        def fallback1():
            raise ValueError("Fallback1 failed")
        
        def fallback2():
            return "fallback2"
        
        @fallback(fallback1, fallback2)
        def func():
            return primary()
        
        assert func() == "fallback2"
    
    def test_raises_last_error_when_all_fail(self):
        def primary():
            raise ValueError("Primary failed")
        
        def fallback1():
            raise TypeError("Fallback failed")
        
        @fallback(fallback1)
        def func():
            return primary()
        
        with pytest.raises(TypeError):
            func()


class TestCircuitBreakerDecorator:
    """Test circuit breaker decorator"""
    
    def test_decorator_creates_breaker(self):
        @circuit_breaker(failure_threshold=3)
        def func():
            return "success"
        
        assert hasattr(func, 'circuit_breaker')
        assert isinstance(func.circuit_breaker, CircuitBreaker)
    
    def test_decorator_opens_circuit(self):
        @circuit_breaker(failure_threshold=2, timeout=10)
        def failing_func():
            raise ValueError("Fail")
        
        for _ in range(2):
            try:
                failing_func()
            except ValueError:
                pass
        
        with pytest.raises(CircuitOpenError):
            failing_func()


class TestCombinedDecorators:
    """Test combining multiple decorators"""
    
    def test_retry_with_circuit_breaker(self):
        call_count = [0]
        
        @retry(max_attempts=2, base_delay=0.1)
        @circuit_breaker(failure_threshold=5, timeout=1)
        def func():
            call_count[0] += 1
            if call_count[0] < 2:
                raise ValueError("Fail")
            return "success"
        
        result = func()
        assert result == "success"
        assert call_count[0] == 2
    
    def test_rate_limit_with_retry(self):
        @rate_limit(calls=10, period=1)
        @retry(max_attempts=2, base_delay=0.1)
        def func():
            return "success"
        
        result = func()
        assert result == "success"


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
