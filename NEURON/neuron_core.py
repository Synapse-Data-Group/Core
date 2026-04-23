"""
Neuron - Self-Organizing Neural Intelligence System

A living neural organism that dynamically creates specialized neurons on-demand,
replacing fixed agent/MCP architectures with adaptive collective intelligence.

Research focus: Demonstrating emergent capabilities through neural self-organization.

Zero dependencies (LLM providers optional: OpenAI, Anthropic, Google).
"""

import json
import time
import random
from typing import Dict, List, Optional, Any, Set, Tuple, Callable
from dataclasses import dataclass, field
from enum import Enum
from collections import defaultdict
from abc import ABC, abstractmethod


class NeuronType(Enum):
    """Types of neurons in the system"""
    REASONING = "reasoning"
    META = "meta"
    SPECIALIST = "specialist"
    MEMORY = "memory"
    EXCITATORY = "excitatory"
    INHIBITORY = "inhibitory"
    OUTPUT = "output"


@dataclass
class NeuronState:
    """Current state of a neuron"""
    activation: float = 0.0
    last_fired: float = 0.0
    fire_count: int = 0
    input_signals: Dict[str, float] = field(default_factory=dict)
    output_strength: float = 0.0
    is_active: bool = False


@dataclass
class Connection:
    """Connection between neurons"""
    source_id: str
    target_id: str
    weight: float
    last_updated: float = field(default_factory=time.time)
    
    def strengthen(self, amount: float = 0.01):
        """Hebbian learning - strengthen connection"""
        self.weight = min(1.0, self.weight + amount)
        self.last_updated = time.time()
    
    def weaken(self, amount: float = 0.01):
        """Weaken unused connection"""
        self.weight = max(-1.0, self.weight - amount)
        self.last_updated = time.time()


class LLMProvider(ABC):
    """Abstract base class for LLM providers"""
    
    @abstractmethod
    def complete(self, prompt: str, max_tokens: int = 500, temperature: float = 0.7) -> str:
        """Generate completion from prompt"""
        pass
    
    @abstractmethod
    def get_provider_name(self) -> str:
        """Return provider name"""
        pass


class OpenAIProvider(LLMProvider):
    """OpenAI GPT provider"""
    
    def __init__(self, api_key: Optional[str] = None, model: str = "gpt-4o-mini"):
        self.api_key = api_key
        self.model = model
        self._client = None
    
    def _get_client(self):
        if self._client is None:
            try:
                from openai import OpenAI
                self._client = OpenAI(api_key=self.api_key)
            except ImportError:
                raise ImportError("openai package not installed. Install with: pip install openai")
        return self._client
    
    def complete(self, prompt: str, max_tokens: int = 500, temperature: float = 0.7) -> str:
        client = self._get_client()
        response = client.chat.completions.create(
            model=self.model,
            messages=[{"role": "user", "content": prompt}],
            max_tokens=max_tokens,
            temperature=temperature
        )
        return response.choices[0].message.content
    
    def get_provider_name(self) -> str:
        return f"OpenAI-{self.model}"


class AnthropicProvider(LLMProvider):
    """Anthropic Claude provider"""
    
    def __init__(self, api_key: Optional[str] = None, model: str = "claude-3-5-sonnet-20241022"):
        self.api_key = api_key
        self.model = model
        self._client = None
    
    def _get_client(self):
        if self._client is None:
            try:
                from anthropic import Anthropic
                self._client = Anthropic(api_key=self.api_key)
            except ImportError:
                raise ImportError("anthropic package not installed. Install with: pip install anthropic")
        return self._client
    
    def complete(self, prompt: str, max_tokens: int = 500, temperature: float = 0.7) -> str:
        client = self._get_client()
        response = client.messages.create(
            model=self.model,
            max_tokens=max_tokens,
            temperature=temperature,
            messages=[{"role": "user", "content": prompt}]
        )
        return response.content[0].text
    
    def get_provider_name(self) -> str:
        return f"Anthropic-{self.model}"


