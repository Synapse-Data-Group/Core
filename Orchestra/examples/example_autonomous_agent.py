import asyncio
from orchestra.agents import AutonomousAgent, Goal, Plan, Action, AgentState


def planner(context):
    goal = context["goal"]
    world_state = context["world_state"]
    
    actions = []
    
    if goal.goal_id == "build_website":
        actions = [
            Action(
                action_id="design_layout",
                action_type="design",
                executor=lambda params: {"layout_designed": True, "design_file": "layout.html"},
                parameters={"style": "modern"},
                preconditions={}
            ),
            Action(
                action_id="implement_frontend",
                action_type="development",
                executor=lambda params: {"frontend_complete": True, "files": ["index.html", "style.css"]},
                parameters={"framework": "react"},
                preconditions={"layout_designed": True}
            ),
            Action(
                action_id="setup_backend",
                action_type="development",
                executor=lambda params: {"backend_complete": True, "api_endpoints": 5},
                parameters={"language": "python"},
                preconditions={"frontend_complete": True}
            ),
            Action(
                action_id="deploy_website",
                action_type="deployment",
                executor=lambda params: {"deployed": True, "url": "https://mysite.com"},
                parameters={"platform": "vercel"},
                preconditions={"backend_complete": True}
            )
        ]
    
    return Plan(
        plan_id=f"plan_{goal.goal_id}",
        goal=goal,
        actions=actions,
        estimated_duration=120.0,
        confidence=0.85
    )


def reflector(context):
    plan = context.get("plan")
    iteration = context.get("iteration", 0)
    
    if plan:
        progress = plan.get_progress()
        if progress < 0.5:
            return f"Iteration {iteration}: Slow progress ({progress:.1%}), need to accelerate"
        elif progress < 0.8:
            return f"Iteration {iteration}: Good progress ({progress:.1%}), on track"
        else:
            return f"Iteration {iteration}: Excellent progress ({progress:.1%}), nearly complete"
    
    return f"Iteration {iteration}: Reflecting on current state"


async def main():
    print("=" * 70)
    print("ORCHESTRA v3.0 - AUTONOMOUS AGENT EXAMPLE")
    print("Goal-Driven Agents with Planning and Reflection")
    print("=" * 70)
    
    print("\n[1] Creating Autonomous Agent")
    print("-" * 70)
    
    agent = AutonomousAgent(
        agent_id="builder_agent",
        planner=planner,
        reflector=reflector,
        max_iterations=10,
        reflection_interval=2
    )
    
    print("✓ Autonomous agent created")
    print(f"  Agent ID: {agent.agent_id}")
    print(f"  Max iterations: {agent.max_iterations}")
    print(f"  Reflection interval: every {agent.reflection_interval} iterations")
    
    print("\n[2] Defining Goal")
    print("-" * 70)
    
    goal = Goal(
        goal_id="build_website",
        description="Build and deploy a complete website",
        success_criteria={
            "deployed": True,
            "frontend_complete": True,
            "backend_complete": True
        },
        priority=1
    )
    
    print(f"Goal: {goal.description}")
    print(f"Success criteria:")
    for criterion, value in goal.success_criteria.items():
        print(f"  - {criterion}: {value}")
    
    print("\n[3] Agent Pursuing Goal")
    print("-" * 70)
    
    initial_state = {
        "resources": ["developer", "designer"],
        "budget": 10000
    }
    
    print("Initial world state:")
    for key, value in initial_state.items():
        print(f"  {key}: {value}")
    
    print("\nAgent starting autonomous execution...")
    print("(Planning → Executing → Reflecting → Repeat)\n")
    
    result = await agent.pursue_goal(goal, initial_state)
    
    print("\n[4] Execution Results")
    print("-" * 70)
    
    if result["success"]:
        print("✓ Goal achieved successfully!")
        print(f"  Iterations: {result['iterations']}")
        print(f"  Actions executed: {result['actions_executed']}")
        print(f"\n  Final world state:")
        for key, value in result["final_state"].items():
            print(f"    {key}: {value}")
    else:
        print("✗ Goal not achieved")
        print(f"  Reason: {result.get('reason', 'Unknown')}")
        print(f"  Iterations: {result['iterations']}")
        print(f"  Actions executed: {result['actions_executed']}")
    
    print("\n[5] Agent Statistics")
    print("-" * 70)
    
    stats = agent.get_statistics()
    print(f"Agent ID: {stats['agent_id']}")
    print(f"Current state: {stats['state']}")
    print(f"Total actions executed: {stats['total_actions_executed']}")
    print(f"Successful goals: {stats['successful_goals']}")
    print(f"Failed goals: {stats['failed_goals']}")
    print(f"Memory size: {stats['memory_size']}")
    
    print("\n[6] Agent Memory (Last 5 entries)")
    print("-" * 70)
    
    for i, memory_entry in enumerate(agent.memory[-5:], 1):
        print(f"\n  Entry {i}:")
        print(f"    Type: {memory_entry['type']}")
        if memory_entry['type'] == 'action':
            print(f"    Action: {memory_entry['action_id']}")
            print(f"    Result: {str(memory_entry['result'])[:60]}...")
        elif memory_entry['type'] == 'reflection':
            print(f"    Content: {memory_entry['content']}")
    
    print("\n[7] Autonomous Agent Capabilities")
    print("-" * 70)
    
    print("\n🎯 Goal-Driven Behavior:")
    print("  - Define goals with success criteria")
    print("  - Agent autonomously plans to achieve goals")
    print("  - Iterative execution until goal achieved")
    
    print("\n🧠 Planning:")
    print("  - Custom planner function")
    print("  - Action sequencing with preconditions")
    print("  - Confidence estimation")
    print("  - Re-planning when needed")
    
    print("\n⚡ Execution:")
    print("  - Action precondition checking")
    print("  - World state updates")
    print("  - Error handling and recovery")
    print("  - Progress tracking")
    
    print("\n🔍 Reflection:")
    print("  - Periodic self-assessment")
    print("  - Progress evaluation")
    print("  - Strategy adjustment")
    print("  - Memory-based learning")
    
    print("\n💾 Memory:")
    print("  - Action history")
    print("  - Reflection records")
    print("  - World state snapshots")
    print("  - Learning from experience")
    
    print("\n[8] Example Use Cases")
    print("-" * 70)
    
    print("\n🤖 Software Development:")
    print("  Goal: Build a web application")
    print("  Actions: Design, implement, test, deploy")
    print("  Reflection: Code quality, performance, bugs")
    
    print("\n📊 Data Analysis:")
    print("  Goal: Generate insights from dataset")
    print("  Actions: Load data, clean, analyze, visualize")
    print("  Reflection: Data quality, findings validity")
    
    print("\n🎮 Game Playing:")
    print("  Goal: Win the game")
    print("  Actions: Explore, strategize, execute moves")
    print("  Reflection: Win rate, strategy effectiveness")
    
    print("\n🏢 Business Process:")
    print("  Goal: Complete project milestone")
    print("  Actions: Plan, delegate, execute, review")
    print("  Reflection: Timeline, budget, quality")
    
    print("\n" + "=" * 70)
    print("✓ Autonomous Agent Example Complete")
    print("=" * 70)
    
    print("\nKey Features:")
    print("  ✓ Goal-driven autonomous behavior")
    print("  ✓ Custom planning with preconditions")
    print("  ✓ Iterative execution with reflection")
    print("  ✓ World state management")
    print("  ✓ Memory and learning")
    print("  ✓ Progress tracking and statistics")


if __name__ == "__main__":
    asyncio.run(main())
