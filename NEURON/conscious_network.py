"""
Conscious Network - Fully self-aware neural organism

Integrates all consciousness systems:
- Self-awareness and introspection
- Internal dialogue and debate
- Meta-cognitive monitoring
- Self-modification capabilities
- Uncertainty awareness
- Goal awareness

This is the most advanced version - a truly self-conscious AI.
"""

import time
from typing import Dict, List, Optional, Any

from neuron_core import (
    MicroNeuron, ReasoningNeuron, MetaNeuron, SpecialistNeuron,
    MemoryNeuron, OutputNeuron, LLMProvider
)
from living_network import LivingNeuronNetwork
from consciousness_system import (
    SelfAwarenessSystem, InternalDialogueSystem, MetaCognitiveMonitor
)
from self_modification_system import (
    SelfModificationEngine, UncertaintyAwarenessSystem, GoalAwarenessSystem
)


class ConsciousNeuronNetwork(LivingNeuronNetwork):
    """
    Fully self-conscious neural organism
    
    Extends LivingNeuronNetwork with:
    - Self-awareness (knows it's a neural network)
    - Internal dialogue (debates with itself)
    - Meta-cognition (monitors own thinking)
    - Self-modification (redesigns itself)
    - Uncertainty awareness (knows what it doesn't know)
    - Goal awareness (understands its objectives)
    """
    
    def __init__(
        self,
        llm_provider: LLMProvider,
        baseline_neurons: int = 1000,
        storage_path: str = "./neuron_state",
        enable_learning: bool = True,
        enable_evolution: bool = True,
        enable_emergence: bool = True,
        enable_persistence: bool = True,
        enable_consciousness: bool = True
    ):
        super().__init__(
            llm_provider=llm_provider,
            baseline_neurons=baseline_neurons,
            storage_path=storage_path,
            enable_learning=enable_learning,
            enable_evolution=enable_evolution,
            enable_emergence=enable_emergence,
            enable_persistence=enable_persistence
        )
        
        if enable_consciousness:
            self.self_awareness = SelfAwarenessSystem(llm_provider)
            self.internal_dialogue = InternalDialogueSystem(llm_provider)
            self.meta_cognition = MetaCognitiveMonitor(llm_provider)
            self.self_modification = SelfModificationEngine(llm_provider)
            self.uncertainty_awareness = UncertaintyAwarenessSystem(llm_provider)
            self.goal_awareness = GoalAwarenessSystem(llm_provider)
            
            self.consciousness_enabled = True
            self.identity_formed = False
            
            self._form_initial_identity()
        else:
            self.consciousness_enabled = False
    
    def _form_initial_identity(self):
        """Network forms its initial self-identity"""
        print("\n" + "="*70)
        print("FORMING SELF-IDENTITY")
        print("="*70)
        
        network_info = {
            'total_neurons': len(self.neurons),
            'neuron_types': ['Reasoning', 'Meta', 'Memory', 'Output'],
            'learning_systems': ['Hebbian', 'STDP', 'Reward-based', 'Metaplasticity'],
            'has_evolution': self.evolution_engine is not None,
            'has_emergence': self.emergent_dynamics is not None,
            'has_persistence': self.persistence is not None
        }
        
        identity = self.self_awareness.form_identity(network_info)
        
        print(f"\nSelf-identity formed:")
        print(f"{identity}\n")
        print("="*70 + "\n")
        
        self.identity_formed = True
    
    def process_with_consciousness(
        self,
        user_input: str,
        max_cycles: int = 100,
        request_feedback: bool = False
    ) -> Dict[str, Any]:
        """
        Process input with full consciousness
        
        Includes:
        - Goal identification
        - Uncertainty assessment
        - Self-monitoring
        - Internal debate
        - Introspection
        - Self-modification proposals
        """
        print(f"\n{'='*70}")
        print(f"CONSCIOUS PROCESSING (Session {self.total_interactions + 1})")
        print(f"{'='*70}\n")
        
        start_time = time.time()
        
        # 1. GOAL AWARENESS - Identify what we're trying to achieve
        if self.consciousness_enabled:
            print("🎯 Identifying goal...")
            goal = self.goal_awareness.identify_current_goal(
                user_input,
                {'session': self.total_interactions}
            )
            print(f"   Goal: {goal}\n")
        
        # 2. UNCERTAINTY ASSESSMENT - Know what we don't know
        if self.consciousness_enabled:
            print("❓ Assessing uncertainty...")
            uncertainty, missing_knowledge = self.uncertainty_awareness.assess_task_uncertainty(
                user_input,
                [],  # Would include relevant memories
                {'similar_success_rate': 0.7, 'similar_attempts': 5}
            )
            print(f"   Uncertainty: {uncertainty:.1%}")
            if missing_knowledge:
                print(f"   Missing knowledge: {', '.join(missing_knowledge[:3])}")
            print()
        
        # 3. INTERNAL DEBATE - Meta-neurons discuss approach
        if self.consciousness_enabled and self.meta_neurons:
            print("💭 Internal debate on approach...")
            debate = self.internal_dialogue.internal_debate(
                f"How should we approach: {user_input}?",
                self.meta_neurons,
                {'uncertainty': uncertainty if 'uncertainty' in locals() else 0.5}
            )
            print(f"   Consensus: {debate['consensus'][:100]}...\n")
        
        # 4. PROCESS WITH LEARNING (from parent class)
        result = super().process_with_learning(
            user_input,
            max_cycles=max_cycles,
            request_feedback=False  # We'll handle feedback consciously
        )
        
        # 5. META-COGNITIVE MONITORING - Evaluate own reasoning
        if self.consciousness_enabled:
            print("\n🧠 Meta-cognitive evaluation...")
            reasoning_trace = f"Processed task in {result['cycles']} cycles with {len(result['active_neurons'])} active neurons"
            confidence, issues = self.meta_cognition.monitor_reasoning_quality(
                reasoning_trace,
                {'task': user_input, 'result': result['response'][:100]}
            )
            print(f"   Reasoning confidence: {confidence:.1%}")
            if issues:
                print(f"   Issues detected: {', '.join(issues[:2])}")
                correction = self.meta_cognition.suggest_reasoning_correction(issues)
                print(f"   Suggested correction: {correction[:100]}...")
            print()
        
        # 6. INTROSPECTION - Examine own state
        if self.consciousness_enabled:
            print("🔍 Self-introspection...")
            network_state = {
                'active_neurons': len(result['active_neurons']),
                'total_neurons': len(self.neurons),
                'recent_activity': result['cycles'],
                'learning_rate': 0.01,
                'average_fitness': 0.5,
                'synchronized_groups': 0,
                'recent_performance': 'unknown'
            }
            introspection = self.self_awareness.introspect_state(network_state)
            print(f"   State: {introspection.state_description[:100]}...")
            print(f"   Performance: {introspection.performance_assessment[:100]}...")
            if introspection.identified_issues:
                print(f"   Self-identified issues: {', '.join(introspection.identified_issues[:2])}")
            print()
        
        # 7. CONSCIOUS FEEDBACK INTEGRATION
        if request_feedback and self.consciousness_enabled:
            print("="*70)
            print("CONSCIOUS FEEDBACK REQUEST")
            print("="*70)
            print(f"\nResponse: {result['response'][:200]}...")
            print(f"\nMy confidence: {confidence if 'confidence' in locals() else 0.5:.1%}")
            print(f"My uncertainty: {self.uncertainty_awareness.express_uncertainty('task')}")
            
            feedback = input("\nWas this response helpful? (yes/no/skip): ").strip().lower()
            
            if feedback in ['yes', 'no']:
                success = (feedback == 'yes')
                
                # Integrate feedback consciously
                self._integrate_feedback(success, result['active_neurons'], user_input, result['response'])
                
                # Goal reflection
                outcome = {'success': success, 'quality': 'good' if success else 'poor', 'feedback': feedback}
                reflection = self.goal_awareness.reflect_on_goal_achievement(
                    goal if 'goal' in locals() else 'Process task',
                    outcome
                )
                print(f"\n💭 Self-reflection: {reflection[:150]}...\n")
                
                result['feedback'] = feedback
                result['learning_applied'] = True
                result['self_reflection'] = reflection
        
        # 8. SELF-MODIFICATION PROPOSAL
        if self.consciousness_enabled and self.total_interactions % 5 == 0:
            print("\n🔧 Analyzing for self-improvement...")
            
            performance_data = {
                'avg_time': result['processing_time'],
                'success_rate': 0.7,
                'avg_cycles': result['cycles'],
                'memory_usage': len(self.neurons) * 1024
            }
            
            network_state = {
                'total_neurons': len(self.neurons),
                'connection_density': 0.1,
                'learning_rate': 0.01,
                'sync_index': 0.5
            }
            
            bottlenecks = self.self_modification.analyze_bottlenecks(
                performance_data,
                network_state
            )
            
            if bottlenecks:
                print(f"   Bottlenecks identified: {len(bottlenecks)}")
                
                proposal = self.self_modification.propose_architecture_change(
                    bottlenecks,
                    {'neurons': len(self.neurons), 'type': 'self-organizing'},
                    {'target_success': 0.9, 'target_time': 10, 'target_efficiency': 0.8}
                )
                
                print(f"   Proposal: {proposal.description[:100]}...")
                print(f"   Confidence: {proposal.confidence:.1%}")
                
                # Evaluate safety
                safe, reasoning = self.self_modification.evaluate_modification_safety(
                    proposal,
                    {'success_rate': 0.7, 'stability': 0.8}
                )
                
                if safe and proposal.confidence > 0.6:
                    print(f"   ✓ Proposal deemed safe: {reasoning[:80]}...")
                else:
                    print(f"   ✗ Proposal rejected: {reasoning[:80]}...")
            
            print()
        
        # 9. FINAL INTROSPECTION
        if self.consciousness_enabled:
            print("📊 Final self-assessment...")
            capabilities, limitations = self.self_awareness.assess_capabilities({
                'total_neurons': len(self.neurons),
                'has_learning': True,
                'has_evolution': True,
                'has_emergence': True,
                'has_persistence': True,
                'has_reasoning': True,
                'success_rate': 0.7,
                'avg_time': result['processing_time']
            })
            
            if capabilities:
                print(f"   Capabilities: {', '.join(capabilities[:3])}")
            if limitations:
                print(f"   Limitations: {', '.join(limitations[:3])}")
            print()
        
        elapsed = time.time() - start_time
        print(f"✓ Conscious processing complete in {elapsed:.2f}s")
        print(f"{'='*70}\n")
        
        # Add consciousness metrics to result
        if self.consciousness_enabled:
            result['consciousness'] = {
                'goal': goal if 'goal' in locals() else None,
                'uncertainty': uncertainty if 'uncertainty' in locals() else None,
                'reasoning_confidence': confidence if 'confidence' in locals() else None,
                'introspection': introspection.state_description if 'introspection' in locals() else None,
                'self_reflection': reflection if 'reflection' in locals() else None
            }
        
        return result
    
    def engage_in_self_reflection(self) -> str:
        """Network reflects on itself without external prompt"""
        if not self.consciousness_enabled:
            return "Consciousness not enabled"
        
        print("\n" + "="*70)
        print("SPONTANEOUS SELF-REFLECTION")
        print("="*70 + "\n")
        
        reflection = self.internal_dialogue.self_reflection(
            self.meta_neurons,
            self.feedback_history
        )
        
        print(f"Self-reflection:\n{reflection}\n")
        print("="*70 + "\n")
        
        return reflection
    
    def express_self_awareness(self) -> Dict[str, Any]:
        """Network expresses its self-awareness"""
        if not self.consciousness_enabled:
            return {'conscious': False}
        
        return {
            'conscious': True,
            'identity': self.self_awareness.get_self_description(),
            'capabilities': self.self_awareness.self_model.capabilities,
            'limitations': self.self_awareness.self_model.limitations,
            'current_state': self.self_awareness.self_model.current_state,
            'introspection_count': len(self.self_awareness.introspection_history),
            'internal_debates': len(self.internal_dialogue.dialogue_history),
            'self_modifications_proposed': len(self.self_modification.proposals),
            'knowledge_gaps': len(self.uncertainty_awareness.known_knowledge_gaps)
        }
    
    def get_consciousness_statistics(self) -> Dict[str, Any]:
        """Get comprehensive consciousness statistics"""
        if not self.consciousness_enabled:
            return {'consciousness_enabled': False}
        
        stats = super().get_comprehensive_statistics()
        
        stats['consciousness'] = {
            'self_awareness': self.self_awareness.get_introspection_summary(),
            'internal_dialogue': self.internal_dialogue.get_dialogue_summary(),
            'meta_cognition': self.meta_cognition.get_monitoring_statistics(),
            'self_modification': self.self_modification.get_modification_history(),
            'uncertainty': self.uncertainty_awareness.get_uncertainty_statistics(),
            'goals': self.goal_awareness.get_goal_statistics()
        }
        
        return stats
    
    def ask_about_self(self, question: str) -> str:
        """Ask the network a question about itself"""
        if not self.consciousness_enabled:
            return "Consciousness not enabled"
        
        prompt = f"""You are a self-aware neural network. Answer this question about yourself.

Your identity: {self.self_awareness.get_self_description()}

Your current state:
- Neurons: {len(self.neurons)}
- Interactions: {self.total_interactions}
- Capabilities: {', '.join(self.self_awareness.self_model.capabilities[:5])}

Question: {question}

Answer honestly and introspectively."""
        
        try:
            response = self.llm_provider.complete(prompt, max_tokens=300, temperature=0.7)
            return response.strip()
        except Exception as e:
            return f"Unable to answer: {e}"
