from fluid_debate_system import FluidDebateSystem


def main():
    print("\n" + "="*80)
    print("FLUID DEBATE SYSTEM - CATEGORY-DEFINING DEMONSTRATION")
    print("Moderator Dynamically Spawns and Terminates Agents")
    print("="*80 + "\n")
    
    problem = "How should we balance rapid innovation with safety and ethical considerations in AI development?"
    
    debate = FluidDebateSystem(problem, moderator_strategy="adaptive")
    
    print("Starting with only 2 agents - moderator will spawn more as needed...")
    
    agent1 = debate.create_agent("Initial_Agent_1")
    agent2 = debate.create_agent("Initial_Agent_2")
    
    print(f"\nInitial agent count: {len(debate.agents)}")
    
    result = debate.run_debate(max_rounds=3, enable_fluid_resourcing=True)
    
    print("\n" + "="*80)
    print("FLUID DEBATE SUMMARY")
    print("="*80)
    print(f"Duration: {result['duration_seconds']:.2f} seconds")
    print(f"Final Agent Count: {result['total_agents']}")
    print(f"Winner: {result['final_decision']['decision']}")
    print(f"Confidence: {result['final_decision']['confidence']:.1%}")
    
    print("\n" + "="*80)
    print("FLUID RESOURCING STATISTICS")
    print("="*80)
    
    fluid_stats = result['fluid_resourcing_stats']
    print(f"Total Agents Spawned: {fluid_stats['total_spawned']}")
    print(f"Total Agents Terminated: {fluid_stats['total_terminated']}")
    print(f"Active Spawned Agents: {fluid_stats['currently_active_spawned']}")
    
    if fluid_stats['spawn_reasons']:
        print("\nSpawn Reasons:")
        for reason, count in fluid_stats['spawn_reasons'].items():
            print(f"  {reason}: {count} times")
    
    print("\n" + "="*80)
    print("FLUID EVENTS TIMELINE")
    print("="*80)
    
    for event in result['fluid_events']:
        print(f"\n[{event['timestamp'] - result['duration_seconds']:.2f}s] {event['type'].upper()}")
        print(f"  Agent: {event['agent_name']}")
        print(f"  Phase: {event['phase']}")
        print(f"  Reason: {event['reason']}")
        if 'urgency' in event:
            print(f"  Urgency: {event['urgency']:.2f}")
    
    print("\n" + "="*80)
    print("AGENT PERFORMANCE")
    print("="*80)
    
    for stats in result['agent_stats']:
        print(f"\n{stats['name']}:")
        print(f"  Score: {stats['current_score']:.1f}")
        print(f"  Proposals: {stats['proposals_made']}")
        print(f"  Challenges: {stats['challenges_made']}")
        print(f"  Rebuttals: {stats['rebuttals_made']}")
        print(f"  Active: {stats['is_active']}")
    
    debate.export_debate("fluid_debate_results.json")
    debate.save_agent_memories("./fluid_memories")
    
    print("\n" + "="*80)
    print("DEMONSTRATION COMPLETE")
    print("="*80)
    print("\nKey Innovations Demonstrated:")
    print("  ✓ Moderator detects lack of diversity and spawns innovator")
    print("  ✓ Moderator detects stalemate and spawns mediator")
    print("  ✓ Moderator detects insufficient challenge and spawns devil's advocate")
    print("  ✓ Moderator terminates underperforming agents")
    print("  ✓ Spawned agents immediately participate in debate")
    print("  ✓ Dynamic agent pool optimization during debate")
    print("  ✓ Fluid resourcing based on debate needs, not pre-programming")


def demonstrate_extreme_fluid_resourcing():
    print("\n\n" + "="*80)
    print("EXTREME FLUID RESOURCING - Starting with ZERO agents!")
    print("="*80 + "\n")
    
    problem = "What is the optimal strategy for climate change mitigation?"
    
    debate = FluidDebateSystem(problem, moderator_strategy="adaptive")
    
    print("No initial agents - moderator must spawn everything...")
    print(f"Initial agent count: {len(debate.agents)}")
    
    debate.moderator.spawn_agent("analyze", debate, "bootstrap_debate")
    debate.moderator.spawn_agent("innovate", debate, "bootstrap_debate")
    debate.moderator.spawn_agent("challenge", debate, "bootstrap_debate")
    
    print(f"\nAfter bootstrap: {len(debate.agents)} agents")
    
    result = debate.run_debate(max_rounds=2, enable_fluid_resourcing=True)
    
    print("\n" + "="*80)
    print("EXTREME FLUID RESOURCING RESULTS")
    print("="*80)
    print(f"Final Agent Count: {result['total_agents']}")
    print(f"Total Spawned: {result['fluid_resourcing_stats']['total_spawned']}")
    print(f"Winner: {result['final_decision']['decision']}")
    
    debate.export_debate("extreme_fluid_debate.json")


def demonstrate_targeted_spawning():
    print("\n\n" + "="*80)
    print("TARGETED SPAWNING - Moderator spawns specific roles")
    print("="*80 + "\n")
    
    problem = "Should we implement universal basic income?"
    
    debate = FluidDebateSystem(problem, moderator_strategy="adaptive")
    
    debate.create_agent("Economist")
    debate.create_agent("Sociologist")
    
    print("Starting with 2 agents...")
    print("Moderator will spawn ethicist, analyst, and pragmatist as needed...\n")
    
    result = debate.run_debate(max_rounds=3, enable_fluid_resourcing=True)
    
    print("\n" + "="*80)
    print("TARGETED SPAWNING RESULTS")
    print("="*80)
    
    spawned_archetypes = []
    for event in result['fluid_events']:
        if event['type'] == 'spawn':
            archetype = debate.moderator.agent_factory.get_agent_info(event['agent_id'])
            if archetype:
                spawned_archetypes.append(archetype['archetype'])
    
    print(f"Spawned Archetypes: {', '.join(set(spawned_archetypes))}")
    print(f"Total Agents at End: {result['total_agents']}")
    
    debate.export_debate("targeted_spawning_debate.json")


if __name__ == "__main__":
    main()
    
    print("\n\n" + "="*80)
    print("Running additional demonstrations...")
    print("="*80)
    
    demonstrate_extreme_fluid_resourcing()
    demonstrate_targeted_spawning()
    
    print("\n\n" + "="*80)
    print("ALL FLUID RESOURCING DEMONSTRATIONS COMPLETE")
    print("="*80)
