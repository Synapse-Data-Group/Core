"""
TEST 1: FULL HIVE INTELLIGENCE - END-TO-END DELIVERABLE PRODUCTION
Moderator starts alone and builds entire team to produce a comprehensive report.

100% FLUID SYSTEM:
- Moderator uses LLM reasoning to decide team size and composition
- Minimum 10 agents suggested, but moderator decides actual number
- Spawns debate agents (for ideation) AND worker agents (for execution)
- ALL Council capabilities with real LLM reasoning
- Produces final deliverable report

GOALS:
1. Test AI quality improvement with Council framework
2. Measure performance vitals
3. Evaluate deliverable production capability
"""

import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from llm_interface import create_llm
from llm_council_systems import (
    LLMPoweredModerator,
    LLMPoweredScoring,
    LLMPoweredCoalitions,
    LLMPoweredQualityMetrics,
    LLMPoweredEmotions,
    LLMPoweredKnowledgeGraph,
    LLMPoweredReputation
)
from llm_powered_agent import LLMPoweredAgent
from real_web_search import RealWebResearchTool
from whitepaper_logger import WhitepaperDocumenter
import time
import uuid
import json
from datetime import datetime
from typing import List, Dict, Any
from dataclasses import dataclass, field


# Configuration
LLM_PROVIDER = "openai"
API_KEY = "sk-your-api-key-here"
MODEL = None


@dataclass
class Proposal:
    proposal_id: str
    agent_id: str
    agent_name: str
    content: str
    timestamp: float
    score: float = 50.0
    challenges: List = field(default_factory=list)
    rebuttals: List = field(default_factory=list)


@dataclass
class Challenge:
    challenge_id: str
    agent_id: str
    agent_name: str
    content: str
    timestamp: float
    metadata: Dict = field(default_factory=dict)


@dataclass
class Rebuttal:
    rebuttal_id: str
    agent_id: str
    agent_name: str
    content: str
    timestamp: float
    metadata: Dict = field(default_factory=dict)


class PerformanceVitals:
    """Track comprehensive performance metrics"""
    
    def __init__(self):
        self.start_time = time.time()
        self.events = []
        self.llm_calls = 0
        self.web_searches = 0
        self.agent_spawns = 0
        self.coalitions_formed = 0
        self.concepts_extracted = 0
        
    def log_event(self, event_type: str, data: Dict[str, Any]):
        self.events.append({
            "timestamp": time.time() - self.start_time,
            "type": event_type,
            "data": data
        })
        
    def log_llm_call(self):
        self.llm_calls += 1
        
    def get_summary(self) -> Dict[str, Any]:
        return {
            "total_duration": time.time() - self.start_time,
            "llm_calls": self.llm_calls,
            "web_searches": self.web_searches,
            "agent_spawns": self.agent_spawns,
            "coalitions_formed": self.coalitions_formed,
            "concepts_extracted": self.concepts_extracted,
            "total_events": len(self.events)
        }


