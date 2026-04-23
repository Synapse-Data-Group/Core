import time
import random
from typing import Dict, List, Optional, Any
from enum import Enum


class EmotionalState(Enum):
    NEUTRAL = "neutral"
    CONFIDENT = "confident"
    FRUSTRATED = "frustrated"
    EXCITED = "excited"
    ANXIOUS = "anxious"
    SATISFIED = "satisfied"
    DISAPPOINTED = "disappointed"
    DETERMINED = "determined"


class EmotionEngine:
    def __init__(self, agent_id: str):
        self.agent_id = agent_id
        self.current_state = EmotionalState.NEUTRAL
        self.emotion_intensity = 0.5
        self.emotion_history: List[Dict[str, Any]] = []
        
        self.emotion_modifiers = {
            "aggressiveness": 0.0,
            "creativity": 0.0,
            "confidence": 0.0,
            "defensiveness": 0.0,
            "supportiveness": 0.0
        }
        
        self.frustration_threshold = 0.7
        self.excitement_threshold = 0.7
        self.decay_rate = 0.1
    
    def process_event(self, event_type: str, outcome: float, context: Dict[str, Any]):
        """Process an event and update emotional state"""
        
        previous_state = self.current_state
        
        if event_type == "proposal_accepted":
            if outcome > 0.7:
                self.current_state = EmotionalState.EXCITED
                self.emotion_intensity = 0.8
            else:
                self.current_state = EmotionalState.SATISFIED
                self.emotion_intensity = 0.6
        
        elif event_type == "proposal_rejected":
            if outcome < 0.3:
                self.current_state = EmotionalState.DISAPPOINTED
                self.emotion_intensity = 0.7
            else:
                self.current_state = EmotionalState.DETERMINED
                self.emotion_intensity = 0.6
        
        elif event_type == "challenged":
            challenge_count = context.get("challenge_count", 0)
            if challenge_count > 2:
                self.current_state = EmotionalState.FRUSTRATED
                self.emotion_intensity = min(1.0, 0.5 + challenge_count * 0.1)
            else:
                self.current_state = EmotionalState.DETERMINED
                self.emotion_intensity = 0.5
        
        elif event_type == "rebuttal_successful":
            self.current_state = EmotionalState.CONFIDENT
            self.emotion_intensity = 0.7
        
        elif event_type == "debate_won":
            self.current_state = EmotionalState.EXCITED
            self.emotion_intensity = 0.9
        
        elif event_type == "debate_lost":
            self.current_state = EmotionalState.DISAPPOINTED
            self.emotion_intensity = 0.6
        
        self._update_modifiers()
        
        self.emotion_history.append({
            "timestamp": time.time(),
            "event_type": event_type,
            "previous_state": previous_state.value,
            "new_state": self.current_state.value,
            "intensity": self.emotion_intensity,
            "outcome": outcome
        })
    
    def _update_modifiers(self):
        """Update personality modifiers based on emotional state"""
        
        if self.current_state == EmotionalState.FRUSTRATED:
            self.emotion_modifiers["aggressiveness"] = self.emotion_intensity * 0.3
            self.emotion_modifiers["defensiveness"] = self.emotion_intensity * 0.2
            self.emotion_modifiers["creativity"] = -self.emotion_intensity * 0.1
        
        elif self.current_state == EmotionalState.CONFIDENT:
            self.emotion_modifiers["aggressiveness"] = self.emotion_intensity * 0.2
            self.emotion_modifiers["confidence"] = self.emotion_intensity * 0.3
            self.emotion_modifiers["creativity"] = self.emotion_intensity * 0.1
        
        elif self.current_state == EmotionalState.EXCITED:
            self.emotion_modifiers["creativity"] = self.emotion_intensity * 0.3
            self.emotion_modifiers["supportiveness"] = self.emotion_intensity * 0.2
            self.emotion_modifiers["aggressiveness"] = -self.emotion_intensity * 0.1
        
        elif self.current_state == EmotionalState.ANXIOUS:
            self.emotion_modifiers["defensiveness"] = self.emotion_intensity * 0.3
            self.emotion_modifiers["confidence"] = -self.emotion_intensity * 0.2
            self.emotion_modifiers["aggressiveness"] = -self.emotion_intensity * 0.1
        
        elif self.current_state == EmotionalState.DISAPPOINTED:
            self.emotion_modifiers["confidence"] = -self.emotion_intensity * 0.2
            self.emotion_modifiers["creativity"] = -self.emotion_intensity * 0.1
        
        elif self.current_state == EmotionalState.DETERMINED:
            self.emotion_modifiers["aggressiveness"] = self.emotion_intensity * 0.15
            self.emotion_modifiers["defensiveness"] = self.emotion_intensity * 0.15
        
        else:
            for key in self.emotion_modifiers:
                self.emotion_modifiers[key] = 0.0
    
    def apply_to_personality(self, personality: Dict[str, float]) -> Dict[str, float]:
        """Apply emotional modifiers to personality traits"""
        
        modified = personality.copy()
        
        for trait, modifier in self.emotion_modifiers.items():
            if trait in modified:
                modified[trait] = max(0.0, min(1.0, modified[trait] + modifier))
        
        return modified
    
    def decay_emotion(self):
        """Gradually return to neutral state"""
        
        self.emotion_intensity = max(0.0, self.emotion_intensity - self.decay_rate)
        
        if self.emotion_intensity < 0.3:
            self.current_state = EmotionalState.NEUTRAL
            self.emotion_intensity = 0.5
            self._update_modifiers()
    
    def emotional_contagion(self, other_emotion: 'EmotionEngine', strength: float = 0.3):
        """Spread emotion from another agent"""
        
        if other_emotion.emotion_intensity > 0.6:
            influence = other_emotion.emotion_intensity * strength
            
            if random.random() < influence:
                self.current_state = other_emotion.current_state
                self.emotion_intensity = min(1.0, self.emotion_intensity + influence)
                self._update_modifiers()
    
    def get_emotional_tone(self) -> str:
        """Get text describing current emotional tone"""
        
        tones = {
            EmotionalState.NEUTRAL: ["calmly", "objectively", "rationally"],
            EmotionalState.CONFIDENT: ["confidently", "assertively", "boldly"],
            EmotionalState.FRUSTRATED: ["frustratedly", "impatiently", "tersely"],
            EmotionalState.EXCITED: ["enthusiastically", "eagerly", "passionately"],
            EmotionalState.ANXIOUS: ["cautiously", "hesitantly", "nervously"],
            EmotionalState.SATISFIED: ["contentedly", "pleasantly", "approvingly"],
            EmotionalState.DISAPPOINTED: ["disappointedly", "reluctantly", "regretfully"],
            EmotionalState.DETERMINED: ["resolutely", "firmly", "steadfastly"]
        }
        
        tone_list = tones.get(self.current_state, ["neutrally"])
        return random.choice(tone_list)
    
    def should_escalate_response(self) -> bool:
        """Determine if emotion should escalate response"""
        
        return (self.current_state in [EmotionalState.FRUSTRATED, EmotionalState.DETERMINED] and 
                self.emotion_intensity > 0.6)
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            "agent_id": self.agent_id,
            "current_state": self.current_state.value,
            "intensity": self.emotion_intensity,
            "modifiers": self.emotion_modifiers.copy(),
            "history_length": len(self.emotion_history)
        }
    
    def get_stats(self) -> Dict[str, Any]:
        """Get emotion statistics"""
        
        state_counts = {}
        for record in self.emotion_history:
            state = record["new_state"]
            state_counts[state] = state_counts.get(state, 0) + 1
        
        return {
            "current_state": self.current_state.value,
            "intensity": self.emotion_intensity,
            "total_transitions": len(self.emotion_history),
            "state_distribution": state_counts,
            "avg_intensity": sum(r["intensity"] for r in self.emotion_history) / len(self.emotion_history) if self.emotion_history else 0.5
        }