class GoogleProvider(LLMProvider):
    """Google Gemini provider"""
    
    def __init__(self, api_key: Optional[str] = None, model: str = "gemini-pro"):
        self.api_key = api_key
        self.model = model
        self._client = None
    
    def _get_client(self):
        if self._client is None:
            try:
                import google.generativeai as genai
                genai.configure(api_key=self.api_key)
                self._client = genai.GenerativeModel(self.model)
            except ImportError:
                raise ImportError("google-generativeai package not installed. Install with: pip install google-generativeai")
        return self._client
    
    def complete(self, prompt: str, max_tokens: int = 500, temperature: float = 0.7) -> str:
        client = self._get_client()
        response = client.generate_content(
            prompt,
            generation_config={'max_output_tokens': max_tokens, 'temperature': temperature}
        )
        return response.text
    
    def get_provider_name(self) -> str:
        return f"Google-{self.model}"


class OllamaProvider(LLMProvider):
    """Ollama local LLM provider"""
    
    def __init__(self, model: str = "llama2", base_url: str = "http://localhost:11434"):
        self.model = model
        self.base_url = base_url
    
    def complete(self, prompt: str, max_tokens: int = 500, temperature: float = 0.7) -> str:
        try:
            import requests
            response = requests.post(
                f"{self.base_url}/api/generate",
                json={
                    "model": self.model,
                    "prompt": prompt,
                    "stream": False,
                    "options": {
                        "num_predict": max_tokens,
                        "temperature": temperature
                    }
                }
            )
            return response.json()['response']
        except ImportError:
            raise ImportError("requests package not installed. Install with: pip install requests")
    
    def get_provider_name(self) -> str:
        return f"Ollama-{self.model}"


class MicroNeuron(ABC):
    """
    Base class for all neurons
    
    Each neuron:
    - Has single specialized function
    - <1MB memory footprint
    - Participates in collective reasoning
    - No single neuron "knows" the answer
    """
    
    def __init__(
        self,
        neuron_id: str,
        neuron_type: NeuronType,
        function_description: str,
        threshold: float = 0.5,
        llm_provider: Optional[LLMProvider] = None
    ):
        self.id = neuron_id
        self.type = neuron_type
        self.function = function_description
        self.threshold = threshold
        self.state = NeuronState()
        self.connections: Dict[str, Connection] = {}
        self.semantic_vector: List[float] = []
        self.creation_time = time.time()
        self.last_activity = time.time()
        self.llm_provider = llm_provider
        self.metadata: Dict[str, Any] = {}
    
    def receive_signal(self, source_id: str, signal_strength: float):
        """Receive signal from another neuron"""
        self.state.input_signals[source_id] = signal_strength
        self.last_activity = time.time()
    
    def compute_activation(self) -> float:
        """Compute activation based on input signals and weights"""
        if not self.connections:
            return 0.0
        
        weighted_sum = sum(
            self.state.input_signals.get(conn.source_id, 0.0) * conn.weight
            for conn in self.connections.values()
        )
        
        self.state.activation = self._apply_activation_function(weighted_sum)
        return self.state.activation
    
    def _apply_activation_function(self, x: float) -> float:
        """Apply activation function (default: sigmoid)"""
        import math
        try:
            return 1 / (1 + math.exp(-x))
        except OverflowError:
            return 0.0 if x < 0 else 1.0
    
    def should_fire(self) -> bool:
        """Determine if neuron should fire"""
        return self.state.activation > self.threshold
    
    @abstractmethod
    def fire(self) -> Dict[str, Any]:
        """
        Execute neuron's specialized function
        Returns output to be sent to connected neurons
        """
        pass
    
    def add_connection(self, target_id: str, weight: float = 0.5):
        """Add connection to another neuron"""
        conn = Connection(
            source_id=self.id,
            target_id=target_id,
            weight=weight
        )
        self.connections[target_id] = conn
    
    def get_memory_footprint(self) -> int:
        """Estimate memory usage in bytes"""
        import sys
        return sys.getsizeof(self.__dict__)
    
    def to_dict(self) -> Dict[str, Any]:
        """Serialize neuron state"""
        return {
            'id': self.id,
            'type': self.type.value,
            'function': self.function,
            'activation': self.state.activation,
            'fire_count': self.state.fire_count,
            'connections': len(self.connections),
            'last_activity': self.last_activity
        }


