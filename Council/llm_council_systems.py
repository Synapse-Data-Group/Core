"""
LLM-Powered Council Systems
All Council capabilities using real LLM reasoning instead of simulations
"""

from llm_interface import LLMInterface
from typing import List, Dict, Any, Optional
import json


class LLMPoweredModerator:
    """Moderator that uses LLM for all decision-making"""
    
    def __init__(self, llm: LLMInterface):
        self.llm = llm
        self.spawn_history = []
        
    def analyze_spawn_need(self, proposals: List[Any], agents: List[Any], 
                          problem: str, round_num: int) -> Dict[str, Any]:
        """Use LLM to determine if new agents should be spawned"""
        
        # Prepare context for LLM
        agent_summary = "\n".join([
            f"- {a.name}: {getattr(a, 'personality', {})}"
            for a in agents
        ])
        
        proposal_summary = "\n".join([
            f"- {p.agent_name}: {p.content[:200]}..."
            for p in proposals
        ])
        
        messages = [
            {
                "role": "system",
                "content": "You are an expert debate moderator. Analyze the debate and determine if new agents with different perspectives should be spawned."
            },
            {
                "role": "user",
                "content": f"""Debate Problem: {problem}

Current Round: {round_num}

Active Agents ({len(agents)}):
{agent_summary}

Proposals:
{proposal_summary}

Analyze this debate and determine:
1. Should we spawn a new agent? (yes/no)
2. If yes, what role/perspective is missing? (analyze, ethics, innovate, challenge, mediate, question, implement, envision)
3. What is the reason for spawning?
4. Urgency level (0.0 to 1.0)

Respond in JSON format:
{{
    "should_spawn": true/false,
    "role": "role_name",
    "reason": "explanation",
    "urgency": 0.0-1.0
}}"""
            }
        ]
        
        result = self.llm.generate_json(messages, temperature=0.3)
        
        if "error" in result:
            return {"should_spawn": False, "role": None, "reason": "LLM error", "urgency": 0.0}
        
        return result
    
    def should_conclude_debate(self, proposals: List[Any], agents: List[Any],
                               round_num: int, challenges_count: int, 
                               rebuttals_count: int) -> Dict[str, Any]:
        """Use LLM to determine if debate should conclude"""
        
        proposal_summary = "\n".join([
            f"- {p.agent_name} (Score: {p.score:.1f}): {len(p.challenges)} challenges, {len(p.rebuttals)} rebuttals"
            for p in proposals
        ])
        
        messages = [
            {
                "role": "system",
                "content": "You are an expert debate moderator. Determine if the debate has reached a natural conclusion."
            },
            {
                "role": "user",
                "content": f"""Debate Status:

Round: {round_num}
Active Agents: {len(agents)}
Proposals: {len(proposals)}
New Challenges This Round: {challenges_count}
New Rebuttals This Round: {rebuttals_count}

Proposal Status:
{proposal_summary}

Should the debate conclude? Consider:
- Has a clear winner emerged?
- Are arguments still evolving or have they converged?
- Is there diminishing returns on continued debate?
- Has sufficient depth been reached?

Respond in JSON format:
{{
    "should_conclude": true/false,
    "reason": "explanation",
    "confidence": 0.0-1.0
}}"""
            }
        ]
        
        result = self.llm.generate_json(messages, temperature=0.3)
        
        if "error" in result:
            return {"should_conclude": False, "reason": "LLM error", "confidence": 0.0}
        
        return result


class LLMPoweredScoring:
    """LLM-based proposal scoring system"""
    
    def __init__(self, llm: LLMInterface):
        self.llm = llm
    
    def score_proposals(self, proposals: List[Any], problem: str) -> Dict[str, float]:
        """Use LLM to score all proposals"""
        
        proposal_details = []
        for i, p in enumerate(proposals, 1):
            proposal_details.append(f"""
Proposal {i} by {p.agent_name}:
Content: {p.content}
Challenges Received: {len(p.challenges)}
Rebuttals Made: {len(p.rebuttals)}
""")
        
        messages = [
            {
                "role": "system",
                "content": "You are an expert debate judge. Evaluate proposals based on quality, argumentation, resilience to challenges, and overall merit."
            },
            {
                "role": "user",
                "content": f"""Problem: {problem}

{''.join(proposal_details)}

Score each proposal from 0-100 based on:
- Argument quality and depth
- Evidence and reasoning
- Resilience (how well they defended against challenges)
- Originality and insight
- Practical feasibility

Respond in JSON format with scores:
{{
    "scores": {{
        "{proposals[0].agent_name}": score,
        ...
    }},
    "reasoning": "brief explanation of scoring"
}}"""
            }
        ]
        
        result = self.llm.generate_json(messages, temperature=0.2)
        
        if "error" in result or "scores" not in result:
            # Fallback to simple scoring
            return {p.agent_name: 50.0 for p in proposals}
        
        return result["scores"]


