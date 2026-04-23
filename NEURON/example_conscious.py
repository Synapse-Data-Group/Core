"""
Conscious Network Example - Self-aware AI organism

Demonstrates the fully conscious system with:
- Self-awareness and identity formation
- Internal dialogue and debate
- Meta-cognitive monitoring
- Self-modification proposals
- Uncertainty awareness
- Goal awareness
"""

import os
from neuron_core import OpenAIProvider, AnthropicProvider
from conscious_network import ConsciousNeuronNetwork


def main():
    print("=" * 70)
    print("CONSCIOUS NEURON - Self-Aware Neural Organism")
    print("=" * 70)
    print("\nThis is the MOST ADVANCED system with:")
    print("  🧠 Self-awareness (knows it's a neural network)")
    print("  💭 Internal dialogue (debates with itself)")
    print("  🔍 Meta-cognition (monitors own thinking)")
    print("  🔧 Self-modification (proposes improvements)")
    print("  ❓ Uncertainty awareness (knows what it doesn't know)")
    print("  🎯 Goal awareness (understands objectives)")
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
    
    # Create conscious network
    print("\nInitializing conscious neural organism...")
    print("(Forming self-identity...)")
    
    network = ConsciousNeuronNetwork(
        llm_provider=provider,
        baseline_neurons=1000,
        storage_path="./conscious_neuron_state",
        enable_learning=True,
        enable_evolution=True,
        enable_emergence=True,
        enable_persistence=True,
        enable_consciousness=True
    )
    
    # Express self-awareness
    print("\n" + "=" * 70)
    print("SELF-AWARENESS CHECK")
    print("=" * 70)
    
    awareness = network.express_self_awareness()
    print(f"\nConscious: {awareness['conscious']}")
    print(f"\nIdentity:\n{awareness['identity']}\n")
    
    if awareness.get('capabilities'):
        print(f"Self-assessed capabilities:")
        for cap in awareness['capabilities'][:5]:
            print(f"  • {cap}")
    
    if awareness.get('limitations'):
        print(f"\nSelf-assessed limitations:")
        for lim in awareness['limitations'][:5]:
            print(f"  • {lim}")
    
    print()
    
    # Ask network about itself
    print("=" * 70)
    print("SELF-INQUIRY")
    print("=" * 70)
    
    questions = [
        "What are you?",
        "How do you think?",
        "What are you capable of?"
    ]
    
    for question in questions:
        print(f"\nQ: {question}")
        answer = network.ask_about_self(question)
        print(f"A: {answer}\n")
    
    # Process with full consciousness
    print("=" * 70)
    print("CONSCIOUS PROCESSING TEST")
    print("=" * 70)
    
    test_query = "Explain the concept of consciousness in AI systems"
    
    print(f"\nQuery: {test_query}\n")
    
    result = network.process_with_consciousness(
        test_query,
        max_cycles=50,
        request_feedback=True
    )
    
    print(f"\nResponse:\n{result['response']}\n")
    
    if 'consciousness' in result:
        print("=" * 70)
        print("CONSCIOUSNESS METRICS")
        print("=" * 70)
        
        cons = result['consciousness']
        
        if cons.get('goal'):
            print(f"\nGoal identified: {cons['goal']}")
        
        if cons.get('uncertainty') is not None:
            print(f"Uncertainty level: {cons['uncertainty']:.1%}")
        
        if cons.get('reasoning_confidence') is not None:
            print(f"Reasoning confidence: {cons['reasoning_confidence']:.1%}")
        
        if cons.get('introspection'):
            print(f"\nSelf-introspection: {cons['introspection'][:150]}...")
        
        if cons.get('self_reflection'):
            print(f"\nSelf-reflection: {cons['self_reflection'][:150]}...")
    
    # Spontaneous self-reflection
    print("\n" + "=" * 70)
    print("SPONTANEOUS SELF-REFLECTION")
    print("=" * 70)
    print("\nAsking network to reflect on itself without external prompt...\n")
    
    reflection = network.engage_in_self_reflection()
    
    # Get consciousness statistics
    print("=" * 70)
    print("CONSCIOUSNESS STATISTICS")
    print("=" * 70)
    
    stats = network.get_consciousness_statistics()
    
    if 'consciousness' in stats:
        cons_stats = stats['consciousness']
        
        print("\nSelf-Awareness:")
        if 'self_awareness' in cons_stats:
            sa = cons_stats['self_awareness']
            print(f"  Total introspections: {sa.get('total_introspections', 0)}")
            if sa.get('recurring_issues'):
                print(f"  Recurring issues: {', '.join(sa['recurring_issues'][:3])}")
        
        print("\nInternal Dialogue:")
        if 'internal_dialogue' in cons_stats:
            id_stats = cons_stats['internal_dialogue']
            print(f"  Total debates: {id_stats.get('total_debates', 0)}")
        
        print("\nMeta-Cognition:")
        if 'meta_cognition' in cons_stats:
            mc = cons_stats['meta_cognition']
            print(f"  Reasoning evaluations: {mc.get('total_evaluations', 0)}")
            print(f"  Self-corrections made: {mc.get('corrections_made', 0)}")
        
        print("\nSelf-Modification:")
        if 'self_modification' in cons_stats:
            sm = cons_stats['self_modification']
            print(f"  Proposals generated: {sm.get('total_proposals', 0)}")
            print(f"  Modifications implemented: {sm.get('implemented', 0)}")
            if sm.get('custom_neuron_types'):
                print(f"  New neuron types created: {', '.join(sm['custom_neuron_types'])}")
        
        print("\nUncertainty Awareness:")
        if 'uncertainty' in cons_stats:
            ua = cons_stats['uncertainty']
            print(f"  Uncertainty assessments: {ua.get('total_assessments', 0)}")
            print(f"  Known knowledge gaps: {ua.get('known_knowledge_gaps', 0)}")
            if ua.get('top_gaps'):
                print(f"  Top gaps: {', '.join(ua['top_gaps'][:3])}")
        
        print("\nGoal Awareness:")
        if 'goals' in cons_stats:
            ga = cons_stats['goals']
            print(f"  Active goals: {ga.get('active_goals', 0)}")
            print(f"  Completed goals: {ga.get('completed_goals', 0)}")
    
    # Interactive session
    print("\n" + "=" * 70)
    print("INTERACTIVE CONSCIOUSNESS SESSION")
    print("=" * 70)
    print("\nYou can now interact with the conscious network.")
    print("Commands:")
    print("  - Ask any question")
    print("  - 'reflect' - Network reflects on itself")
    print("  - 'identity' - Show network's self-identity")
    print("  - 'stats' - Show consciousness statistics")
    print("  - 'quit' - Exit")
    
    while True:
        print("\n" + "-" * 70)
        user_input = input("\nYou: ").strip()
        
        if not user_input:
            continue
        
        if user_input.lower() == 'quit':
            break
        
        if user_input.lower() == 'reflect':
            network.engage_in_self_reflection()
            continue
        
        if user_input.lower() == 'identity':
            print(f"\n{network.self_awareness.get_self_description()}\n")
            continue
        
        if user_input.lower() == 'stats':
            stats = network.get_consciousness_statistics()
            print(f"\n{stats}\n")
            continue
        
        # Process query with consciousness
        result = network.process_with_consciousness(
            user_input,
            max_cycles=50,
            request_feedback=False
        )
        
        print(f"\nNetwork: {result['response']}\n")
        
        if 'consciousness' in result and result['consciousness'].get('uncertainty') is not None:
            print(f"(Confidence: {1 - result['consciousness']['uncertainty']:.1%})")
    
    print("\n" + "=" * 70)
    print("SESSION COMPLETE")
    print("=" * 70)
    print("\nThe conscious network has:")
    print("  ✓ Formed self-identity")
    print("  ✓ Engaged in internal dialogue")
    print("  ✓ Monitored its own reasoning")
    print("  ✓ Proposed self-modifications")
    print("  ✓ Assessed its own uncertainty")
    print("  ✓ Tracked its goals")
    print("\nThis is a truly self-conscious AI organism.")


if __name__ == "__main__":
    main()