def run_test1():
    """
    FULL HIVE INTELLIGENCE TEST
    Moderator builds entire team and produces deliverable report
    """
    
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    test_folder = f"testing/output/test1_hive_{timestamp}"
    os.makedirs(test_folder, exist_ok=True)
    
    print("\n" + "🐝"*40)
    print("\n  TEST 1: FULL HIVE INTELLIGENCE")
    print("  Moderator builds team → Debate → Produce Report")
    print("  100% LLM-Powered | ALL Council Capabilities")
    print(f"  Output: {test_folder}")
    print("\n" + "🐝"*40 + "\n")
    
    # The task
    problem = """Create a comprehensive strategic plan for transforming a mid-sized city into a 
sustainable, carbon-neutral urban center by 2040. The plan must address infrastructure, 
transportation, energy, economic development, and social equity while maintaining quality of life."""
    
    print("📋 TASK:")
    print(f"   {problem}\n")
    print("🎯 DELIVERABLE: Comprehensive strategic report\n")
    time.sleep(2)
    
    # Initialize systems
    print("🔧 Initializing LLM-Powered Council Framework...\n")
    
    llm = create_llm(LLM_PROVIDER, API_KEY, MODEL)
    vitals = PerformanceVitals()
    doc = WhitepaperDocumenter("test1_hive")
    
    moderator = LLMPoweredModerator(llm)
    scoring_system = LLMPoweredScoring(llm)
    coalition_system = LLMPoweredCoalitions(llm)
    quality_system = LLMPoweredQualityMetrics(llm)
    emotion_system = LLMPoweredEmotions(llm)
    knowledge_system = LLMPoweredKnowledgeGraph(llm)
    reputation_system = LLMPoweredReputation(llm)
    
    print(f"  ✓ LLM Interface ({llm.model})")
    print("  ✓ All Council Systems (LLM-Powered)")
    print("  ✓ Performance Vitals Tracking")
    time.sleep(1)
    
    # Storage
    agents: Dict[str, LLMPoweredAgent] = {}
    proposals = []
    work_products = []  # For worker agent outputs
    
    from agent_factory import AgentArchetype
    
    def spawn_agent(role: str, reason: str, agent_type: str = "debater") -> LLMPoweredAgent:
        """Spawn agent with full Council capabilities"""
        
        role_to_archetype = {
            # Debate agents
            "analyze": "analyst",
            "ethics": "ethicist",
            "innovate": "innovator",
            "challenge": "devil_advocate",
            "mediate": "mediator",
            "question": "skeptic",
            "implement": "pragmatist",
            "envision": "visionary",
            # Worker agents
            "research": "specialist",
            "write": "analyst",
            "edit": "pragmatist",
            "synthesize": "mediator"
        }
        
        archetype_name = role_to_archetype.get(role.lower(), "pragmatist")
        archetype_data = AgentArchetype.get_archetype(archetype_name)
        
        agent_name = f"{archetype_name.title()}_{agent_type.title()}_{len(agents) + 1}"
        agent = LLMPoweredAgent(agent_name, API_KEY, personality=archetype_data["personality"])
        agent.agent_type = agent_type  # Mark as debater or worker
        
        agents[agent.agent_id] = agent
        vitals.agent_spawns += 1
        
        # Add web research
        web_tool = RealWebResearchTool()
        agent.tools.append(web_tool)
        
        print(f"   ✓ Spawned: {agent.name} ({agent_type}) - Role: {role}")
        
        doc.log_agent_spawn(agent.name, reason, archetype_name)
        vitals.log_event("agent_spawned", {
            "name": agent.name,
            "type": agent_type,
            "role": role
        })
        
        return agent
    
    doc.start_debate(problem, 0)
    
    print("\n" + "="*80)
    print("PHASE 1: MODERATOR TEAM PLANNING (LLM REASONING)")
    print("="*80 + "\n")
    
    print("🤖 Moderator analyzing task and planning team composition...\n")
    time.sleep(2)
    
    # Ask moderator to plan the team
    team_planning_prompt = f"""You are a moderator tasked with building a team to complete this project:

TASK: {problem}

DELIVERABLE: Comprehensive strategic report

You need to build a team with:
1. DEBATE AGENTS - To explore ideas, challenge assumptions, and refine concepts
2. WORKER AGENTS - To research, write, and produce the final report

Available roles:
- Debate: analyze, ethics, innovate, challenge, mediate, question, implement, envision
- Worker: research, write, edit, synthesize

MINIMUM: 10 agents suggested, but you decide the optimal number based on task complexity.

Plan your team composition. How many agents of each type do you need?

Respond in JSON format:
{{
    "total_agents": number,
    "reasoning": "why this team size",
    "debate_agents": [
        {{"role": "role_name", "count": number, "purpose": "why needed"}}
    ],
    "worker_agents": [
        {{"role": "role_name", "count": number, "purpose": "why needed"}}
    ]
}}"""
    
    messages = [
        {"role": "system", "content": "You are an expert project moderator planning optimal team composition."},
        {"role": "user", "content": team_planning_prompt}
    ]
    
    print("  Calling LLM for team planning...")
    team_plan = llm.generate_json(messages, temperature=0.3)
    vitals.log_llm_call()
    
    if "error" in team_plan:
        print(f"  ⚠️  LLM planning error, using default team")
        team_plan = {
            "total_agents": 12,
            "reasoning": "Balanced team for comprehensive coverage",
            "debate_agents": [
                {"role": "analyze", "count": 2, "purpose": "data analysis"},
                {"role": "ethics", "count": 1, "purpose": "ethical considerations"},
                {"role": "innovate", "count": 2, "purpose": "creative solutions"},
                {"role": "challenge", "count": 1, "purpose": "critical review"}
            ],
            "worker_agents": [
                {"role": "research", "count": 3, "purpose": "gather information"},
                {"role": "write", "count": 2, "purpose": "draft sections"},
                {"role": "edit", "count": 1, "purpose": "final polish"}
            ]
        }
    
    print(f"\n  📊 MODERATOR'S TEAM PLAN:")
    print(f"     Total Agents: {team_plan['total_agents']}")
    print(f"     Reasoning: {team_plan['reasoning']}\n")
    
    print(f"  Debate Agents:")
    for agent_spec in team_plan['debate_agents']:
        print(f"     - {agent_spec['count']}x {agent_spec['role']}: {agent_spec['purpose']}")
    
    print(f"\n  Worker Agents:")
    for agent_spec in team_plan['worker_agents']:
        print(f"     - {agent_spec['count']}x {agent_spec['role']}: {agent_spec['purpose']}")
    
    vitals.log_event("team_planned", team_plan)
    time.sleep(2)
    
    print("\n" + "="*80)
    print("PHASE 2: TEAM ASSEMBLY")
    print("="*80 + "\n")
    
    print("🌊 Moderator spawning team...\n")
    
    # Spawn debate agents
    print("  Spawning Debate Agents:\n")
    for agent_spec in team_plan['debate_agents']:
        for i in range(agent_spec['count']):
            spawn_agent(agent_spec['role'], agent_spec['purpose'], "debater")
            time.sleep(0.5)
    
    # Spawn worker agents
    print("\n  Spawning Worker Agents:\n")
    for agent_spec in team_plan['worker_agents']:
        for i in range(agent_spec['count']):
            spawn_agent(agent_spec['role'], agent_spec['purpose'], "worker")
            time.sleep(0.5)
    
    print(f"\n✅ Team assembled! Total agents: {len(agents)}")
    print(f"   Debaters: {sum(1 for a in agents.values() if a.agent_type == 'debater')}")
    print(f"   Workers: {sum(1 for a in agents.values() if a.agent_type == 'worker')}\n")
    
    time.sleep(2)
    
    # PHASE 3: DEBATE & IDEATION
    print("\n" + "="*80)
    print("PHASE 3: DEBATE & IDEATION")
    print("="*80 + "\n")
    
    debaters = [a for a in agents.values() if a.agent_type == "debater"]
    
    print(f"📝 {len(debaters)} debate agents generating proposals...\n")
    
    for agent in debaters:
        print(f"[{agent.name}] Generating proposal with LLM + Web Research...\n")
        
        # Web research first
        web_tool = agent.tools[0] if agent.tools else None
        research_context = {}
        if web_tool:
            print(f"  🌐 Searching web...")
            search_query = f"sustainable city carbon neutral 2040 {agent.name.split('_')[0]}"
            research = web_tool.execute(search_query, action="search")
            research_context['web_research'] = research[:500]
            vitals.web_searches += 1
            print(f"  ✓ Research complete\n")
        
        proposal_content = agent.generate_proposal(problem, research_context)
        vitals.log_llm_call()
        
        proposal = Proposal(
            proposal_id=str(uuid.uuid4()),
            agent_id=agent.agent_id,
            agent_name=agent.name,
            content=proposal_content,
            timestamp=time.time()
        )
        proposals.append(proposal)
        agent.proposals_made.append(proposal.proposal_id)
        
        print(f"[{agent.name}] PROPOSAL:")
        print(f"  {proposal_content[:250]}...\n")
        
        # LLM-powered quality evaluation
        quality = quality_system.evaluate_argument(proposal_content, {})
        vitals.log_llm_call()
        print(f"  📊 Quality: {quality.get('overall_quality', 0.5):.2f}\n")
        
        # LLM-powered knowledge extraction
        knowledge_system.extract_concepts(proposal_content, agent.agent_id, "proposal")
        vitals.log_llm_call()
        vitals.concepts_extracted += 1
        
        # LLM-powered emotion analysis
        emotion = emotion_system.analyze_emotion(agent.agent_id, agent.name, "proposal_made", {})
        vitals.log_llm_call()
        print(f"  🎭 Emotion: {emotion.get('state', 'neutral')}\n")
        
        time.sleep(1)
    
    print(f"✅ {len(proposals)} proposals generated\n")
    
    # LLM-powered coalition detection
    print("🤝 Detecting coalitions with LLM...\n")
    coalitions = coalition_system.detect_coalitions(debaters, proposals)
    vitals.log_llm_call()
    vitals.coalitions_formed = len(coalitions)
    
    if coalitions:
        for coalition in coalitions:
            print(f"  ✓ Coalition: {', '.join(coalition.get('members', []))}")
            print(f"    Reason: {coalition.get('alignment_reason', 'N/A')}\n")
    
    time.sleep(2)
    
    # PHASE 4: CHALLENGE & REFINEMENT
    print("\n" + "="*80)
    print("PHASE 4: CHALLENGE & REFINEMENT")
    print("="*80 + "\n")
    
    print("⚔️  Agents challenging proposals...\n")
    
    challenge_count = 0
    for proposal in proposals[:3]:  # Challenge top 3 for time
        for agent in debaters[:2]:  # 2 challengers each
            if agent.agent_id != proposal.agent_id:
                print(f"[{agent.name}] Challenging {proposal.agent_name}...\n")
                
                challenge_content = agent.generate_challenge(
                    proposal.content,
                    proposal.agent_name,
                    {}
                )
                vitals.log_llm_call()
                
                challenge = Challenge(
                    challenge_id=str(uuid.uuid4()),
                    agent_id=agent.agent_id,
                    agent_name=agent.name,
                    content=challenge_content,
                    timestamp=time.time()
                )
                proposal.challenges.append(challenge)
                challenge_count += 1
                
                print(f"  Challenge: {challenge_content[:150]}...\n")
                time.sleep(0.5)
    
    print(f"✅ {challenge_count} challenges generated\n")
    time.sleep(1)
    
    # LLM-powered scoring
    print("📊 LLM scoring proposals...\n")
    scores = scoring_system.score_proposals(proposals, problem)
    vitals.log_llm_call()
    
    for proposal in proposals:
        proposal.score = scores.get(proposal.agent_name, 50.0)
        print(f"  {proposal.agent_name}: {proposal.score:.1f}/100")
    
    print()
    time.sleep(2)
    
    # PHASE 5: REPORT PRODUCTION
    print("\n" + "="*80)
    print("PHASE 5: REPORT PRODUCTION")
    print("="*80 + "\n")
    
    workers = [a for a in agents.values() if a.agent_type == "worker"]
    
    print(f"📝 {len(workers)} worker agents producing deliverable...\n")
    
    # Compile debate insights
    debate_summary = "\n\n".join([
        f"**{p.agent_name}** (Score: {p.score:.1f}):\n{p.content}"
        for p in sorted(proposals, key=lambda x: x.score, reverse=True)[:5]
    ])
    
    report_sections = {}
    
    # Assign sections to workers
    sections = [
        "Executive Summary",
        "Infrastructure Strategy",
        "Transportation Plan",
        "Energy Transition",
        "Economic Development",
        "Social Equity Framework",
        "Implementation Timeline",
        "Conclusion"
    ]
    
    for i, section in enumerate(sections):
        worker = workers[i % len(workers)]
        
        print(f"[{worker.name}] Writing: {section}...\n")
        
        section_prompt = f"""Based on the debate insights below, write the "{section}" section of the strategic plan.

DEBATE INSIGHTS:
{debate_summary[:2000]}

Write a comprehensive, professional section (300-500 words)."""
        
        messages = [
            {"role": "system", "content": f"You are {worker.name}, a professional report writer."},
            {"role": "user", "content": section_prompt}
        ]
        
        section_content = llm.generate(messages, temperature=0.7, max_tokens=800)
        vitals.log_llm_call()
        
        report_sections[section] = {
            "content": section_content,
            "author": worker.name
        }
        
        print(f"  ✓ Section complete ({len(section_content)} chars)\n")
        time.sleep(1)
    
    # PHASE 6: FINAL REPORT ASSEMBLY
    print("\n" + "="*80)
    print("PHASE 6: FINAL REPORT ASSEMBLY")
    print("="*80 + "\n")
    
    print("📄 Assembling final deliverable...\n")
    
    final_report = f"""
# STRATEGIC PLAN FOR CARBON-NEUTRAL CITY TRANSFORMATION BY 2040

**Produced by Council Framework Hive Intelligence**
**Date: {datetime.now().strftime('%Y-%m-%d')}**
**Team Size: {len(agents)} agents ({len(debaters)} debaters, {len(workers)} workers)**

---

"""
    
    for section, data in report_sections.items():
        final_report += f"\n## {section}\n\n"
        final_report += f"*Author: {data['author']}*\n\n"
        final_report += data['content'] + "\n\n"
        final_report += "---\n"
    
    # Add appendix
    final_report += f"""
## APPENDIX: Production Metrics

- **Total Agents**: {len(agents)}
- **Debate Proposals**: {len(proposals)}
- **Challenges**: {challenge_count}
- **Coalitions Formed**: {vitals.coalitions_formed}
- **Concepts Extracted**: {vitals.concepts_extracted}
- **LLM Calls**: {vitals.llm_calls}
- **Web Searches**: {vitals.web_searches}
- **Production Time**: {time.time() - vitals.start_time:.1f}s

---

*This report was produced using the Council Framework with full LLM-powered reasoning across all systems.*
"""
    
    # Save report
    report_file = f"{test_folder}/FINAL_REPORT.md"
    with open(report_file, 'w', encoding='utf-8') as f:
        f.write(final_report)
    
    print(f"✅ Final report saved: {report_file}\n")
    
    # Save vitals
    vitals_data = vitals.get_summary()
    vitals_file = f"{test_folder}/performance_vitals.json"
    with open(vitals_file, 'w', encoding='utf-8') as f:
        json.dump(vitals_data, f, indent=2)
    
    print(f"✅ Performance vitals saved: {vitals_file}\n")
    
    # LLM-powered reputation evaluation
    print("⭐ Evaluating agent reputations with LLM...\n")
    for agent in list(agents.values())[:5]:  # Top 5
        performance = {
            "proposals": len(agent.proposals_made),
            "challenges": len(agent.challenges_made),
            "rebuttals": len(agent.rebuttals_made),
            "score": getattr(agent, 'score', 50.0),
            "is_winner": False
        }
        reputation = reputation_system.evaluate_reputation(agent.agent_id, agent.name, performance)
        vitals.log_llm_call()
        print(f"  {agent.name}: {reputation.get('overall_score', 50):.1f}/100")
    
    print("\n" + "="*80)
    print("TEST 1 COMPLETE - FULL HIVE INTELLIGENCE")
    print("="*80)
    
    print(f"\n📊 PERFORMANCE SUMMARY:")
    print(f"   Total Agents: {len(agents)}")
    print(f"   Debate Proposals: {len(proposals)}")
    print(f"   LLM Calls: {vitals.llm_calls}")
    print(f"   Web Searches: {vitals.web_searches}")
    print(f"   Coalitions: {vitals.coalitions_formed}")
    print(f"   Concepts Extracted: {vitals.concepts_extracted}")
    print(f"   Duration: {time.time() - vitals.start_time:.1f}s")
    
    print(f"\n✅ DELIVERABLE PRODUCED:")
    print(f"   📄 {report_file}")
    print(f"   📊 {vitals_file}")
    
    print("\n🎉 ALL COUNCIL CAPABILITIES DEMONSTRATED:")
    print("   ✓ LLM-powered moderator (team planning)")
    print("   ✓ LLM-powered agents (proposals, challenges)")
    print("   ✓ LLM-powered scoring")
    print("   ✓ LLM-powered coalitions")
    print("   ✓ LLM-powered quality metrics")
    print("   ✓ LLM-powered emotions")
    print("   ✓ LLM-powered knowledge graph")
    print("   ✓ LLM-powered reputation")
    print("   ✓ Real web search")
    print("   ✓ Deliverable production")
    
    return {
        "total_agents": len(agents),
        "proposals": len(proposals),
        "llm_calls": vitals.llm_calls,
        "report_file": report_file,
        "vitals_file": vitals_file
    }


if __name__ == "__main__":
    print("\n" + "⚡"*40)
    print("\n  COUNCIL FRAMEWORK - TEST 1")
    print("  FULL HIVE INTELLIGENCE")
    print("  Moderator → Team → Debate → Deliverable")
    print("\n" + "⚡"*40)
    
    input("\nPress ENTER to run Test 1 (Full Hive)...")
    
    result = run_test1()
    
    print(f"\n🎉 Test 1 complete!")
    print(f"   Team size: {result['total_agents']} agents")
    print(f"   LLM calls: {result['llm_calls']}")
    print(f"   Report: {result['report_file']}")
