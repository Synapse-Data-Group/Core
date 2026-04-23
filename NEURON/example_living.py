"""
Living Network Example - Demonstrates true self-evolving organism

This example shows the complete system with:
- Hebbian learning
- Evolutionary algorithms
- Persistent state
- Emergent dynamics
- Feedback integration
"""

import os
from neuron_core import OpenAIProvider, AnthropicProvider
from living_network import LivingNeuronNetwork


def main():
    print("=" * 70)
    print("LIVING NEURON - Self-Evolving Neural Organism")
    print("=" * 70)
    print("\nThis is the COMPLETE system with:")
    print("  ✓ Hebbian learning (connections strengthen/weaken)")
    print("  ✓ Evolutionary algorithms (neurons mutate and evolve)")
    print("  ✓ Persistent state (learns across sessions)")
    print("  ✓ Emergent dynamics (oscillations, synchronization)")
    print("  ✓ Feedback integration (learns from outcomes)")
    print("\n" + "=" * 70 + "\n")
    
    # Choose LLM provider
    print("Available LLM providers:")
    print("  1. OpenAI (GPT-4o-mini)")
    print("  2. Anthropic (Claude)")
    
    choice = input("\nSelect provider (1-2) [1]: ").strip() or "1"
    
    if choice == "1":
        api_key = os.getenv("OPENAI_API_KEY")
        if not api_key:
            api_key = input("Enter OpenAI API key: ").strip()
        provider = OpenAIProvider(api_key=api_key, model="gpt-4o-mini")
    else:
        api_key = os.getenv("ANTHROPIC_API_KEY")
        if not api_key:
            api_key = input("Enter Anthropic API key: ").strip()
        provider = AnthropicProvider(api_key=api_key)
    
    print(f"\n✓ Using {provider.get_provider_name()}")
    
    # Create living network
    print("\nInitializing living neural organism...")
    print("(This will load saved state if available)")
    
    network = LivingNeuronNetwork(
        llm_provider=provider,
        baseline_neurons=1000,
        storage_path="./neuron_research_state",
        enable_learning=True,
        enable_evolution=True,
        enable_emergence=True,
        enable_persistence=True
    )
    
    print("\n" + "=" * 70)
    print("RESEARCH SESSION")
    print("=" * 70)
    print("\nThe network will:")
    print("  1. Process your query")
    print("  2. Learn from feedback")
    print("  3. Evolve neurons based on performance")
    print("  4. Save state for next session")
    print("\nOver multiple sessions, the network IMPROVES.")
    
    # Research queries
    queries = [
        "Explain the concept of emergence in complex systems",
        "How do neural networks learn?",
        "What is the difference between supervised and unsupervised learning?"
    ]
    
    print("\n" + "=" * 70)
    print("QUERY 1: Simple explanation")
    print("=" * 70)
    
    result = network.process_with_learning(
        queries[0],
        max_cycles=50,
        request_feedback=True
    )
    
    print(f"\nResponse:\n{result['response']}\n")
    print(f"Processing time: {result['processing_time']:.2f}s")
    print(f"Cycles: {result['cycles']}")
    
    # Show statistics
    stats = network.get_comprehensive_statistics()
    print("\n" + "=" * 70)
    print("NETWORK STATISTICS")
    print("=" * 70)
    
    print(f"\nNetwork:")
    print(f"  Total neurons: {stats['network']['total_neurons']}")
    print(f"  Interactions: {stats['network']['total_interactions']}")
    
    if 'learning' in stats:
        print(f"\nLearning:")
        print(f"  Hebbian updates: {stats['learning']['hebbian_updates']}")
        print(f"  Potentiated connections: {stats['learning']['potentiated_connections']}")
        print(f"  Depressed connections: {stats['learning']['depressed_connections']}")
    
    if 'evolution' in stats:
        print(f"\nEvolution:")
        print(f"  Generation: {stats['evolution']['generation']}")
        print(f"  Average fitness: {stats['evolution']['average_fitness']:.3f}")
        print(f"  Species count: {stats['evolution']['species_count']}")
    
    if 'emergence' in stats:
        print(f"\nEmergence:")
        print(f"  Synchronized groups: {stats['emergence']['synchronized_groups']}")
        print(f"  Attractor count: {stats['emergence']['attractor_count']}")
        print(f"  Discovered patterns: {stats['emergence']['discovered_patterns']}")
    
    if 'feedback' in stats:
        print(f"\nFeedback:")
        print(f"  Total feedback: {stats['feedback']['total_feedback']}")
        print(f"  Success rate: {stats['feedback']['success_rate']:.1%}")
    
    # Continue with more queries
    print("\n" + "=" * 70)
    print("CONTINUE RESEARCH SESSION")
    print("=" * 70)
    
    continue_session = input("\nContinue with more queries? (yes/no) [yes]: ").strip().lower()
    
    if continue_session != 'no':
        for i, query in enumerate(queries[1:], 2):
            print(f"\n{'='*70}")
            print(f"QUERY {i}: {query[:50]}...")
            print("=" * 70)
            
            result = network.process_with_learning(
                query,
                max_cycles=50,
                request_feedback=True
            )
            
            print(f"\nResponse:\n{result['response']}\n")
    
    # Final statistics
    final_stats = network.get_comprehensive_statistics()
    
    print("\n" + "=" * 70)
    print("FINAL SESSION STATISTICS")
    print("=" * 70)
    
    print(f"\nTotal interactions: {final_stats['network']['total_interactions']}")
    print(f"Session duration: {final_stats['network']['session_duration']:.0f}s")
    
    if 'evolution' in final_stats:
        print(f"\nEvolutionary progress:")
        print(f"  Generations evolved: {final_stats['evolution']['generation']}")
        print(f"  Elite neurons: {final_stats['evolution']['elite_neurons']}")
        print(f"  Weak neurons: {final_stats['evolution']['weak_neurons']}")
    
    if 'learning' in final_stats:
        print(f"\nLearning progress:")
        print(f"  Total weight updates: {final_stats['learning']['hebbian_updates']}")
        print(f"  Average change: {final_stats['learning']['average_weight_change']:.4f}")
    
    print("\n" + "=" * 70)
    print("KEY RESEARCH INSIGHTS")
    print("=" * 70)
    print("""
1. LEARNING: Connections strengthen/weaken based on success
   - Hebbian: "Neurons that fire together, wire together"
   - STDP: Timing-dependent plasticity
   - Reward-based: Successful patterns reinforced

2. EVOLUTION: Neurons mutate and naturally select
   - Weak neurons die
   - Strong neurons reproduce
   - Offspring have mutations
   - New capabilities emerge

3. PERSISTENCE: Network remembers across sessions
   - Connection weights saved
   - Evolutionary history preserved
   - Learned patterns retained
   - Improves over time

4. EMERGENCE: Collective behavior not programmed
   - Oscillatory dynamics
   - Synchronized groups
   - Attractor states
   - Self-organizing criticality

5. FEEDBACK: User input shapes evolution
   - Success → strengthen active neurons
   - Failure → weaken active neurons
   - Adaptive learning rates
   - Continuous improvement

This is a TRUE self-evolving organism.
""")
    
    print("=" * 70)
    print("RESEARCH SESSION COMPLETE")
    print("=" * 70)
    print("\nNetwork state has been saved.")
    print("Next session will continue learning from this point.")
    print("\nFor research: Analyze saved state in ./neuron_research_state/")


if __name__ == "__main__":
    main()
