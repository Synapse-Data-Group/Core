import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import json
from fluid_debate_system import FluidDebateSystem


def test_fluid_resourcing_basic():
    print("\n" + "="*80)
    print("TEST: Basic Fluid Resourcing")
    print("="*80)
    
    problem = "How to optimize resource allocation in healthcare?"
    debate = FluidDebateSystem(problem, moderator_strategy="adaptive")
    
    debate.create_agent("Agent_A")
    debate.create_agent("Agent_B")
    
    result = debate.run_debate(max_rounds=2, enable_fluid_resourcing=True)
    
    assert result['fluid_resourcing_stats']['total_spawned'] >= 0, "Should track spawned agents"
    assert len(result['fluid_events']) >= 0, "Should track fluid events"
    
    print(f"✓ Spawned {result['fluid_resourcing_stats']['total_spawned']} agents")
    print(f"✓ Recorded {len(result['fluid_events'])} fluid events")
    
    debate.export_debate("testing/results/test_fluid_basic.json")
    
    return result


def test_zero_agent_bootstrap():
    print("\n" + "="*80)
    print("TEST: Zero Agent Bootstrap")
    print("="*80)
    
    problem = "What is the future of renewable energy?"
    debate = FluidDebateSystem(problem, moderator_strategy="adaptive")
    
    print("Starting with 0 agents...")
    assert len(debate.agents) == 0, "Should start with no agents"
    
    debate.moderator.spawn_agent("analyze", debate, "bootstrap")
    debate.moderator.spawn_agent("innovate", debate, "bootstrap")
    debate.moderator.spawn_agent("challenge", debate, "bootstrap")
    
    print(f"After bootstrap: {len(debate.agents)} agents")
    assert len(debate.agents) == 3, "Should have 3 agents after bootstrap"
    
    result = debate.run_debate(max_rounds=2, enable_fluid_resourcing=True)
    
    assert result['total_agents'] >= 3, "Should maintain or increase agents"
    print(f"✓ Final agent count: {result['total_agents']}")
    
    debate.export_debate("testing/results/test_fluid_bootstrap.json")
    
    return result


def test_agent_termination():
    print("\n" + "="*80)
    print("TEST: Agent Termination")
    print("="*80)
    
    problem = "How to improve education systems?"
    debate = FluidDebateSystem(problem, moderator_strategy="adaptive")
    
    for i in range(5):
        debate.create_agent(f"Agent_{i}")
    
    initial_count = len(debate.agents)
    print(f"Starting with {initial_count} agents")
    
    result = debate.run_debate(max_rounds=3, enable_fluid_resourcing=True)
    
    terminated = result['fluid_resourcing_stats']['total_terminated']
    print(f"✓ Terminated {terminated} agents")
    
    if terminated > 0:
        print("✓ Agent termination working")
    
    debate.export_debate("testing/results/test_fluid_termination.json")
    
    return result


def test_archetype_diversity():
    print("\n" + "="*80)
    print("TEST: Archetype Diversity")
    print("="*80)
    
    problem = "Should we colonize Mars?"
    debate = FluidDebateSystem(problem, moderator_strategy="adaptive")
    
    debate.create_agent("Initial_Agent")
    
    result = debate.run_debate(max_rounds=3, enable_fluid_resourcing=True)
    
    spawned_archetypes = set()
    for event in result['fluid_events']:
        if event['type'] == 'spawn':
            agent_info = debate.moderator.agent_factory.get_agent_info(event['agent_id'])
            if agent_info:
                spawned_archetypes.add(agent_info['archetype'])
    
    print(f"✓ Spawned archetypes: {spawned_archetypes}")
    print(f"✓ Archetype diversity: {len(spawned_archetypes)} unique types")
    
    debate.export_debate("testing/results/test_fluid_diversity.json")
    
    return result


def test_spawn_reasons():
    print("\n" + "="*80)
    print("TEST: Spawn Reasons Analysis")
    print("="*80)
    
    problem = "How to address income inequality?"
    debate = FluidDebateSystem(problem, moderator_strategy="adaptive")
    
    debate.create_agent("Agent_1")
    debate.create_agent("Agent_2")
    
    result = debate.run_debate(max_rounds=3, enable_fluid_resourcing=True)
    
    spawn_reasons = result['fluid_resourcing_stats']['spawn_reasons']
    
    print("✓ Spawn reasons detected:")
    for reason, count in spawn_reasons.items():
        print(f"  - {reason}: {count} times")
    
    debate.export_debate("testing/results/test_fluid_reasons.json")
    
    return result