class ReasoningNeuron(MicroNeuron):
    """
    LLM-powered reasoning neuron
    
    Each neuron has specialized reasoning capability
    Contributes to collective intelligence
    """
    
    def __init__(
        self,
        neuron_id: str,
        function_description: str,
        specialization: str = "general",
        llm_provider: Optional[LLMProvider] = None,
        threshold: float = 0.5
    ):
        super().__init__(neuron_id, NeuronType.REASONING, function_description, threshold, llm_provider)
        self.specialization = specialization
        self.reasoning_history: List[Dict[str, Any]] = []
    
    def fire(self) -> Dict[str, Any]:
        """Execute specialized reasoning"""
        self.state.fire_count += 1
        self.state.last_fired = time.time()
        self.state.is_active = True
        
        if not self.llm_provider:
            return {'output': 'No LLM provider configured', 'confidence': 0.0}
        
        context = self._build_context()
        prompt = self._construct_prompt(context)
        
        try:
            reasoning_output = self.llm_provider.complete(prompt, max_tokens=300, temperature=0.7)
            
            result = {
                'neuron_id': self.id,
                'specialization': self.specialization,
                'output': reasoning_output,
                'confidence': self.state.activation,
                'timestamp': time.time()
            }
            
            self.reasoning_history.append(result)
            self.state.output_strength = self.state.activation
            
            return result
            
        except Exception as e:
            return {'output': f'Error: {str(e)}', 'confidence': 0.0}
    
    def _build_context(self) -> Dict[str, Any]:
        """Build context from input signals"""
        return {
            'activation': self.state.activation,
            'input_signals': self.state.input_signals,
            'specialization': self.specialization,
            'function': self.function
        }
    
    def _construct_prompt(self, context: Dict[str, Any]) -> str:
        """Construct LLM prompt for this neuron's specialized function"""
        query = self.metadata.get('current_query', 'No query provided')
        
        return f"""You are a specialized reasoning neuron in a neural network.

User Query: {query}

Your specialization: {self.specialization}
Your function: {self.function}
Current activation level: {context['activation']:.2f}

Task: Reason about the user's query from your specialized perspective. Provide a concise insight (2-3 sentences) that contributes to answering the question.

Output:"""


