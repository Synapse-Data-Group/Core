from council_framework import DebateSystem, Agent, Tool
import time


class ResearchTool(Tool):
    def __init__(self):
        super().__init__("research_001", "Research Tool")
    
    def execute(self, topic: str) -> str:
        return f"Research findings on '{topic}': Multiple studies support this approach"


class CalculatorTool(Tool):
    def __init__(self):
        super().__init__("calc_001", "Calculator Tool")
    
    def execute(self, expression: str) -> str:
        try:
            result = eval(expression)
            return f"Calculation: {expression} = {result}"
        except:
            return "Invalid calculation"


def demonstrate_agent_lifecycle():
    print("\n" + "="*80)
    print("COUNCIL FRAMEWORK - ADVANCED EXAMPLE")
    print("Demonstrating Agent Lifecycle Management")
    print("="*80 + "\n")
    
    problem = "Should we invest in AI research, renewable energy, or healthcare infrastructure?"
    
    debate = DebateSystem(problem, moderator_strategy="analytical")
    
    agent1 = debate.create_agent(
        "Dr. Tech",
        personality={
            "bias": "optimistic",
            "creativity": 0.9,
            "aggressiveness": 0.7,
            "defensiveness": 0.6,
            "supportiveness": 0.4
        }
    )
    
    agent2 = debate.create_agent(
        "Prof. Cautious",
        personality={
            "bias": "pessimistic",
            "creativity": 0.2,
            "aggressiveness": 0.9,
            "defensiveness": 0.8,
            "supportiveness": 0.1
        }
    )
    
    agent3 = debate.create_agent(
        "Dr. Data",
        personality={
            "bias": "analytical",
            "creativity": 0.5,
            "aggressiveness": 0.4,
            "defensiveness": 0.5,
            "supportiveness": 0.8
        }
    )
    
    research_tool = ResearchTool()
    calc_tool = CalculatorTool()
    
    debate.create_tool_for_agent(agent1.agent_id, research_tool)
    debate.create_tool_for_agent(agent3.agent_id, calc_tool)
    
    print("\n--- Running initial debate with 3 agents ---")
    result = debate.run_debate(max_rounds=2)
    
    print("\n" + "="*80)
    print("MID-DEBATE AGENT MANAGEMENT")
    print("="*80)
    
    agent4 = debate.create_agent(
        "Mx. Mediator",
        personality={
            "bias": "balanced",
            "creativity": 0.6,
            "aggressiveness": 0.3,
            "defensiveness": 0.4,
            "supportiveness": 0.9
        }
    )
    
    print(f"\nTotal agents now: {len(debate.agents)}")
    
    print(f"\nRemoving tool from {agent1.name}...")
    debate.remove_tool_from_agent(agent1.agent_id, research_tool.tool_id)
    
    print(f"\nKilling agent: {agent2.name}")
    debate.kill_agent(agent2.agent_id)
    print(f"Active agents remaining: {len(debate.agents)}")
    
    print("\n" + "="*80)
    print("FINAL STATISTICS")
    print("="*80)
    print(f"Duration: {result['duration_seconds']:.2f} seconds")
    print(f"Total Proposals: {result['total_proposals']}")
    print(f"Total Messages: {result['total_messages']}")
    
    if result['final_decision']:
        print(f"\nFinal Decision: {result['final_decision']['decision']}")
        print(f"Winning Score: {result['final_decision']['winning_proposal']['score']:.1f}")
    
    print("\n" + "="*80)
    print("AGENT PERFORMANCE")
    print("="*80)
    for stats in result['agent_stats']:
        print(f"\n{stats['name']} ({'ACTIVE' if stats['is_active'] else 'INACTIVE'}):")
        print(f"  Proposals: {stats['proposals_made']}")
        print(f"  Challenges: {stats['challenges_made']}")
        print(f"  Rebuttals: {stats['rebuttals_made']}")
        print(f"  Score: {stats['score']:.1f}")
        print(f"  Tools: {stats['tools_count']}")
    
    debate.export_debate("debate_advanced_results.json")
    
    return debate


def demonstrate_multiple_debates():
    print("\n\n" + "="*80)
    print("MULTIPLE DEBATE SCENARIOS")
    print("="*80 + "\n")
    
    scenarios = [
        {
            "problem": "How to reduce carbon emissions by 50% in 10 years?",
            "strategy": "aggressive",
            "agents": [
                ("Innovator", {"bias": "optimistic", "creativity": 0.9, "aggressiveness": 0.8}),
                ("Realist", {"bias": "pessimistic", "creativity": 0.3, "aggressiveness": 0.7}),
                ("Scientist", {"bias": "analytical", "creativity": 0.6, "aggressiveness": 0.5})
            ]
        },
        {
            "problem": "Should we implement a 4-day work week?",
            "strategy": "conservative",
            "agents": [
                ("HR Director", {"bias": "balanced", "creativity": 0.5, "aggressiveness": 0.4}),
                ("CFO", {"bias": "pessimistic", "creativity": 0.2, "aggressiveness": 0.6}),
                ("Employee Rep", {"bias": "optimistic", "creativity": 0.7, "aggressiveness": 0.5})
            ]
        }
    ]
    
    results = []
    
    for idx, scenario in enumerate(scenarios, 1):
        print(f"\n{'='*80}")
        print(f"SCENARIO {idx}: {scenario['problem']}")
        print(f"{'='*80}\n")
        
        debate = DebateSystem(scenario['problem'], moderator_strategy=scenario['strategy'])
        
        for agent_name, personality in scenario['agents']:
            debate.create_agent(agent_name, personality)
        
        result = debate.run_debate(max_rounds=1)
        results.append(result)
        
        print(f"\nScenario {idx} Winner: {result['final_decision']['decision']}")
        print(f"Score: {result['final_decision']['winning_proposal']['score']:.1f}")
    
    return results


if __name__ == "__main__":
    debate1 = demonstrate_agent_lifecycle()
    
    results = demonstrate_multiple_debates()
    
    print("\n\n" + "="*80)
    print("ALL SCENARIOS COMPLETED")
    print("="*80)
    print(f"Total debates run: {len(results) + 1}")
