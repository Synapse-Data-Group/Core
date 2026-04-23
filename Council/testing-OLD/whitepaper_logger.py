"""
Whitepaper Documentation Logger
Captures full debate conversations and vitals over time for research documentation
"""

import json
import time
from typing import Dict, List, Any
from datetime import datetime


class ConversationLogger:
    """Logs complete debate conversation in human-readable format"""
    
    def __init__(self, test_name: str):
        self.test_name = test_name
        self.conversation_lines: List[str] = []
        self.start_time = time.time()
        
    def log_header(self, problem: str, agent_count: int):
        """Log debate header"""
        self.conversation_lines.append("="*80)
        self.conversation_lines.append(f"DEBATE CONVERSATION LOG")
        self.conversation_lines.append(f"Test: {self.test_name}")
        self.conversation_lines.append(f"Timestamp: {datetime.now().isoformat()}")
        self.conversation_lines.append("="*80)
        self.conversation_lines.append(f"\nProblem: {problem}")
        self.conversation_lines.append(f"Initial Agents: {agent_count}\n")
        self.conversation_lines.append("="*80 + "\n")
    
    def log_phase(self, phase: str):
        """Log debate phase"""
        self.conversation_lines.append(f"\n{'='*80}")
        self.conversation_lines.append(f"PHASE: {phase.upper()}")
        self.conversation_lines.append(f"{'='*80}\n")
    
    def log_agent_action(self, agent_name: str, action_type: str, content: str, 
                        target: str = None, metadata: Dict = None):
        """Log agent action with full context"""
        timestamp = time.time() - self.start_time
        
        self.conversation_lines.append(f"[{timestamp:.2f}s] {agent_name} - {action_type.upper()}")
        if target:
            self.conversation_lines.append(f"  Target: {target}")
        self.conversation_lines.append(f"  Content: {content}")
        if metadata:
            self.conversation_lines.append(f"  Metadata: {json.dumps(metadata, indent=4)}")
        self.conversation_lines.append("")
    
    def log_moderator_action(self, action: str, details: Dict):
        """Log moderator actions"""
        timestamp = time.time() - self.start_time
        
        self.conversation_lines.append(f"[{timestamp:.2f}s] MODERATOR - {action.upper()}")
        for key, value in details.items():
            self.conversation_lines.append(f"  {key}: {value}")
        self.conversation_lines.append("")
    
    def log_decision(self, decision: Dict):
        """Log final decision"""
        self.conversation_lines.append("\n" + "="*80)
        self.conversation_lines.append("FINAL DECISION")
        self.conversation_lines.append("="*80 + "\n")
        self.conversation_lines.append(f"Winner: {decision.get('decision', 'Unknown')}")
        self.conversation_lines.append(f"Confidence: {decision.get('confidence', 0):.1%}")
        self.conversation_lines.append(f"\nReasoning:")
        self.conversation_lines.append(f"{decision.get('reasoning', 'N/A')}\n")
    
    def save(self, filepath: str):
        """Save conversation to file"""
        with open(filepath, 'w', encoding='utf-8') as f:
            f.write('\n'.join(self.conversation_lines))


class VitalsMonitor:
    """Monitors and tracks system vitals over time"""
    
    def __init__(self, test_name: str):
        self.test_name = test_name
        self.start_time = time.time()
        self.snapshots: List[Dict[str, Any]] = []
        self.events: List[Dict[str, Any]] = []
        
    def snapshot(self, agents: List[Any], proposals: List[Any], 
                context: Dict[str, Any] = None):
        """Take a snapshot of current system state"""
        
        timestamp = time.time() - self.start_time
        
        snapshot = {
            "timestamp": timestamp,
            "datetime": datetime.now().isoformat(),
            "agent_count": len(agents),
            "proposal_count": len(proposals),
            "agents": []
        }
        
        for agent in agents:
            agent_data = {
                "name": agent.name,
                "agent_id": agent.agent_id,
                "is_active": agent.is_active,
                "score": agent.score,
                "proposals_made": len(agent.proposals_made),
                "challenges_made": len(agent.challenges_made),
                "rebuttals_made": len(agent.rebuttals_made),
                "personality": agent.personality.copy() if hasattr(agent, 'personality') else {},
                "exploration_rate": agent.q_learning.exploration_rate if hasattr(agent, 'q_learning') else 0,
                "memory_size": len(agent.memory.experiences) if hasattr(agent, 'memory') else 0
            }
            snapshot["agents"].append(agent_data)
        
        snapshot["proposals"] = []
        for proposal in proposals:
            proposal_data = {
                "agent_name": proposal.agent_name,
                "score": proposal.score,
                "challenges": len(proposal.challenges),
                "rebuttals": len(proposal.rebuttals)
            }
            snapshot["proposals"].append(proposal_data)
        
        if context:
            snapshot["context"] = context
        
        self.snapshots.append(snapshot)
    
    def log_event(self, event_type: str, details: Dict[str, Any]):
        """Log a significant event"""
        
        timestamp = time.time() - self.start_time
        
        event = {
            "timestamp": timestamp,
            "datetime": datetime.now().isoformat(),
            "event_type": event_type,
            "details": details
        }
        
        self.events.append(event)
    
    def save(self, filepath: str):
        """Save vitals to JSON file"""
        
        vitals = {
            "test_name": self.test_name,
            "start_time": datetime.fromtimestamp(self.start_time).isoformat(),
            "duration_seconds": time.time() - self.start_time,
            "total_snapshots": len(self.snapshots),
            "total_events": len(self.events),
            "snapshots": self.snapshots,
            "events": self.events,
            "summary": self._generate_summary()
        }
        
        with open(filepath, 'w', encoding='utf-8') as f:
            json.dump(vitals, f, indent=2)
    
    def _generate_summary(self) -> Dict[str, Any]:
        """Generate summary statistics"""
        
        if not self.snapshots:
            return {}
        
        first = self.snapshots[0]
        last = self.snapshots[-1]
        
        return {
            "agent_count_change": last["agent_count"] - first["agent_count"],
            "total_proposals": last["proposal_count"],
            "snapshots_taken": len(self.snapshots),
            "events_logged": len(self.events),
            "duration": time.time() - self.start_time
        }


