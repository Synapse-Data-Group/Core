"""
Test Logger - Comprehensive logging system for research validation

Logs all system activity to prove hypothesis:
- Conversations (all LLM prompts and responses)
- Vitals (neuron counts, activation patterns, fitness)
- Behavior (decisions, reasoning traces, actions)
"""

import json
import time
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Any, Optional


class TestLogger:
    """Comprehensive logging for test validation"""
    
    def __init__(self, test_name: str, output_dir: str = "."):
        self.test_name = test_name
        self.output_dir = Path(output_dir)
        self.output_dir.mkdir(exist_ok=True)
        
        self.start_time = time.time()
        self.test_start = datetime.now()
        
        # Log storage
        self.conversations: List[Dict[str, Any]] = []
        self.vitals: List[Dict[str, Any]] = []
        self.behaviors: List[Dict[str, Any]] = []
        self.events: List[Dict[str, Any]] = []
        
        self._log_event("test_started", {
            "test_name": test_name,
            "timestamp": self.test_start.isoformat()
        })
    
    def log_conversation(
        self,
        conversation_type: str,
        prompt: str,
        response: str,
        metadata: Optional[Dict[str, Any]] = None
    ):
        """Log LLM conversation (prompt + response)"""
        entry = {
            "timestamp": datetime.now().isoformat(),
            "elapsed": time.time() - self.start_time,
            "type": conversation_type,
            "prompt": prompt,
            "response": response,
            "metadata": metadata or {}
        }
        self.conversations.append(entry)
        self._log_event("conversation", {
            "type": conversation_type,
            "prompt_length": len(prompt),
            "response_length": len(response)
        })
    
    def log_vitals(
        self,
        cycle: int,
        total_neurons: int,
        active_neurons: int,
        neuron_types: Dict[str, int],
        average_fitness: float = 0.0,
        metadata: Optional[Dict[str, Any]] = None
    ):
        """Log network vitals (state snapshot)"""
        entry = {
            "timestamp": datetime.now().isoformat(),
            "elapsed": time.time() - self.start_time,
            "cycle": cycle,
            "total_neurons": total_neurons,
            "active_neurons": active_neurons,
            "activation_rate": active_neurons / total_neurons if total_neurons > 0 else 0,
            "neuron_types": neuron_types,
            "average_fitness": average_fitness,
            "metadata": metadata or {}
        }
        self.vitals.append(entry)
    
    def log_behavior(
        self,
        behavior_type: str,
        action: str,
        reasoning: str,
        confidence: float = 0.0,
        metadata: Optional[Dict[str, Any]] = None
    ):
        """Log decision/behavior (action + reasoning)"""
        entry = {
            "timestamp": datetime.now().isoformat(),
            "elapsed": time.time() - self.start_time,
            "behavior_type": behavior_type,
            "action": action,
            "reasoning": reasoning,
            "confidence": confidence,
            "metadata": metadata or {}
        }
        self.behaviors.append(entry)
        self._log_event("behavior", {
            "type": behavior_type,
            "action": action,
            "confidence": confidence
        })
    
    def _log_event(self, event_type: str, data: Dict[str, Any]):
        """Log general event"""
        entry = {
            "timestamp": datetime.now().isoformat(),
            "elapsed": time.time() - self.start_time,
            "event_type": event_type,
            "data": data
        }
        self.events.append(entry)
    
    def save_logs(self):
        """Save all logs to files"""
        # Save conversations log
        conversations_file = self.output_dir / "conversations.json"
        with open(conversations_file, 'w', encoding='utf-8') as f:
            json.dump({
                "test_name": self.test_name,
                "test_start": self.test_start.isoformat(),
                "total_conversations": len(self.conversations),
                "conversations": self.conversations
            }, f, indent=2, ensure_ascii=False)
        
        # Save vitals log
        vitals_file = self.output_dir / "vitals.json"
        with open(vitals_file, 'w', encoding='utf-8') as f:
            json.dump({
                "test_name": self.test_name,
                "test_start": self.test_start.isoformat(),
                "total_snapshots": len(self.vitals),
                "vitals": self.vitals
            }, f, indent=2)
        
        # Save behavior log
        behavior_file = self.output_dir / "behavior.json"
        with open(behavior_file, 'w', encoding='utf-8') as f:
            json.dump({
                "test_name": self.test_name,
                "test_start": self.test_start.isoformat(),
                "total_behaviors": len(self.behaviors),
                "behaviors": self.behaviors
            }, f, indent=2, ensure_ascii=False)
        
        # Save events log
        events_file = self.output_dir / "events.json"
        with open(events_file, 'w', encoding='utf-8') as f:
            json.dump({
                "test_name": self.test_name,
                "test_start": self.test_start.isoformat(),
                "total_events": len(self.events),
                "events": self.events
            }, f, indent=2)
        
        # Generate human-readable summary
        self._generate_summary()
        
        return {
            "conversations": str(conversations_file),
            "vitals": str(vitals_file),
            "behavior": str(behavior_file),
            "events": str(events_file)
        }
    
    def _generate_summary(self):
        """Generate human-readable summary"""
        summary_file = self.output_dir / "log_summary.md"
        
        with open(summary_file, 'w', encoding='utf-8') as f:
            f.write(f"# Test Log Summary: {self.test_name}\n\n")
            f.write(f"**Test Start:** {self.test_start.strftime('%Y-%m-%d %H:%M:%S')}\n\n")
            f.write(f"**Duration:** {time.time() - self.start_time:.2f}s\n\n")
            
            f.write(f"## Statistics\n\n")
            f.write(f"- **Conversations:** {len(self.conversations)}\n")
            f.write(f"- **Vitals Snapshots:** {len(self.vitals)}\n")
            f.write(f"- **Behaviors Logged:** {len(self.behaviors)}\n")
            f.write(f"- **Total Events:** {len(self.events)}\n\n")
            
            # Conversation summary
            if self.conversations:
                f.write(f"## Conversations\n\n")
                for i, conv in enumerate(self.conversations, 1):
                    f.write(f"### {i}. {conv['type']} (t={conv['elapsed']:.1f}s)\n\n")
                    f.write(f"**Prompt:**\n```\n{conv['prompt'][:500]}...\n```\n\n")
                    f.write(f"**Response:**\n```\n{conv['response'][:500]}...\n```\n\n")
            
            # Vitals summary
            if self.vitals:
                f.write(f"## Vitals Timeline\n\n")
                f.write(f"| Cycle | Time | Total Neurons | Active | Activation Rate | Avg Fitness |\n")
                f.write(f"|-------|------|---------------|--------|-----------------|-------------|\n")
                for v in self.vitals:
                    f.write(f"| {v['cycle']} | {v['elapsed']:.1f}s | {v['total_neurons']} | {v['active_neurons']} | {v['activation_rate']:.1%} | {v['average_fitness']:.3f} |\n")
                f.write(f"\n")
            
            # Behavior summary
            if self.behaviors:
                f.write(f"## Behaviors\n\n")
                for i, b in enumerate(self.behaviors, 1):
                    f.write(f"### {i}. {b['behavior_type']} (t={b['elapsed']:.1f}s)\n\n")
                    f.write(f"**Action:** {b['action']}\n\n")
                    f.write(f"**Reasoning:** {b['reasoning']}\n\n")
                    f.write(f"**Confidence:** {b['confidence']:.2f}\n\n")
            
            # Event timeline
            f.write(f"## Event Timeline\n\n")
            for event in self.events:
                f.write(f"- **{event['elapsed']:.1f}s** - {event['event_type']}: {event['data']}\n")
    
    def get_summary_stats(self) -> Dict[str, Any]:
        """Get summary statistics"""
        return {
            "test_name": self.test_name,
            "duration": time.time() - self.start_time,
            "conversations": len(self.conversations),
            "vitals_snapshots": len(self.vitals),
            "behaviors": len(self.behaviors),
            "events": len(self.events)
        }
