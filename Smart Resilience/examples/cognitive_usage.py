"""
Cognitive-aware resilience examples (SYNAPSE INNOVATION)

Demonstrates the unique twist: resilience primitives that adapt based on
cognitive load (CLM) and learned patterns (MEO).

Requirements:
    pip install cognitive-load-monitor
    pip install synapse-meo
"""

import time
import random


try:
    from cognitive_load_monitor import CognitiveLoadMonitor
    CLM_AVAILABLE = True
except ImportError:
    print("⚠ cognitive-load-monitor not installed")
    print("Install with: pip install cognitive-load-monitor")
    CLM_AVAILABLE = False

try:
    from meo import WisdomOrchestrator
    MEO_AVAILABLE = True
except ImportError:
    print("⚠ synapse-meo not installed")
    print("Install with: pip install synapse-meo")
    MEO_AVAILABLE = False

from smart_resilience import (
    cognitive_retry,
    memory_circuit_breaker,
    adaptive_backoff,
    RetryError,
    CircuitOpenError
)


print("=" * 60)
print("COGNITIVE-AWARE RESILIENCE - SYNAPSE INNOVATION")
print("=" * 60)


if CLM_AVAILABLE:
    print("\n1. COGNITIVE-AWARE RETRY")
    print("-" * 60)
    print("Retry behavior adapts based on cognitive load:")
    print("  • High load (>0.7): Longer backoff")
    print("  • Low load (<0.3): Faster retry")
    print("  • Rising load: More conservative strategy")
    print()
    
    monitor = CognitiveLoadMonitor()
    
    @cognitive_retry(clm=monitor, max_attempts=5, adaptive=True)
    def complex_agent_task(task_complexity: float):
        """Simulates an agent task with varying complexity"""
        monitor.record(
            tokens_used=int(1000 * task_complexity),
            tokens_budget=2000,
            reasoning_steps=int(5 * task_complexity),
            latency_ms=int(200 * task_complexity)
        )
        
        if random.random() < 0.6:
            raise Exception("Agent task failed")
        
        return f"Task completed (complexity: {task_complexity})"
    
    print("Scenario A: Low complexity task (fast retry)")
    try:
        result = complex_agent_task(task_complexity=0.2)
        print(f"  ✓ {result}")
    except RetryError as e:
        print(f"  ✗ Failed: {e}")
    
    print("\nScenario B: High complexity task (slower retry)")
    try:
        result = complex_agent_task(task_complexity=0.9)
        print(f"  ✓ {result}")
    except RetryError as e:
        print(f"  ✗ Failed: {e}")
    
    print("\nScenario C: Multiple tasks showing adaptive behavior")
    for i, complexity in enumerate([0.1, 0.3, 0.5, 0.7, 0.9], 1):
        current_load = monitor.get_current_load()
        print(f"  Task {i} (complexity={complexity:.1f}, load={current_load:.2f})")
        try:
            result = complex_agent_task(complexity)
            print(f"    ✓ Success")
        except RetryError:
            print(f"    ✗ Failed after adaptive retries")
        time.sleep(0.5)


if MEO_AVAILABLE:
    print("\n2. MEMORY-AWARE CIRCUIT BREAKER")
    print("-" * 60)
    print("Circuit breaker learns from failure patterns:")
    print("  • Detects recurring failure patterns")
    print("  • Adapts timeout based on history")
    print("  • Pre-opens circuit for predicted failures")
    print()
    
    wisdom = WisdomOrchestrator()
    
    @memory_circuit_breaker(
        meo=wisdom,
        failure_threshold=3,
        timeout=5,
        learn_from_history=True
    )
    def learning_service():
        """Service that circuit breaker learns about"""
        if random.random() < 0.7:
            raise Exception("Service temporarily down")
        return "Service OK"
    
    print("Making 15 calls - watch circuit breaker learn:")
    for i in range(15):
        try:
            result = learning_service()
            print(f"  Call {i+1:2d}: ✓ {result}")
        except CircuitOpenError:
            breaker = learning_service.circuit_breaker
            print(f"  Call {i+1:2d}: ⚠ Circuit OPEN (timeout: {breaker.timeout:.1f}s)")
        except Exception as e:
            breaker = learning_service.circuit_breaker
            print(f"  Call {i+1:2d}: ✗ Failed (failures: {breaker.failure_count})")
        time.sleep(0.5)


if CLM_AVAILABLE and MEO_AVAILABLE:
    print("\n3. ADAPTIVE BACKOFF (CLM + MEO)")
    print("-" * 60)
    print("Backoff timing adapts to both cognitive load and learned patterns")
    print()
    
    @adaptive_backoff(clm=monitor, meo=wisdom, strategy="cognitive")
    def intelligent_operation():
        """Operation with intelligent backoff"""
        return "Operation complete"
    
    print("Testing adaptive backoff with varying load:")
    for i in range(5):
        monitor.record(
            tokens_used=500 + i * 300,
            tokens_budget=2000,
            reasoning_steps=3 + i,
            latency_ms=100 + i * 50
        )
        
        load = monitor.get_current_load()
        start = time.time()
        result = intelligent_operation()
        elapsed = time.time() - start
        
        print(f"  Call {i+1}: Load={load:.2f}, Backoff={elapsed:.3f}s")


print("\n4. PRODUCTION EXAMPLE: SMART LLM ROUTER")
print("-" * 60)
print("Combining all cognitive primitives for production LLM calls")
print()

if CLM_AVAILABLE and MEO_AVAILABLE:
    @cognitive_retry(clm=monitor, max_attempts=3, adaptive=True)
    @memory_circuit_breaker(meo=wisdom, failure_threshold=5, learn_from_history=True)
    @adaptive_backoff(clm=monitor, strategy="cognitive")
    def smart_llm_call(prompt: str, model: str = "gpt-4"):
        """Production LLM call with full cognitive awareness"""
        tokens = len(prompt.split()) * 1.3
        
        monitor.record(
            tokens_used=int(tokens),
            tokens_budget=8000,
            reasoning_steps=5,
            latency_ms=random.randint(200, 800)
        )
        
        if random.random() < 0.3:
            raise Exception("LLM API error")
        
        return {
            "model": model,
            "response": f"Response to: {prompt[:30]}...",
            "tokens": int(tokens),
            "load": monitor.get_current_load()
        }
    
    print("Making smart LLM calls:")
    prompts = [
        "Simple question",
        "Medium complexity analysis task",
        "Very complex multi-step reasoning problem with many constraints"
    ]
    
    for i, prompt in enumerate(prompts, 1):
        try:
            result = smart_llm_call(prompt)
            print(f"  Call {i}: ✓ Model={result['model']}, Load={result['load']:.2f}")
        except Exception as e:
            print(f"  Call {i}: ✗ {type(e).__name__}")
        time.sleep(0.5)


print("\n" + "=" * 60)
print("KEY INNOVATION: Resilience that THINKS")
print("=" * 60)
print("""
Traditional retry logic is blind:
  • Fixed retry counts
  • Static backoff timing
  • No awareness of system state

Smart Resilience is cognitive:
  ✓ Adapts to cognitive load (CLM)
  ✓ Learns from patterns (MEO)
  ✓ Predicts failures before they happen
  ✓ Optimizes retry timing automatically
  ✓ Self-improving over time

This is the Synapse difference.
""")

if not CLM_AVAILABLE or not MEO_AVAILABLE:
    print("\n⚠ Install optional dependencies to see full cognitive features:")
    if not CLM_AVAILABLE:
        print("  pip install cognitive-load-monitor")
    if not MEO_AVAILABLE:
        print("  pip install synapse-meo")
