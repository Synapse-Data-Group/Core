from council_framework import DebateSystem, Agent, Tool


class AnalysisTool(Tool):
    def __init__(self):
        super().__init__("analysis_001", "Data Analysis Tool")
    
    def execute(self, data: str) -> str:
        return f"Analysis result: {data} shows positive trends"


def main():
    print("\n" + "="*80)
    print("COUNCIL FRAMEWORK - BASIC EXAMPLE")
    print("="*80 + "\n")
    
    problem = "How should we allocate a $1M budget for improving customer satisfaction?"
    
    debate = DebateSystem(problem, moderator_strategy="balanced")
    
    alice = debate.create_agent(
        "Alice",
        personality={
            "bias": "optimistic",
            "creativity": 0.8,
            "aggressiveness": 0.6,
            "defensiveness": 0.7,
            "supportiveness": 0.3
        }
    )
    
    bob = debate.create_agent(
        "Bob",
        personality={
            "bias": "pessimistic",
            "creativity": 0.3,
            "aggressiveness": 0.8,
            "defensiveness": 0.5,
            "supportiveness": 0.2
        }
    )
    
    carol = debate.create_agent(
        "Carol",
        personality={
            "bias": "analytical",
            "creativity": 0.5,
            "aggressiveness": 0.5,
            "defensiveness": 0.6,
            "supportiveness": 0.7
        }
    )
    
    analysis_tool = AnalysisTool()
    debate.create_tool_for_agent(carol.agent_id, analysis_tool)
    
    result = debate.run_debate(max_rounds=2)
    
    print("\n" + "="*80)
    print("DEBATE SUMMARY")
    print("="*80)
    print(f"Duration: {result['duration_seconds']:.2f} seconds")
    print(f"Total Proposals: {result['total_proposals']}")
    print(f"Total Messages: {result['total_messages']}")
    print(f"\nWinner: {result['final_decision']['decision']}")
    print(f"Winning Score: {result['final_decision']['winning_proposal']['score']:.1f}")
    
    print("\n" + "="*80)
    print("AGENT STATISTICS")
    print("="*80)
    for stats in result['agent_stats']:
        print(f"\n{stats['name']}:")
        print(f"  Proposals: {stats['proposals_made']}")
        print(f"  Challenges: {stats['challenges_made']}")
        print(f"  Rebuttals: {stats['rebuttals_made']}")
        print(f"  Final Score: {stats['score']:.1f}")
    
    debate.export_debate("debate_results.json")


if __name__ == "__main__":
    main()
