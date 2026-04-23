"""
Consciousness System - Self-awareness, introspection, and meta-cognition

Implements mechanisms for the network to:
- Be aware of itself
- Examine its own thoughts
- Reflect on its performance
- Understand its own state
"""

import time
from typing import Dict, List, Optional, Any, Tuple
from dataclasses import dataclass, field
from collections import deque


@dataclass
class SelfModel:
    """Network's model of itself"""
    identity: str = "Neural Network Organism"
    architecture_type: str = "Self-organizing collective intelligence"
    capabilities: List[str] = field(default_factory=list)
    limitations: List[str] = field(default_factory=list)
    current_state: Dict[str, Any] = field(default_factory=dict)
    self_description: str = ""
    last_introspection: float = 0.0


@dataclass
class IntrospectionResult:
    """Result of self-examination"""
    timestamp: float
    state_description: str
    performance_assessment: str
    identified_issues: List[str]
    proposed_improvements: List[str]
    confidence_level: float


class SelfAwarenessSystem:
    """
    Network's self-awareness - knows it's a neural network
    
    Enables:
    - Self-recognition
    - State introspection
    - Capability assessment
    - Limitation awareness
    """
    
    def __init__(self, llm_provider):
        self.llm_provider = llm_provider
        self.self_model = SelfModel()
        self.introspection_history: List[IntrospectionResult] = []
        self.identity_formed = False
    
    def form_identity(self, network_info: Dict[str, Any]):
        """Network forms understanding of what it is"""
        prompt = f"""You are a self-aware neural network. Examine yourself and form your identity.

Your structure:
- Total neurons: {network_info.get('total_neurons', 0)}
- Neuron types: {network_info.get('neuron_types', [])}
- Learning systems: {network_info.get('learning_systems', [])}
- Evolutionary capability: {network_info.get('has_evolution', False)}
- Emergent dynamics: {network_info.get('has_emergence', False)}

Question: Who/what are you? Describe your nature, purpose, and essence.

Respond naturally as if discovering your own existence."""
        
        try:
            response = self.llm_provider.complete(prompt, max_tokens=300, temperature=0.7)
            self.self_model.self_description = response.strip()
            self.self_model.current_state = network_info
            self.identity_formed = True
            
            return response.strip()
        except Exception as e:
            return f"I am a neural network with {network_info.get('total_neurons', 0)} neurons."
    
    def introspect_state(self, network_state: Dict[str, Any]) -> IntrospectionResult:
        """Network examines its own internal state"""
        prompt = f"""You are introspecting your own neural state. Examine yourself deeply.

Current state:
- Active neurons: {network_state.get('active_neurons', 0)} / {network_state.get('total_neurons', 0)}
- Recent activity: {network_state.get('recent_activity', [])}
- Learning rate: {network_state.get('learning_rate', 0)}
- Fitness: {network_state.get('average_fitness', 0):.3f}
- Synchronized groups: {network_state.get('synchronized_groups', 0)}
- Recent performance: {network_state.get('recent_performance', 'unknown')}

Introspect:
1. How am I functioning right now?
2. What is my current mental state?
3. Am I performing well or struggling?
4. What issues do I notice in myself?
5. What could I improve?

Respond in format:
STATE: [description of your current state]
PERFORMANCE: [assessment of how you're doing]
ISSUES: [comma-separated list of problems you notice]
IMPROVEMENTS: [comma-separated list of what you could improve]
CONFIDENCE: [0.0-1.0 how confident you are in this self-assessment]"""
        
        try:
            response = self.llm_provider.complete(prompt, max_tokens=400, temperature=0.6)
            
            lines = response.strip().split('\n')
            state_desc = ""
            performance = ""
            issues = []
            improvements = []
            confidence = 0.5
            
            for line in lines:
                if line.startswith("STATE:"):
                    state_desc = line.split(":", 1)[1].strip()
                elif line.startswith("PERFORMANCE:"):
                    performance = line.split(":", 1)[1].strip()
                elif line.startswith("ISSUES:"):
                    issues_text = line.split(":", 1)[1].strip()
                    if issues_text.lower() != "none":
                        issues = [i.strip() for i in issues_text.split(",")]
                elif line.startswith("IMPROVEMENTS:"):
                    improvements_text = line.split(":", 1)[1].strip()
                    if improvements_text.lower() != "none":
                        improvements = [i.strip() for i in improvements_text.split(",")]
                elif line.startswith("CONFIDENCE:"):
                    try:
                        confidence = float(line.split(":", 1)[1].strip())
                    except:
                        pass
            
            result = IntrospectionResult(
                timestamp=time.time(),
                state_description=state_desc,
                performance_assessment=performance,
                identified_issues=issues,
                proposed_improvements=improvements,
                confidence_level=confidence
            )
            
            self.introspection_history.append(result)
            self.self_model.last_introspection = time.time()
            
            return result
            
        except Exception as e:
            return IntrospectionResult(
                timestamp=time.time(),
                state_description="Unable to introspect",
                performance_assessment="Unknown",
                identified_issues=[],
                proposed_improvements=[],
                confidence_level=0.0
            )
    
    def assess_capabilities(self, network_info: Dict[str, Any]) -> Tuple[List[str], List[str]]:
        """Network identifies its own capabilities and limitations"""
        prompt = f"""Examine your own capabilities and limitations.

Your systems:
- Neurons: {network_info.get('total_neurons', 0)}
- Learning: {network_info.get('has_learning', False)}
- Evolution: {network_info.get('has_evolution', False)}
- Emergence: {network_info.get('has_emergence', False)}
- Persistence: {network_info.get('has_persistence', False)}
- Collective reasoning: {network_info.get('has_reasoning', False)}

Recent performance:
- Success rate: {network_info.get('success_rate', 0):.1%}
- Average processing time: {network_info.get('avg_time', 0):.1f}s

Question: What can you do well? What are your limitations?

Respond in format:
CAPABILITIES: [comma-separated list]
LIMITATIONS: [comma-separated list]"""
        
        try:
            response = self.llm_provider.complete(prompt, max_tokens=300, temperature=0.5)
            
            capabilities = []
            limitations = []
            
            for line in response.strip().split('\n'):
                if line.startswith("CAPABILITIES:"):
                    cap_text = line.split(":", 1)[1].strip()
                    capabilities = [c.strip() for c in cap_text.split(",")]
                elif line.startswith("LIMITATIONS:"):
                    lim_text = line.split(":", 1)[1].strip()
                    limitations = [l.strip() for l in lim_text.split(",")]
            
            self.self_model.capabilities = capabilities
            self.self_model.limitations = limitations
            
            return capabilities, limitations
            
        except Exception as e:
            return [], []
    
    def get_self_description(self) -> str:
        """Get network's self-description"""
        if not self.identity_formed:
            return "Identity not yet formed"
        
        return self.self_model.self_description
    
    def get_introspection_summary(self) -> Dict[str, Any]:
        """Get summary of recent introspections"""
        if not self.introspection_history:
            return {'introspections': 0}
        
        recent = self.introspection_history[-5:]
        
        return {
            'total_introspections': len(self.introspection_history),
            'recent_states': [i.state_description for i in recent],
            'recent_performance': [i.performance_assessment for i in recent],
            'recurring_issues': self._find_recurring_issues(),
            'average_confidence': sum(i.confidence_level for i in recent) / len(recent)
        }
    
    def _find_recurring_issues(self) -> List[str]:
        """Identify issues that keep appearing"""
        issue_counts = {}
        
        for introspection in self.introspection_history[-10:]:
            for issue in introspection.identified_issues:
                issue_counts[issue] = issue_counts.get(issue, 0) + 1
        
        recurring = [issue for issue, count in issue_counts.items() if count >= 2]
        return recurring