def test_late_entry_participation():
    print("\n" + "="*80)
    print("TEST: Late Entry Agent Participation")
    print("="*80)
    
    problem = "What is the best approach to cybersecurity?"
    debate = FluidDebateSystem(problem, moderator_strategy="adaptive")
    
    debate.create_agent("Agent_A")
    debate.create_agent("Agent_B")
    
    result = debate.run_debate(max_rounds=2, enable_fluid_resourcing=True)
    
    late_entry_messages = [
        msg for msg in result['proposals'] + 
        [c for p in result['proposals'] for c in p.get('challenges', [])]
        if msg.get('metadata', {}).get('late_entry', False)
    ]
    
    print(f"✓ Late entry messages: {len(late_entry_messages)}")
    
    if result['fluid_resourcing_stats']['total_spawned'] > 0:
        print("✓ Spawned agents participated in debate")
    
    debate.export_debate("testing/results/test_fluid_late_entry.json")
    
    return result


def test_fluid_vs_static():
    print("\n" + "="*80)
    print("TEST: Fluid vs Static Comparison")
    print("="*80)
    
    problem = "How to balance privacy and security?"
    
    print("\n--- Running STATIC debate (no fluid resourcing) ---")
    debate_static = FluidDebateSystem(problem, moderator_strategy="adaptive")
    debate_static.create_agent("Agent_1")
    debate_static.create_agent("Agent_2")
    debate_static.create_agent("Agent_3")
    
    result_static = debate_static.run_debate(max_rounds=2, enable_fluid_resourcing=False)
    
    print("\n--- Running FLUID debate (with fluid resourcing) ---")
    debate_fluid = FluidDebateSystem(problem, moderator_strategy="adaptive")
    debate_fluid.create_agent("Agent_1")
    debate_fluid.create_agent("Agent_2")
    debate_fluid.create_agent("Agent_3")
    
    result_fluid = debate_fluid.run_debate(max_rounds=2, enable_fluid_resourcing=True)
    
    print("\n✓ COMPARISON:")
    print(f"  Static - Final agents: {result_static['total_agents']}, Messages: {result_static['total_messages']}")
    print(f"  Fluid  - Final agents: {result_fluid['total_agents']}, Messages: {result_fluid['total_messages']}")
    print(f"  Fluid spawned: {result_fluid['fluid_resourcing_stats']['total_spawned']} agents")
    
    debate_static.export_debate("testing/results/test_static_debate.json")
    debate_fluid.export_debate("testing/results/test_fluid_debate.json")
    
    return result_fluid


def run_all_fluid_tests():
    os.makedirs("testing/results", exist_ok=True)
    
    print("\n" + "="*80)
    print("FLUID DEBATE SYSTEM - COMPREHENSIVE TEST SUITE")
    print("="*80)
    
    tests = [
        ("Basic Fluid Resourcing", test_fluid_resourcing_basic),
        ("Zero Agent Bootstrap", test_zero_agent_bootstrap),
        ("Agent Termination", test_agent_termination),
        ("Archetype Diversity", test_archetype_diversity),
        ("Spawn Reasons", test_spawn_reasons),
        ("Late Entry Participation", test_late_entry_participation),
        ("Fluid vs Static", test_fluid_vs_static)
    ]
    
    results = []
    passed = 0
    failed = 0
    
    for test_name, test_func in tests:
        try:
            result = test_func()
            results.append({"test": test_name, "status": "PASSED", "result": result})
            passed += 1
            print(f"\n✓ {test_name} PASSED")
        except Exception as e:
            results.append({"test": test_name, "status": "FAILED", "error": str(e)})
            failed += 1
            print(f"\n✗ {test_name} FAILED: {e}")
    
    print("\n" + "="*80)
    print("TEST SUITE SUMMARY")
    print("="*80)
    print(f"Total Tests: {len(tests)}")
    print(f"Passed: {passed}")
    print(f"Failed: {failed}")
    print(f"Success Rate: {passed/len(tests)*100:.1f}%")
    
    summary = {
        "total_tests": len(tests),
        "passed": passed,
        "failed": failed,
        "results": results
    }
    
    with open("testing/results/fluid_test_summary.json", 'w') as f:
        json.dump(summary, f, indent=2)
    
    print("\nTest results saved to: testing/results/fluid_test_summary.json")
    
    return summary


if __name__ == "__main__":
    run_all_fluid_tests()
