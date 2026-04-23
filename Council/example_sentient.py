from sentient_debate_system import SentientDebateSystem, Tool


class AnalysisTool(Tool):
    def execute(self, data: str) -> str:
        return f"Analysis: {data} shows measurable patterns"


def main():
    print("\n" + "="*80)
    print("SENTIENT COUNCIL FRAMEWORK - DEMONSTRATION")
    print("="*80 + "\n")
    
    problem = "How should we allocate resources to maximize innovation while managing risk?"
    
    debate = SentientDebateSystem(problem, moderator_strategy="adaptive")
    
    alice = debate.create_agent("Alice")
    bob = debate.create_agent("Bob")
    carol = debate.create_agent("Carol")
    
    analysis_tool = AnalysisTool("tool_001", "Analysis Tool")
    debate.create_tool_for_agent(carol.agent_id, analysis_tool)
    
    print("\n" + "="*80)
    print("RUNNING FIRST DEBATE - Agents learning from scratch")
    print("="*80)
    
    result1 = debate.run_debate(max_rounds=2)
    
    print("\n" + "="*80)
    print("FIRST DEBATE SUMMARY")
    print("="*80)
    print(f"Duration: {result1['duration_seconds']:.2f} seconds")
    print(f"Winner: {result1['final_decision']['decision']}")
    print(f"Confidence: {result1['final_decision']['confidence']:.1%}")
    
    print("\n" + "="*80)
    print("AGENT LEARNING STATISTICS")
    print("="*80)
    for stats in result1['agent_stats']:
        print(f"\n{stats['name']}:")
        print(f"  Score: {stats['current_score']:.1f}")
        print(f"  Win Rate: {stats['win_rate']:.1%}")
        print(f"  Learned Strategies: {stats['exploration_rate']:.3f} exploration")
        print(f"  Memory Size: {stats['memory_size']} experiences")
        print(f"  Personality Evolution:")
        for trait in ['creativity', 'boldness', 'aggressiveness']:
            print(f"    {trait}: {stats['personality'].get(trait, 0):.2f}")
    
    debate.save_agent_memories("./memories")
    debate.export_debate("debate_sentient_1.json")
    
    print("\n\n" + "="*80)
    print("RUNNING SECOND DEBATE - Agents using learned knowledge")
    print("="*80)
    
    problem2 = "Should we prioritize short-term gains or long-term sustainability?"
    debate2 = SentientDebateSystem(problem2, moderator_strategy="adaptive")
    
    alice2 = debate2.create_agent("Alice", memory_path="./memories/agent_" + alice.agent_id + "_memory.pkl")
    bob2 = debate2.create_agent("Bob", memory_path="./memories/agent_" + bob.agent_id + "_memory.pkl")
    carol2 = debate2.create_agent("Carol", memory_path="./memories/agent_" + carol.agent_id + "_memory.pkl")
    
    result2 = debate2.run_debate(max_rounds=2)
    
    print("\n" + "="*80)
    print("SECOND DEBATE SUMMARY")
    print("="*80)
    print(f"Duration: {result2['duration_seconds']:.2f} seconds")
    print(f"Winner: {result2['final_decision']['decision']}")
    print(f"Confidence: {result2['final_decision']['confidence']:.1%}")
    
    print("\n" + "="*80)
    print("LEARNING PROGRESSION")
    print("="*80)
    for stats in result2['agent_stats']:
        print(f"\n{stats['name']}:")
        print(f"  Total Debates: {stats['debates_participated']}")
        print(f"  Overall Win Rate: {stats['win_rate']:.1%}")
        print(f"  Lifetime Score: {stats['lifetime_score']:.1f}")
        print(f"  Memory Accumulated: {stats['memory_size']} experiences")
    
    print("\n" + "="*80)
    print("EVOLVING AGENT POPULATION")
    print("="*80)
    
    debate2.evolve_agents()
    
    debate2.export_debate("debate_sentient_2.json")
    debate2.save_agent_memories("./memories")
    
    print("\n" + "="*80)
    print("DEMONSTRATION COMPLETE")
    print("="*80)
    print("\nKey Features Demonstrated:")
    print("  ✓ Agents learn from experience using Q-learning")
    print("  ✓ Persistent memory across debates")
    print("  ✓ Dynamic personality evolution")
    print("  ✓ Generative argument creation (no templates)")
    print("  ✓ Adaptive moderator scoring")
    print("  ✓ Genetic algorithm for trait evolution")
    print("  ✓ Cross-debate knowledge transfer")


if __name__ == "__main__":
    main()