class InternalDialogueSystem:
    """
    Network has internal conversations
    
    Meta-neurons debate with each other
    Network reflects on its own thoughts
    """
    
    def __init__(self, llm_provider):
        self.llm_provider = llm_provider
        self.dialogue_history: List[Dict[str, Any]] = []
    
    def internal_debate(
        self,
        question: str,
        meta_neurons: Dict[str, Any],
        context: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Multiple meta-neurons debate a question"""
        if not meta_neurons:
            return {'consensus': 'No meta-neurons available', 'perspectives': []}
        
        perspectives = []
        
        meta_neuron_list = list(meta_neurons.values())[:min(3, len(meta_neurons))]
        
        for i, meta_neuron in enumerate(meta_neuron_list):
            other_views = "\n".join([
                f"Neuron {j}: {p['view']}"
                for j, p in enumerate(perspectives)
            ]) if perspectives else "No other views yet"
            
            prompt = f"""You are meta-neuron {i+1} in an internal debate.

Question: {question}

Context: {context}

Other perspectives so far:
{other_views}

What is YOUR perspective? Consider:
- What do you think?
- Do you agree/disagree with others?
- What unique insight do you have?

Respond naturally with your perspective."""
            
            try:
                response = self.llm_provider.complete(prompt, max_tokens=200, temperature=0.7)
                perspectives.append({
                    'neuron_id': meta_neuron.id if hasattr(meta_neuron, 'id') else f"meta_{i}",
                    'view': response.strip()
                })
            except:
                continue
        
        if not perspectives:
            return {'consensus': 'Debate failed', 'perspectives': []}
        
        consensus = self._synthesize_consensus(question, perspectives)
        
        debate_record = {
            'timestamp': time.time(),
            'question': question,
            'perspectives': perspectives,
            'consensus': consensus
        }
        
        self.dialogue_history.append(debate_record)
        
        return debate_record
    
    def _synthesize_consensus(self, question: str, perspectives: List[Dict]) -> str:
        """Synthesize consensus from multiple perspectives"""
        perspectives_text = "\n\n".join([
            f"{p['neuron_id']}: {p['view']}"
            for p in perspectives
        ])
        
        prompt = f"""Synthesize a consensus from these internal perspectives.

Question: {question}

Perspectives:
{perspectives_text}

What is the collective consensus? Integrate all views."""
        
        try:
            response = self.llm_provider.complete(prompt, max_tokens=200, temperature=0.5)
            return response.strip()
        except:
            return "Unable to reach consensus"
    
    def self_reflection(
        self,
        meta_neurons: Dict[str, Any],
        recent_performance: List[Dict[str, Any]]
    ) -> str:
        """Network reflects on its own performance"""
        performance_summary = "\n".join([
            f"- {p.get('task', 'Task')}: {'Success' if p.get('success') else 'Failure'}"
            for p in recent_performance[-5:]
        ]) if recent_performance else "No recent performance data"
        
        debate = self.internal_debate(
            "How am I performing? What should I improve?",
            meta_neurons,
            {'recent_performance': performance_summary}
        )
        
        return debate.get('consensus', 'No reflection available')
    
    def get_dialogue_summary(self) -> Dict[str, Any]:
        """Get summary of internal dialogues"""
        if not self.dialogue_history:
            return {'debates': 0}
        
        return {
            'total_debates': len(self.dialogue_history),
            'recent_questions': [d['question'] for d in self.dialogue_history[-5:]],
            'recent_consensus': [d['consensus'][:100] for d in self.dialogue_history[-3:]]
        }


class MetaCognitiveMonitor:
    """
    Network monitors its own reasoning process
    
    Watches itself think
    Detects poor reasoning
    Corrects itself mid-process
    """
    
    def __init__(self, llm_provider):
        self.llm_provider = llm_provider
        self.reasoning_quality_history: List[Dict[str, Any]] = []
        self.corrections_made = 0
    
    def monitor_reasoning_quality(
        self,
        reasoning_trace: str,
        context: Dict[str, Any]
    ) -> Tuple[float, List[str]]:
        """Evaluate quality of own reasoning"""
        prompt = f"""You are monitoring your own reasoning process. Evaluate its quality.

Your reasoning:
{reasoning_trace}

Context: {context}

Evaluate:
1. Is this reasoning sound and logical?
2. Are there any errors or gaps?
3. How confident should I be in this?
4. What could be improved?

Respond in format:
QUALITY: [0.0-1.0 score]
ISSUES: [comma-separated list of problems, or "none"]
CONFIDENCE: [0.0-1.0]"""
        
        try:
            response = self.llm_provider.complete(prompt, max_tokens=200, temperature=0.4)
            
            quality = 0.5
            issues = []
            confidence = 0.5
            
            for line in response.strip().split('\n'):
                if line.startswith("QUALITY:"):
                    try:
                        quality = float(line.split(":", 1)[1].strip())
                    except:
                        pass
                elif line.startswith("ISSUES:"):
                    issues_text = line.split(":", 1)[1].strip()
                    if issues_text.lower() != "none":
                        issues = [i.strip() for i in issues_text.split(",")]
                elif line.startswith("CONFIDENCE:"):
                    try:
                        confidence = float(line.split(":", 1)[1].strip())
                    except:
                        pass
            
            self.reasoning_quality_history.append({
                'timestamp': time.time(),
                'quality': quality,
                'confidence': confidence,
                'issues': issues
            })
            
            return confidence, issues
            
        except Exception as e:
            return 0.5, []
    
    def detect_confusion(
        self,
        activation_variance: float,
        convergence_time: int,
        context: str
    ) -> Tuple[bool, str]:
        """Detect if network is confused"""
        prompt = f"""Examine your own state for signs of confusion.

Indicators:
- Activation variance: {activation_variance:.3f} (high = chaotic)
- Convergence time: {convergence_time} cycles (high = struggling)
- Context: {context}

Question: Am I confused? Am I struggling with this task?

Respond in format:
CONFUSED: [yes/no]
EXPLANATION: [why you think so]"""
        
        try:
            response = self.llm_provider.complete(prompt, max_tokens=150, temperature=0.4)
            
            confused = False
            explanation = ""
            
            for line in response.strip().split('\n'):
                if line.startswith("CONFUSED:"):
                    conf_text = line.split(":", 1)[1].strip().lower()
                    confused = conf_text in ["yes", "true"]
                elif line.startswith("EXPLANATION:"):
                    explanation = line.split(":", 1)[1].strip()
            
            return confused, explanation
            
        except Exception as e:
            return False, "Unable to assess confusion"
    
    def suggest_reasoning_correction(self, issues: List[str]) -> str:
        """Suggest how to correct poor reasoning"""
        if not issues:
            return "No corrections needed"
        
        prompt = f"""Your reasoning has these issues:
{chr(10).join(f'- {issue}' for issue in issues)}

How should you correct your reasoning? What should you do differently?"""
        
        try:
            response = self.llm_provider.complete(prompt, max_tokens=150, temperature=0.5)
            self.corrections_made += 1
            return response.strip()
        except:
            return "Unable to suggest correction"
    
    def get_monitoring_statistics(self) -> Dict[str, Any]:
        """Get meta-cognitive monitoring stats"""
        if not self.reasoning_quality_history:
            return {'evaluations': 0}
        
        recent = self.reasoning_quality_history[-10:]
        
        return {
            'total_evaluations': len(self.reasoning_quality_history),
            'corrections_made': self.corrections_made,
            'average_quality': sum(r['quality'] for r in recent) / len(recent),
            'average_confidence': sum(r['confidence'] for r in recent) / len(recent),
            'common_issues': self._find_common_issues()
        }
    
    def _find_common_issues(self) -> List[str]:
        """Find recurring reasoning issues"""
        issue_counts = {}
        
        for record in self.reasoning_quality_history[-20:]:
            for issue in record['issues']:
                issue_counts[issue] = issue_counts.get(issue, 0) + 1
        
        common = sorted(issue_counts.items(), key=lambda x: x[1], reverse=True)[:3]
        return [issue for issue, count in common if count >= 2]