class MetaNeuron(MicroNeuron):
    """
    Meta-neuron that manages network topology
    
    Responsibilities:
    - Detect capability gaps
    - Spawn specialized neurons on-demand
    - Prune unnecessary neurons
    - Manage network health
    """
    
    def __init__(
        self,
        neuron_id: str,
        function_description: str,
        llm_provider: Optional[LLMProvider] = None,
        threshold: float = 0.6
    ):
        super().__init__(neuron_id, NeuronType.META, function_description, threshold, llm_provider)
        self.spawn_history: List[Dict[str, Any]] = []
        self.prune_history: List[Dict[str, Any]] = []
    
    def fire(self) -> Dict[str, Any]:
        """Execute meta-level reasoning about network state"""
        self.state.fire_count += 1
        self.state.last_fired = time.time()
        self.state.is_active = True
        
        return {
            'neuron_id': self.id,
            'meta_function': self.function,
            'action': 'assess_network',
            'timestamp': time.time()
        }
    
    def assess_capability_gap(self, network_state: Dict[str, Any], task_description: str) -> Optional[Dict[str, Any]]:
        """
        Determine if network needs new specialized neurons
        
        This is where the magic happens - meta-neurons detect:
        "We need React neurons" or "We need Python neurons"
        """
        if not self.llm_provider:
            return None
        
        prompt = f"""You are a meta-neuron managing a neural network.

Current network state:
- Total neurons: {network_state.get('total_neurons', 0)}
- Active neurons: {network_state.get('active_neurons', 0)}
- Neuron types: {network_state.get('neuron_types', {})}

Task requested: {task_description}

Analyze if the network has sufficient specialized neurons for this task.
If not, specify what type of specialized neurons should be created.

Format your response as JSON:
{{
    "gap_detected": true/false,
    "missing_capability": "description",
    "suggested_neurons": ["type1", "type2"],
    "count": number,
    "reasoning": "why these neurons are needed"
}}

Response:"""
        
        try:
            response = self.llm_provider.complete(prompt, max_tokens=300, temperature=0.3)
            
            import re
            json_match = re.search(r'\{.*\}', response, re.DOTALL)
            if json_match:
                assessment = json.loads(json_match.group())
                return assessment
            
        except Exception as e:
            print(f"Meta-neuron assessment error: {e}")
        
        return None
    
    def design_specialist_neuron(self, specialization: str, task_context: str) -> Dict[str, Any]:
        """
        Design a new specialist neuron for a specific capability
        
        Example: Design "React development" neurons
        """
        if not self.llm_provider:
            return {}
        
        prompt = f"""You are designing a new specialized neuron for a neural network.

Specialization needed: {specialization}
Task context: {task_context}

Design this neuron by specifying:
1. Its specific function (what reasoning it performs)
2. What knowledge it needs to acquire
3. How it contributes to collective intelligence

Format as JSON:
{{
    "function_description": "specific function",
    "required_knowledge": ["knowledge1", "knowledge2"],
    "reasoning_focus": "what this neuron reasons about",
    "initial_prompt_template": "prompt template for this neuron"
}}

Response:"""
        
        try:
            response = self.llm_provider.complete(prompt, max_tokens=400, temperature=0.5)
            
            import re
            json_match = re.search(r'\{.*\}', response, re.DOTALL)
            if json_match:
                design = json.loads(json_match.group())
                design['specialization'] = specialization
                self.spawn_history.append({
                    'specialization': specialization,
                    'design': design,
                    'timestamp': time.time()
                })
                return design
            
        except Exception as e:
            print(f"Neuron design error: {e}")
        
        return {}


class SpecialistNeuron(ReasoningNeuron):
    """
    Dynamically created specialist neuron
    
    Created on-demand by meta-neurons
    Learns domain-specific knowledge
    Example: React neurons, Python neurons, Math neurons
    """
    
    def __init__(
        self,
        neuron_id: str,
        specialization: str,
        function_description: str,
        required_knowledge: List[str],
        llm_provider: Optional[LLMProvider] = None,
        threshold: float = 0.5
    ):
        super().__init__(neuron_id, function_description, specialization, llm_provider, threshold)
        self.type = NeuronType.SPECIALIST
        self.required_knowledge = required_knowledge
        self.knowledge_acquired: List[str] = []
        self.learning_history: List[Dict[str, Any]] = []
    
    def acquire_knowledge(self, knowledge_topic: str) -> bool:
        """
        Specialist neuron learns domain-specific knowledge
        
        Example: React neuron learns React hooks, components, etc.
        """
        if not self.llm_provider:
            return False
        
        prompt = f"""You are a specialist neuron learning about: {knowledge_topic}

Your specialization: {self.specialization}
Your function: {self.function}

Learn the key concepts about {knowledge_topic} that are relevant to your specialization.
Provide a concise summary (3-4 sentences) of what you've learned.

Learning summary:"""
        
        try:
            learning_output = self.llm_provider.complete(prompt, max_tokens=200, temperature=0.3)
            
            self.knowledge_acquired.append(knowledge_topic)
            self.learning_history.append({
                'topic': knowledge_topic,
                'summary': learning_output,
                'timestamp': time.time()
            })
            
            return True
            
        except Exception as e:
            print(f"Knowledge acquisition error: {e}")
            return False
    
    def _construct_prompt(self, context: Dict[str, Any]) -> str:
        """Construct prompt with acquired knowledge"""
        knowledge_context = "\n".join([
            f"- {entry['topic']}: {entry['summary'][:100]}..."
            for entry in self.learning_history[-3:]
        ])
        
        return f"""You are a specialist neuron in a neural network.

Your specialization: {self.specialization}
Your function: {self.function}

Knowledge you've acquired:
{knowledge_context if knowledge_context else "No specific knowledge yet"}

Current activation: {context['activation']:.2f}
Input signals: {len(context['input_signals'])} received

Task: Apply your specialized knowledge to contribute to the collective reasoning.

Output:"""


