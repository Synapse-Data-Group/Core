from clm.neurons.base import (
    MicroNeuron, NeuronType, SynapticConnection, NeuronState,
    SensoryNeuron, AssociationNeuron, MemoryNeuron,
    InhibitoryNeuron, OutputNeuron,
)
from clm.neurons.hebbian import TriFactorLearner, PredictionRecord
HebbianLearner = TriFactorLearner  # backwards-compat alias
from clm.neurons.network import NeuronNetwork

__all__ = [
    "MicroNeuron", "NeuronType", "SynapticConnection", "NeuronState",
    "SensoryNeuron", "AssociationNeuron", "MemoryNeuron",
    "InhibitoryNeuron", "OutputNeuron",
    "TriFactorLearner", "PredictionRecord", "HebbianLearner", "NeuronNetwork",
]
