import asyncio
from orchestra.agents import AgentTeam, CollaborationPattern, MessageBus, AgentMessage


def researcher_agent(task):
    problem = task.get("problem", "")
    return {
        "agent": "researcher",
        "findings": f"Research findings for: {problem}",
        "sources": ["source1", "source2", "source3"],
        "confidence": 0.85
    }


def analyst_agent(task):
    if "subtask_results" in task:
        findings = task["subtask_results"]
        return {
            "agent": "analyst",
            "analysis": f"Analyzed {len(findings)} research findings",
            "insights": ["insight1", "insight2"],
            "recommendation": "Proceed with approach A"
        }
    
    problem = task.get("problem", "")
    return {
        "agent": "analyst",
        "analysis": f"Analysis of: {problem}",
        "metrics": {"accuracy": 0.92, "completeness": 0.88}
    }


def writer_agent(task):
    problem = task.get("problem", "")
    return {
        "agent": "writer",
        "document": f"Written report for: {problem}",
        "pages": 10,
        "format": "markdown"
    }


def reviewer_agent(task):
    problem = task.get("problem", "")
    return {
        "agent": "reviewer",
        "review": f"Reviewed content for: {problem}",
        "approved": True,
        "suggestions": ["Add more examples", "Clarify section 3"]
    }