class WhitepaperDocumenter:
    """Complete documentation system for whitepaper research"""
    
    def __init__(self, test_name: str):
        self.test_name = test_name
        self.conversation = ConversationLogger(test_name)
        self.vitals = VitalsMonitor(test_name)
        
    def start_debate(self, problem: str, agent_count: int):
        """Initialize documentation for a debate"""
        self.conversation.log_header(problem, agent_count)
    
    def log_phase_start(self, phase: str, agents: List[Any], proposals: List[Any]):
        """Log phase transition"""
        self.conversation.log_phase(phase)
        self.vitals.snapshot(agents, proposals, {"phase": phase})
        self.vitals.log_event("phase_start", {"phase": phase})
    
    def log_proposal(self, agent_name: str, content: str, metadata: Dict = None):
        """Log a proposal"""
        self.conversation.log_agent_action(agent_name, "PROPOSAL", content, metadata=metadata)
    
    def log_challenge(self, agent_name: str, target_name: str, content: str, metadata: Dict = None):
        """Log a challenge"""
        self.conversation.log_agent_action(agent_name, "CHALLENGE", content, target=target_name, metadata=metadata)
    
    def log_rebuttal(self, agent_name: str, target_name: str, content: str, metadata: Dict = None):
        """Log a rebuttal"""
        self.conversation.log_agent_action(agent_name, "REBUTTAL", content, target=target_name, metadata=metadata)
    
    def log_agent_spawn(self, agent_name: str, reason: str, archetype: str):
        """Log agent spawning"""
        self.conversation.log_moderator_action("SPAWN_AGENT", {
            "agent": agent_name,
            "reason": reason,
            "archetype": archetype
        })
        self.vitals.log_event("agent_spawn", {
            "agent": agent_name,
            "reason": reason,
            "archetype": archetype
        })
    
    def log_agent_termination(self, agent_name: str, reason: str):
        """Log agent termination"""
        self.conversation.log_moderator_action("TERMINATE_AGENT", {
            "agent": agent_name,
            "reason": reason
        })
        self.vitals.log_event("agent_termination", {
            "agent": agent_name,
            "reason": reason
        })
    
    def log_scoring(self, scores: Dict[str, float]):
        """Log scoring results"""
        self.conversation.log_moderator_action("SCORING", scores)
        self.vitals.log_event("scoring", {"scores": scores})
    
    def log_final_decision(self, decision: Dict, agents: List[Any], proposals: List[Any]):
        """Log final decision"""
        self.conversation.log_decision(decision)
        self.vitals.snapshot(agents, proposals, {"phase": "completed", "decision": decision})
        self.vitals.log_event("debate_completed", {"decision": decision["decision"]})
    
    def take_snapshot(self, agents: List[Any], proposals: List[Any], context: Dict = None):
        """Take a vitals snapshot"""
        self.vitals.snapshot(agents, proposals, context)
    
    def save_all(self, output_dir: str):
        """Save both conversation and vitals"""
        import os
        os.makedirs(output_dir, exist_ok=True)
        
        conversation_file = os.path.join(output_dir, f"{self.test_name}_conversation.txt")
        vitals_file = os.path.join(output_dir, f"{self.test_name}_vitals.json")
        
        self.conversation.save(conversation_file)
        self.vitals.save(vitals_file)
        
        return conversation_file, vitals_file