class MemoryNeuron(MicroNeuron):
    """
    Stores patterns and learned knowledge
    Enables pattern recognition and recall
    """
    
    def __init__(
        self,
        neuron_id: str,
        function_description: str,
        threshold: float = 0.4
    ):
        super().__init__(neuron_id, NeuronType.MEMORY, function_description, threshold)
        self.stored_patterns: List[Dict[str, Any]] = []
        self.pattern_activations: Dict[str, int] = defaultdict(int)
    
    def fire(self) -> Dict[str, Any]:
        """Recall stored patterns"""
        self.state.fire_count += 1
        self.state.last_fired = time.time()
        self.state.is_active = True
        
        relevant_patterns = [
            p for p in self.stored_patterns
            if p.get('activation_count', 0) > 2
        ]
        
        return {
            'neuron_id': self.id,
            'patterns_recalled': len(relevant_patterns),
            'patterns': relevant_patterns[:5],
            'timestamp': time.time()
        }
    
    def store_pattern(self, pattern: Dict[str, Any]):
        """Store a new pattern"""
        pattern['stored_at'] = time.time()
        pattern['activation_count'] = 0
        self.stored_patterns.append(pattern)
    
    def activate_pattern(self, pattern_id: str):
        """Mark pattern as activated (Hebbian strengthening)"""
        self.pattern_activations[pattern_id] += 1
        
        for pattern in self.stored_patterns:
            if pattern.get('id') == pattern_id:
                pattern['activation_count'] = self.pattern_activations[pattern_id]


class OutputNeuron(MicroNeuron):
    """
    Output neurons translate collective state into user-facing responses
    Like motor neurons - execute collective will
    """
    
    def __init__(
        self,
        neuron_id: str,
        output_type: str,
        threshold: float = 0.3
    ):
        super().__init__(neuron_id, NeuronType.OUTPUT, f"Output: {output_type}", threshold)
        self.output_type = output_type
        self.output_history: List[Dict[str, Any]] = []
    
    def fire(self) -> Dict[str, Any]:
        """Generate output from collective state"""
        self.state.fire_count += 1
        self.state.last_fired = time.time()
        self.state.is_active = True
        
        return {
            'neuron_id': self.id,
            'output_type': self.output_type,
            'activation': self.state.activation,
            'timestamp': time.time()
        }
    
    def integrate_collective_state(self, neuron_outputs: List[Dict[str, Any]]) -> str:
        """
        Integrate outputs from all neurons into final response
        No single neuron decides - this aggregates collective intelligence
        """
        if not neuron_outputs:
            return "No collective output available"
        
        outputs_by_confidence = sorted(
            neuron_outputs,
            key=lambda x: x.get('confidence', 0),
            reverse=True
        )
        
        integrated_output = "\n".join([
            f"{out.get('output', '')}"
            for out in outputs_by_confidence[:5]
            if out.get('output')
        ])
        
        self.output_history.append({
            'integrated_output': integrated_output,
            'sources': len(neuron_outputs),
            'timestamp': time.time()
        })
        
        return integrated_output
