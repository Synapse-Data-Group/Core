# Changelog

All notable changes to Smart Resilience will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [0.1.0] - 2026-01-10

### Added
- Initial release of Smart Resilience
- Basic resilience primitives (zero dependencies):
  - `@retry` decorator with multiple backoff strategies
  - `@circuit_breaker` decorator with state management
  - `@rate_limit` decorator using token bucket algorithm
  - `@timeout` decorator for execution time limits
  - `@fallback` decorator for fallback chains
- Cognitive-aware primitives (optional CLM/MEO integration):
  - `@cognitive_retry` - Adapts retry behavior based on cognitive load
  - `@memory_circuit_breaker` - Learns from failure patterns
  - `@adaptive_backoff` - Intelligent backoff timing
- Backoff strategies:
  - Constant, Linear, Exponential, Fibonacci, Jitter, Cognitive
- Thread-safe implementations
- Comprehensive test suite (pytest)
- Example scripts for basic and cognitive usage
- Full documentation (README, QUICKSTART, CHANGELOG)

### Features
- Zero external dependencies for basic primitives
- Optional cognitive features with CLM and MEO
- Composable decorators (stack multiple layers)
- Production-ready with <100μs overhead
- Pure Python implementation
- Sovereign code philosophy

### Documentation
- README.md with full feature documentation
- QUICKSTART.md for 5-minute tutorial
- examples/basic_usage.py for basic patterns
- examples/cognitive_usage.py for cognitive features
- Comprehensive inline documentation

### Testing
- 50+ unit tests covering all primitives
- Test coverage for edge cases and error conditions
- Integration tests for combined decorators

## [Unreleased]

### Planned
- Async/await support for all decorators
- Metrics export (Prometheus format)
- Custom backoff strategies
- Circuit breaker state persistence
- Advanced learning algorithms for memory circuit breaker
- Performance benchmarks
- Additional examples for common use cases