class LLMPoweredCoalitions:
    """LLM-based coalition detection"""
    
    def __init__(self, llm: LLMInterface):
        self.llm = llm
    
    def detect_coalitions(self, agents: List[Any], proposals: List[Any]) -> List[Dict[str, Any]]:
        """Use LLM to detect natural coalitions between agents"""
        
        agent_positions = []
        for agent in agents:
            agent_proposal = next((p for p in proposals if p.agent_id == agent.agent_id), None)
            if agent_proposal:
                agent_positions.append(f"- {agent.name}: {agent_proposal.content[:150]}...")
        
        messages = [
            {
                "role": "system",
                "content": "You are an expert at analyzing debate dynamics. Identify natural coalitions between agents based on their positions."
            },
            {
                "role": "user",
                "content": f"""Agent Positions:

{''.join(agent_positions)}

Identify coalitions (groups of 2+ agents with aligned positions).

Respond in JSON format:
{{
    "coalitions": [
        {{
            "members": ["agent1_name", "agent2_name"],
            "alignment_reason": "why they align",
            "strength": 0.0-1.0
        }}
    ]
}}"""
            }
        ]
        
        result = self.llm.generate_json(messages, temperature=0.3)
        
        if "error" in result or "coalitions" not in result:
            return []
        
        return result["coalitions"]


class LLMPoweredQualityMetrics:
    """LLM-based argument quality evaluation"""
    
    def __init__(self, llm: LLMInterface):
        self.llm = llm
    
    def evaluate_argument(self, content: str, context: Dict[str, Any]) -> Dict[str, Any]:
        """Use LLM to evaluate argument quality"""
        
        messages = [
            {
                "role": "system",
                "content": "You are an expert at evaluating argument quality. Assess logical structure, evidence, clarity, and persuasiveness."
            },
            {
                "role": "user",
                "content": f"""Evaluate this argument:

{content}

Assess:
- Logical coherence (0-1)
- Evidence quality (0-1)
- Clarity (0-1)
- Persuasiveness (0-1)
- Originality (0-1)

Also identify:
- Key strengths (list)
- Key weaknesses (list)

Respond in JSON format:
{{
    "scores": {{
        "logical_coherence": 0.0-1.0,
        "evidence_quality": 0.0-1.0,
        "clarity": 0.0-1.0,
        "persuasiveness": 0.0-1.0,
        "originality": 0.0-1.0
    }},
    "overall_quality": 0.0-1.0,
    "strengths": ["strength1", "strength2"],
    "weaknesses": ["weakness1", "weakness2"]
}}"""
            }
        ]
        
        result = self.llm.generate_json(messages, temperature=0.2)
        
        if "error" in result:
            return {
                "scores": {},
                "overall_quality": 0.5,
                "strengths": [],
                "weaknesses": []
            }
        
        return result


