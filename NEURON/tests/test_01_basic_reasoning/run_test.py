"""
Test 01: Basic Collective Reasoning

Validates that decisions emerge from collective neural reasoning,
not rule-based logic.
"""

import os
import sys
import json
import time
from datetime import datetime
from pathlib import Path

# Load environment variables from .env file
env_path = Path(__file__).parent.parent.parent / '.env'
if env_path.exists():
    with open(env_path) as f:
        for line in f:
            line = line.strip()
            if line and not line.startswith('#') and '=' in line:
                key, value = line.split('=', 1)
                os.environ[key] = value

# Add parent directory to path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../..')))
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from neuron_core import OpenAIProvider
from living_network import LivingNeuronNetwork
from test_logger import TestLogger


def run_test():
    """Execute Test 01: Basic Collective Reasoning"""
    
    print("="*70)
    print("TEST 01: BASIC COLLECTIVE REASONING")
    print("="*70)
    print("\nObjective: Validate reasoning-based decisions vs rule-based logic")
    print()
    
    # Initialize logger
    logger = TestLogger("test_01_basic_reasoning", output_dir=".")
    print("✓ Logger initialized - will capture all conversations, vitals, and behaviors\n")
    
    # Setup
    api_key = os.getenv("OPENAI_API_KEY")
    if not api_key:
        print("ERROR: OPENAI_API_KEY environment variable not set")
        return
    
    provider = OpenAIProvider(api_key=api_key, model="gpt-4o-mini")
    
    print("Initializing network...")
    network = LivingNeuronNetwork(
        llm_provider=provider,
        baseline_neurons=1000,
        storage_path="./test_state",
        enable_learning=True,
        enable_evolution=False,  # Disable for cleaner reasoning test
        enable_emergence=False,
        enable_persistence=False
    )
    
    print(f"Network initialized with {len(network.neurons)} neurons")
    logger.log_vitals(
        cycle=0,
        total_neurons=len(network.neurons),
        active_neurons=0,
        neuron_types={"total": len(network.neurons)},
        metadata={"phase": "initialization"}
    )
    print()
    
    # Test input
    test_query = "What is the relationship between temperature and molecular motion?"
    
    print("="*70)
    print("TEST QUERY")
    print("="*70)
    print(f"\n{test_query}\n")
    
    # Execute with logging
    start_time = time.time()
    
    # Wrap network to intercept LLM calls for logging
    original_complete = provider.complete
    def logged_complete(prompt, max_tokens=500, temperature=0.7):
        print("\n" + "="*70)
        print("LLM CALL")
        print("="*70)
        print(f"\nPROMPT (max_tokens={max_tokens}, temp={temperature}):")
        print("-"*70)
        print(prompt)
        print("-"*70)
        
        response = original_complete(prompt, max_tokens, temperature)
        
        print(f"\nRESPONSE:")
        print("-"*70)
        print(response)
        print("-"*70)
        print("="*70 + "\n")
        
        logger.log_conversation(
            conversation_type="llm_reasoning",
            prompt=prompt,
            response=response,
            metadata={"max_tokens": max_tokens, "temperature": temperature}
        )
        return response
    provider.complete = logged_complete
    
    try:
        result = network.process_with_learning(
            test_query,
            max_cycles=50,
            request_feedback=False
        )
    except Exception as e:
        print(f"\n✗ ERROR during processing: {e}")
        import traceback
        traceback.print_exc()
        return False
    
    elapsed = time.time() - start_time
    
    # Validate result is a dict
    if not isinstance(result, dict):
        print(f"\n✗ ERROR: process_with_learning returned {type(result)} instead of dict")
        return False
    
    # Log final vitals
    logger.log_vitals(
        cycle=result.get('cycles', 0),
        total_neurons=len(network.neurons),
        active_neurons=len(result.get('active_neurons', [])),
        neuron_types={"active": len(result.get('active_neurons', [])), "total": len(network.neurons)},
        metadata={"phase": "completion"}
    )
    
    # Display results
    print("="*70)
    print("RESPONSE")
    print("="*70)
    print(f"\n{result.get('response', 'No response')}\n")
    
    print("="*70)
    print("PROCESSING METRICS")
    print("="*70)
    print(f"Processing time: {elapsed:.2f}s")
    print(f"Cycles: {result.get('cycles', 0)}")
    print(f"Active neurons: {len(result.get('active_neurons', []))}")
    print(f"Total neurons: {len(network.neurons)}")
    print()
    
    # Analyze reasoning traces
    print("="*70)
    print("REASONING ANALYSIS")
    print("="*70)
    
    decision_stats = network.collective_reasoning.get_decision_statistics()
    
    print(f"\nTotal decisions made: {decision_stats.get('total_decisions', 0)}")
    print(f"Decision types: {decision_stats.get('decision_types', {})}")
    
    # Log all decisions as behaviors
    if decision_stats.get('recent_decisions'):
        print("\nRecent decisions with reasoning:")
        for i, decision in enumerate(decision_stats['recent_decisions'][-3:], 1):
            print(f"\n{i}. {decision.get('decision_type', 'unknown').upper()}")
            print(f"   Reasoning: {decision.get('reasoning', 'N/A')[:150]}...")
            print(f"   Confidence: {decision.get('confidence', 0):.2f}")
            
            # Log each decision as behavior
            logger.log_behavior(
                behavior_type=decision.get('decision_type', 'unknown'),
                action=str(decision.get('action', 'N/A')),
                reasoning=decision.get('reasoning', 'N/A'),
                confidence=decision.get('confidence', 0.0),
                metadata=decision.get('metadata', {})
            )
    
    # Validation
    print("\n" + "="*70)
    print("VALIDATION")
    print("="*70)
    
    validations = {
        'has_reasoning_traces': False,
        'no_rule_patterns': True,
        'coherent_response': False,
        'decisions_with_rationale': False
    }
    
    # Check for reasoning traces
    if decision_stats.get('total_decisions', 0) > 0:
        validations['has_reasoning_traces'] = True
        print("✓ Reasoning traces present")
    else:
        print("✗ No reasoning traces found")
    
    # Check for rule patterns (should not exist)
    recent_decisions = decision_stats.get('recent_decisions', [])
    for decision in recent_decisions:
        reasoning = decision.get('reasoning', '').lower()
        if 'if' in reasoning and 'then' in reasoning:
            validations['no_rule_patterns'] = False
            break
    
    if validations['no_rule_patterns']:
        print("✓ No rule-based patterns detected")
    else:
        print("✗ Rule-based patterns found in reasoning")
    
    # Check response coherence (basic check)
    response = result.get('response', '').lower()
    if len(response) > 50 and ('temperature' in response or 'motion' in response or 'molecular' in response):
        validations['coherent_response'] = True
        print("✓ Response is coherent and on-topic")
    else:
        print(f"✗ Response appears incoherent (length: {len(response)})")
    
    # Check for rationale in decisions
    if recent_decisions and all(d.get('reasoning') for d in recent_decisions):
        validations['decisions_with_rationale'] = True
        print("✓ All decisions include rationale")
    else:
        print("✗ Some decisions missing rationale")
    
    # Overall result
    print("\n" + "="*70)
    print("TEST RESULT")
    print("="*70)
    
    passed = all(validations.values())
    
    if passed:
        print("\n✓ TEST PASSED")
        print("\nThe network demonstrates reasoning-based decision-making.")
        print("All decisions include rationale and no rule-based patterns detected.")
    else:
        print("\n✗ TEST FAILED")
        print("\nValidation failures:")
        for check, result in validations.items():
            if not result:
                print(f"  - {check}")
    
    # Save results
    results = {
        'test_id': 'test_01_basic_reasoning',
        'timestamp': datetime.now().isoformat(),
        'query': test_query,
        'response': result.get('response', 'No response'),
        'metrics': {
            'processing_time': elapsed,
            'cycles': result.get('cycles', 0),
            'active_neurons': len(result.get('active_neurons', [])),
            'total_neurons': len(network.neurons)
        },
        'decision_statistics': decision_stats,
        'validations': validations,
        'passed': passed
    }
    
    with open('results.json', 'w') as f:
        json.dump(results, f, indent=2)
    
    # Save comprehensive logs
    print("\n" + "="*70)
    print("SAVING COMPREHENSIVE LOGS")
    print("="*70)
    
    log_files = logger.save_logs()
    
    print("\nLogs saved:")
    for log_type, filepath in log_files.items():
        print(f"  ✓ {log_type}: {filepath}")
    
    log_stats = logger.get_summary_stats()
    print(f"\nLog statistics:")
    print(f"  - Conversations logged: {log_stats['conversations']}")
    print(f"  - Vitals snapshots: {log_stats['vitals_snapshots']}")
    print(f"  - Behaviors logged: {log_stats['behaviors']}")
    print(f"  - Total events: {log_stats['events']}")
    
    # Generate markdown report
    with open('results.md', 'w') as f:
        f.write(f"# Test 01: Basic Collective Reasoning - Results\n\n")
        f.write(f"**Date:** {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n\n")
        f.write(f"**Status:** {'PASSED ✓' if passed else 'FAILED ✗'}\n\n")
        f.write(f"## Query\n\n{test_query}\n\n")
        f.write(f"## Response\n\n{result.get('response', 'No response')}\n\n")
        f.write(f"## Metrics\n\n")
        f.write(f"- Processing time: {elapsed:.2f}s\n")
        f.write(f"- Cycles: {result.get('cycles', 0)}\n")
        f.write(f"- Active neurons: {len(result.get('active_neurons', []))}\n")
        f.write(f"- Total neurons: {len(network.neurons)}\n\n")
        f.write(f"## Decision Analysis\n\n")
        f.write(f"Total decisions: {decision_stats.get('total_decisions', 0)}\n\n")
        
        if recent_decisions:
            f.write(f"### Recent Decisions\n\n")
            for i, decision in enumerate(recent_decisions[-3:], 1):
                f.write(f"**{i}. {decision.get('decision_type', 'unknown').upper()}**\n\n")
                f.write(f"Reasoning: {decision.get('reasoning', 'N/A')}\n\n")
                f.write(f"Confidence: {decision.get('confidence', 0):.2f}\n\n")
        
        f.write(f"## Validations\n\n")
        for check, result in validations.items():
            status = '✓' if result else '✗'
            f.write(f"- {status} {check.replace('_', ' ').title()}\n")
        
        f.write(f"\n## Conclusion\n\n")
        if passed:
            f.write("The network successfully demonstrates reasoning-based decision-making. ")
            f.write("All decisions include rationale and no rule-based patterns were detected.\n")
        else:
            f.write("The test identified issues with reasoning-based decision-making:\n\n")
            for check, result in validations.items():
                if not result:
                    f.write(f"- {check.replace('_', ' ').title()}\n")
    
    print(f"\nResults saved to results.json and results.md")
    print("="*70)
    
    return passed


if __name__ == "__main__":
    success = run_test()
    sys.exit(0 if success else 1)
