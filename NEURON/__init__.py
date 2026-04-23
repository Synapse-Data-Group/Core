"""
Neuron - Self-Organizing Neural Intelligence System

A living neural organism that dynamically creates specialized neurons on-demand,
replacing fixed agent/MCP architectures with adaptive collective intelligence.

Research tool for advancing behavioral AI research.
"""

from neuron_core import (
    MicroNeuron,
    ReasoningNeuron,
    MetaNeuron,
    SpecialistNeuron,
    MemoryNeuron,
    OutputNeuron,
    NeuronType,
    LLMProvider,
    OpenAIProvider,
    AnthropicProvider,
    GoogleProvider,
    OllamaProvider,
)

from vector_base import VirtualVectorBase, SemanticVector

from neuron_network import NeuronNetwork, CollectiveState

from living_network import LivingNeuronNetwork

from collective_reasoning import CollectiveReasoningEngine

from conscious_network import ConsciousNeuronNetwork

__version__ = "0.2.0"
__author__ = "Synapse Data / Ivan Lluch"
__license__ = "Apache-2.0"

__all__ = [
    "NeuronNetwork",
    "LivingNeuronNetwork",
    "ConsciousNeuronNetwork",
    "MicroNeuron",
    "ReasoningNeuron",
    "MetaNeuron",
    "SpecialistNeuron",
    "MemoryNeuron",
    "OutputNeuron",
    "NeuronType",
    "LLMProvider",
    "OpenAIProvider",
    "AnthropicProvider",
    "GoogleProvider",
    "OllamaProvider",
    "VirtualVectorBase",
    "SemanticVector",
    "CollectiveState",
    "CollectiveReasoningEngine",
]