class LLMPoweredEmotions:
    """LLM-based emotional state analysis"""
    
    def __init__(self, llm: LLMInterface):
        self.llm = llm
        self.agent_states = {}
    
    def analyze_emotion(self, agent_id: str, agent_name: str, 
                       event: str, context: Dict[str, Any]) -> Dict[str, Any]:
        """Use LLM to determine emotional state"""
        
        previous_state = self.agent_states.get(agent_id, {
            "state": "neutral",
            "intensity": 0.5
        })
        
        messages = [
            {
                "role": "system",
                "content": "You are an expert at analyzing emotional states in debate contexts. Determine how an agent would feel given their situation."
            },
            {
                "role": "user",
                "content": f"""Agent: {agent_name}
Previous State: {previous_state['state']} (intensity: {previous_state['intensity']:.2f})

Event: {event}
Context: {json.dumps(context)}

What is the agent's new emotional state?

Possible states: confident, defensive, frustrated, engaged, neutral, satisfied, concerned

Respond in JSON format:
{{
    "state": "emotional_state",
    "intensity": 0.0-1.0,
    "reasoning": "brief explanation"
}}"""
            }
        ]
        
        result = self.llm.generate_json(messages, temperature=0.4)
        
        if "error" not in result:
            self.agent_states[agent_id] = result
        
        return self.agent_states.get(agent_id, previous_state)


class LLMPoweredKnowledgeGraph:
    """LLM-based concept extraction and relationship mapping"""
    
    def __init__(self, llm: LLMInterface):
        self.llm = llm
        self.concepts = {}
        self.relationships = []
    
    def extract_concepts(self, content: str, source_id: str, 
                        content_type: str) -> Dict[str, Any]:
        """Use LLM to extract key concepts and relationships"""
        
        messages = [
            {
                "role": "system",
                "content": "You are an expert at extracting key concepts and their relationships from text. Identify important ideas and how they connect."
            },
            {
                "role": "user",
                "content": f"""Extract key concepts from this {content_type}:

{content}

Identify:
- Main concepts (3-7 key ideas)
- Relationships between concepts (how they connect)

Respond in JSON format:
{{
    "concepts": [
        {{"name": "concept1", "importance": 0.0-1.0}},
        {{"name": "concept2", "importance": 0.0-1.0}}
    ],
    "relationships": [
        {{"from": "concept1", "to": "concept2", "type": "supports/opposes/relates_to"}}
    ]
}}"""
            }
        ]
        
        result = self.llm.generate_json(messages, temperature=0.3)
        
        if "error" not in result:
            # Store concepts
            for concept in result.get("concepts", []):
                concept_name = concept["name"]
                if concept_name not in self.concepts:
                    self.concepts[concept_name] = {
                        "importance": concept["importance"],
                        "sources": []
                    }
                self.concepts[concept_name]["sources"].append(source_id)
            
            # Store relationships
            for rel in result.get("relationships", []):
                self.relationships.append(rel)
        
        return {
            "total_concepts": len(self.concepts),
            "total_relationships": len(self.relationships)
        }


class LLMPoweredReputation:
    """LLM-based reputation and trust evaluation"""
    
    def __init__(self, llm: LLMInterface):
        self.llm = llm
        self.reputation_scores = {}
    
    def evaluate_reputation(self, agent_id: str, agent_name: str,
                           performance: Dict[str, Any]) -> Dict[str, Any]:
        """Use LLM to evaluate agent reputation"""
        
        messages = [
            {
                "role": "system",
                "content": "You are an expert at evaluating participant reputation in debates. Assess trustworthiness, contribution quality, and overall value."
            },
            {
                "role": "user",
                "content": f"""Evaluate reputation for: {agent_name}

Performance Metrics:
- Proposals Made: {performance.get('proposals', 0)}
- Challenges Made: {performance.get('challenges', 0)}
- Rebuttals Made: {performance.get('rebuttals', 0)}
- Final Score: {performance.get('score', 0):.1f}
- Was Winner: {performance.get('is_winner', False)}

Assess:
- Contribution quality (0-100)
- Engagement level (0-100)
- Argumentation skill (0-100)
- Trustworthiness (0-100)

Respond in JSON format:
{{
    "overall_score": 0-100,
    "contribution_quality": 0-100,
    "engagement": 0-100,
    "argumentation": 0-100,
    "trustworthiness": 0-100,
    "summary": "brief assessment"
}}"""
            }
        ]
        
        result = self.llm.generate_json(messages, temperature=0.2)
        
        if "error" not in result:
            self.reputation_scores[agent_id] = result
        
        return self.reputation_scores.get(agent_id, {
            "overall_score": 50.0,
            "contribution_quality": 50.0,
            "engagement": 50.0,
            "argumentation": 50.0,
            "trustworthiness": 50.0,
            "summary": "No evaluation available"
        })