async def main():
    print("=" * 70)
    print("ORCHESTRA v3.0 - MULTI-AGENT COLLABORATION")
    print("5 Collaboration Patterns for Agent Teams")
    print("=" * 70)
    
    print("\n[1] HIERARCHICAL PATTERN")
    print("-" * 70)
    print("Leader coordinates subordinate agents\n")
    
    hierarchical_team = AgentTeam(
        team_id="research_team",
        pattern=CollaborationPattern.HIERARCHICAL
    )
    
    hierarchical_team.add_agent("leader", analyst_agent, role="coordinator", is_leader=True)
    hierarchical_team.add_agent("researcher1", researcher_agent, role="researcher")
    hierarchical_team.add_agent("researcher2", researcher_agent, role="researcher")
    
    task = {
        "problem": "Analyze market trends for Q4 2024",
        "subtasks": [
            {"id": "research1", "data": {"problem": "Tech sector trends"}},
            {"id": "research2", "data": {"problem": "Finance sector trends"}}
        ]
    }
    
    result = await hierarchical_team.execute_collaborative_task(task)
    
    print(f"✓ Hierarchical execution complete")
    print(f"  Leader: {result['leader']}")
    print(f"  Subtasks completed: {len(result['subtask_results'])}")
    print(f"  Final result: {result['final_result']['recommendation']}")
    
    print("\n[2] PEER-TO-PEER PATTERN")
    print("-" * 70)
    print("All agents work independently on same task\n")
    
    peer_team = AgentTeam(
        team_id="analysis_team",
        pattern=CollaborationPattern.PEER_TO_PEER
    )
    
    peer_team.add_agent("researcher", researcher_agent, role="researcher")
    peer_team.add_agent("analyst", analyst_agent, role="analyst")
    peer_team.add_agent("writer", writer_agent, role="writer")
    
    task = {"problem": "Competitive analysis of AI frameworks"}
    
    result = await peer_team.execute_collaborative_task(task)
    
    print(f"✓ Peer-to-peer execution complete")
    print(f"  Agents participated: {len(result['results'])}")
    for agent_result in result['results']:
        print(f"    - {agent_result['agent_id']}: {list(agent_result['result'].keys())}")
    
    print("\n[3] BROADCAST PATTERN")
    print("-" * 70)
    print("Task broadcast to all agents simultaneously\n")
    
    broadcast_team = AgentTeam(
        team_id="review_team",
        pattern=CollaborationPattern.BROADCAST
    )
    
    broadcast_team.add_agent("reviewer1", reviewer_agent, role="reviewer")
    broadcast_team.add_agent("reviewer2", reviewer_agent, role="reviewer")
    broadcast_team.add_agent("reviewer3", reviewer_agent, role="reviewer")
    
    task = {"problem": "Review product documentation"}
    
    result = await broadcast_team.execute_collaborative_task(task)
    
    print(f"✓ Broadcast execution complete")
    print(f"  Agents responded: {len(result['results'])}")
    approved_count = sum(1 for r in result['results'] if r['result'].get('approved', False))
    print(f"  Approved by: {approved_count}/{len(result['results'])} agents")
    
    print("\n[4] PIPELINE PATTERN")
    print("-" * 70)
    print("Sequential processing through agent stages\n")
    
    pipeline_team = AgentTeam(
        team_id="content_pipeline",
        pattern=CollaborationPattern.PIPELINE
    )
    
    pipeline_team.add_agent("researcher", researcher_agent, role="stage1")
    pipeline_team.add_agent("analyst", analyst_agent, role="stage2")
    pipeline_team.add_agent("writer", writer_agent, role="stage3")
    pipeline_team.add_agent("reviewer", reviewer_agent, role="stage4")
    
    task = {"problem": "Create comprehensive market report"}
    
    result = await pipeline_team.execute_collaborative_task(task)
    
    print(f"✓ Pipeline execution complete")
    print(f"  Stages: {len(result['stages'])}")
    for i, stage in enumerate(result['stages'], 1):
        print(f"    Stage {i} ({stage['agent_id']}): {list(stage['output'].keys())}")
    print(f"  Final output: {result['final_output']}")
    
    print("\n[5] CONSENSUS PATTERN")
    print("-" * 70)
    print("Agents vote on best solution\n")
    
    consensus_team = AgentTeam(
        team_id="decision_team",
        pattern=CollaborationPattern.CONSENSUS
    )
    
    def decision_agent_a(task):
        return {"decision": "Option A", "reasoning": "Cost-effective"}
    
    def decision_agent_b(task):
        return {"decision": "Option A", "reasoning": "Faster implementation"}
    
    def decision_agent_c(task):
        return {"decision": "Option B", "reasoning": "Better quality"}
    
    consensus_team.add_agent("agent_a", decision_agent_a)
    consensus_team.add_agent("agent_b", decision_agent_b)
    consensus_team.add_agent("agent_c", decision_agent_c)
    
    task = {"problem": "Choose deployment strategy"}
    
    result = await consensus_team.execute_collaborative_task(task)
    
    print(f"✓ Consensus execution complete")
    print(f"  Proposals: {len(result['proposals'])}")
    print(f"  Votes: {result['votes']}")
    print(f"  Consensus: {result['consensus']}")
    
    print("\n[6] Message Bus Communication")
    print("-" * 70)
    
    message_bus = MessageBus()
    
    message_bus.subscribe("agent1", "task_complete")
    message_bus.subscribe("agent2", "task_complete")
    
    async def agent1_handler(message):
        print(f"  Agent1 received: {message.message_type} from {message.sender_id}")
    
    async def agent2_handler(message):
        print(f"  Agent2 received: {message.message_type} from {message.sender_id}")
    
    message_bus.register_handler("agent1", agent1_handler)
    message_bus.register_handler("agent2", agent2_handler)
    
    print("\nSending broadcast message...")
    await message_bus.send(AgentMessage(
        sender_id="coordinator",
        recipient_id=None,
        message_type="task_complete",
        content={"status": "done"}
    ))
    
    print(f"\n✓ Message bus demonstration complete")
    print(f"  Total messages: {len(message_bus.messages)}")
    
    print("\n[7] Team Statistics")
    print("-" * 70)
    
    for team_name, team in [
        ("Hierarchical", hierarchical_team),
        ("Peer-to-Peer", peer_team),
        ("Pipeline", pipeline_team)
    ]:
        stats = team.get_team_statistics()
        print(f"\n{team_name} Team:")
        print(f"  Pattern: {stats['pattern']}")
        print(f"  Total agents: {stats['total_agents']}")
        print(f"  Messages: {stats['total_messages']}")
    
    print("\n[8] Collaboration Patterns Summary")
    print("-" * 70)
    
    print("\n🏢 HIERARCHICAL:")
    print("  Use when: Clear leadership needed")
    print("  Benefits: Coordinated execution, clear responsibility")
    print("  Example: Project management, military operations")
    
    print("\n🤝 PEER-TO-PEER:")
    print("  Use when: Independent parallel work")
    print("  Benefits: Diverse perspectives, no bottleneck")
    print("  Example: Brainstorming, research, analysis")
    
    print("\n📡 BROADCAST:")
    print("  Use when: Same task for all agents")
    print("  Benefits: Fast parallel execution")
    print("  Example: Code review, testing, validation")
    
    print("\n🔄 PIPELINE:")
    print("  Use when: Sequential stages needed")
    print("  Benefits: Specialization, quality control")
    print("  Example: Content creation, manufacturing, data processing")
    
    print("\n🗳️ CONSENSUS:")
    print("  Use when: Democratic decision needed")
    print("  Benefits: Collective wisdom, buy-in")
    print("  Example: Strategy selection, voting, approval")
    
    print("\n" + "=" * 70)
    print("✓ Multi-Agent Collaboration Example Complete")
    print("=" * 70)
    
    print("\nKey Features:")
    print("  ✓ 5 collaboration patterns")
    print("  ✓ Message bus for communication")
    print("  ✓ Role-based agent organization")
    print("  ✓ Leader/subordinate hierarchy")
    print("  ✓ Consensus voting")
    print("  ✓ Pipeline data flow")
    print("  ✓ Team statistics and monitoring")


if __name__ == "__main__":
    asyncio.run(main())
