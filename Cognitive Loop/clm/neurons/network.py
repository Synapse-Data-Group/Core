"""
CLM - Cognitive Language Model
neurons/network.py

The neuron network — sparse, self-organizing, continuously active.
Manages all neurons, propagates activation, applies Hebbian learning,
and grows/prunes its own topology over time.

No LLM calls here. Pure math.
"""

from __future__ import annotations
import math
import time
import uuid
import logging
from typing import Any, Dict, List, Optional, Set, Tuple, TYPE_CHECKING

from clm.neurons.base import (
    MicroNeuron, NeuronType,
    SensoryNeuron, AssociationNeuron, MemoryNeuron,
    InhibitoryNeuron, OutputNeuron,
)
from clm.neurons.hebbian import TriFactorLearner
HebbianLearner = TriFactorLearner  # backwards-compat alias
from clm.core.signal import CognitiveSignal, ActivationVector, SignalType

if TYPE_CHECKING:
    pass

logger = logging.getLogger(__name__)


class NeuronNetwork:
    """
    The living neuron network.

    Responsibilities:
    - Maintain the neuron population
    - Inject grounded signals as activation
    - Propagate activation across connections
    - Apply Hebbian learning after each cycle
    - Grow new neurons when novel concepts arrive
    - Prune dormant neurons to stay lean
    - Report active neurons to the cognitive loop
    """

    def __init__(
        self,
        initial_size:        int   = 500,
        max_size:            int   = 50_000,
        propagation_decay:   float = 0.85,    # Signal strength decay per hop
        growth_threshold:    float = 0.7,     # Activation needed to grow new neuron
        dormancy_threshold:  float = 0.001,   # Activation below this = dormant
        dormancy_age_s:      float = 3600.0,  # Prune neurons dormant this long
        inhibition_ratio:    float = 0.15,    # Fraction of inhibitory neurons
        output_neuron_count: int   = 20,
        hebbian: Optional[TriFactorLearner] = None,
    ):
        self.max_size           = max_size
        self.propagation_decay  = propagation_decay
        self.growth_threshold   = growth_threshold
        self.dormancy_threshold = dormancy_threshold
        self.dormancy_age_s     = dormancy_age_s
        self.inhibition_ratio   = inhibition_ratio
        self.output_neuron_count = output_neuron_count

        self.neurons: Dict[str, MicroNeuron] = {}
        self.label_index: Dict[str, str] = {}       # label → neuron_id
        self.type_index: Dict[NeuronType, Set[str]] = {t: set() for t in NeuronType}

        self.hebbian = hebbian or TriFactorLearner()

        self._cycle_count = 0
        self._last_fired: Set[str] = set()

        self._initialize(initial_size)

    # ── Initialization ────────────────────────────────────────────────────────

    def _initialize(self, size: int):
        """Seed the network with a baseline population."""
        n_output     = self.output_neuron_count
        n_inhibitory = max(1, int(size * self.inhibition_ratio))
        n_memory     = max(1, int(size * 0.15))
        n_assoc      = size - n_output - n_inhibitory - n_memory

        for _ in range(n_assoc):
            self._add_neuron(AssociationNeuron())

        for _ in range(n_memory):
            self._add_neuron(MemoryNeuron())

        for _ in range(n_inhibitory):
            self._add_neuron(InhibitoryNeuron())

        for i in range(n_output):
            self._add_neuron(OutputNeuron(label=f"output_{i}"))

        # Seed sparse random connections
        self._seed_connections(density=0.02)
        logger.info(f"Network initialized: {len(self.neurons)} neurons")

    def _seed_connections(self, density: float = 0.02):
        """Create sparse random initial connections."""
        import random
        ids = list(self.neurons.keys())
        n = len(ids)
        target_connections = int(n * n * density)

        for _ in range(target_connections):
            src = random.choice(ids)
            tgt = random.choice(ids)
            if src != tgt:
                weight = random.gauss(0.3, 0.15)
                weight = max(-0.5, min(0.8, weight))
                self.neurons[src].connect_to(tgt, weight)

    # ── Public interface ──────────────────────────────────────────────────────

    def inject(self, signal: CognitiveSignal) -> ActivationVector:
        """
        Inject a grounded signal into the network.
        Activates sensory/association neurons matching the signal's features.
        Returns the resulting activation vector.
        """
        activations: Dict[str, float] = {}

        # Find or create neurons for each feature in the signal
        for feature, strength in signal.features.items():
            neuron_id = self._get_or_create_neuron_for_feature(feature, signal)
            neuron = self.neurons.get(neuron_id)
            if neuron:
                neuron.receive("__input__", strength * signal.strength)
                activation = neuron.compute_activation()
                if activation > self.dormancy_threshold:
                    activations[neuron_id] = activation

        # Also activate by label match if signal has content
        if signal.content:
            words = signal.content.lower().split()[:20]
            for word in words:
                if word in self.label_index:
                    nid = self.label_index[word]
                    neuron = self.neurons.get(nid)
                    if neuron:
                        neuron.receive("__content__", signal.strength * 0.6)
                        activation = neuron.compute_activation()
                        if activation > self.dormancy_threshold:
                            activations[nid] = activation

        return ActivationVector(
            activations=activations,
            timestamp=time.time(),
            source_signal_id=signal.signal_id,
        )

    def propagate(self, activation: ActivationVector) -> ActivationVector:
        """
        Spread activation one step through the network.
        Active neurons fire and send signals to their targets.
        Applies Hebbian learning after firing.
        Returns updated activation vector.
        """
        self._cycle_count += 1
        new_activations: Dict[str, float] = {}
        fired_this_cycle: Set[str] = set()

        # Decay existing activations
        for nid, neuron in self.neurons.items():
            neuron.tick_decay()

        # Fire neurons that exceed threshold
        for nid, strength in activation.activations.items():
            neuron = self.neurons.get(nid)
            if neuron is None:
                continue

            neuron.receive("__propagation__", strength)
            neuron.compute_activation()

            if neuron.should_fire():
                output = neuron.fire()
                fired_this_cycle.add(nid)
                out_strength = output.get("strength", neuron.state.activation)

                # Propagate to connected neurons
                for target_id in neuron.get_output_targets():
                    target = self.neurons.get(target_id)
                    if target is None:
                        continue
                    conn = neuron.connections.get(target_id)
                    if conn is None:
                        continue

                    propagated = out_strength * abs(conn.weight) * self.propagation_decay
                    if conn.is_inhibitory():
                        propagated = -propagated

                    target.receive(nid, propagated)
                    new_act = target.compute_activation()

                    if abs(new_act) > self.dormancy_threshold:
                        existing = new_activations.get(target_id, 0.0)
                        new_activations[target_id] = max(existing, new_act)

            else:
                # Neuron didn't fire but still has some activation
                if neuron.state.activation > self.dormancy_threshold:
                    new_activations[nid] = neuron.state.activation * self.propagation_decay

        # Merge with previous activations (persistence)
        for nid, strength in activation.activations.items():
            if nid not in new_activations and strength > self.dormancy_threshold:
                new_activations[nid] = strength * self.propagation_decay * 0.5

        # Apply Hebbian learning
        self.hebbian.update(self.neurons, fired_this_cycle, activation)
        self._last_fired = fired_this_cycle

        # Grow network if novel strong activation with no matching neuron
        if len(self.neurons) < self.max_size:
            self._grow_if_needed(activation)

        return ActivationVector(
            activations=new_activations,
            timestamp=time.time(),
        )

    def get_active_neurons(self) -> List[MicroNeuron]:
        """Return neurons that fired in the last cycle."""
        return [
            self.neurons[nid]
            for nid in self._last_fired
            if nid in self.neurons
        ]

    def get_output_state(self) -> List[Dict[str, Any]]:
        """Return current state of all output neurons."""
        results = []
        for nid in self.type_index[NeuronType.OUTPUT]:
            neuron = self.neurons.get(nid)
            if neuron and isinstance(neuron, OutputNeuron):
                results.append({
                    "id":         neuron.id,
                    "label":      neuron.label,
                    "activation": neuron.state.activation,
                    "features":   neuron.features.copy(),
                    "history":    neuron.output_history[-3:],
                })
        return sorted(results, key=lambda x: x["activation"], reverse=True)

    def shed_load(self, activation: ActivationVector):
        """
        Reduce cognitive load by inhibiting the least-relevant active neurons.
        Called when metacognition detects overload.
        """
        sorted_active = sorted(
            activation.activations.items(), key=lambda x: x[1]
        )
        # Inhibit bottom 30%
        cutoff = max(1, len(sorted_active) // 3)
        for nid, _ in sorted_active[:cutoff]:
            neuron = self.neurons.get(nid)
            if neuron:
                neuron.state.activation *= 0.3

    def get_neuron_by_label(self, label: str) -> Optional[MicroNeuron]:
        nid = self.label_index.get(label.lower())
        return self.neurons.get(nid) if nid else None

    def get_stats(self) -> Dict[str, Any]:
        type_counts = {t.value: len(ids) for t, ids in self.type_index.items()}
        total_connections = sum(len(n.connections) for n in self.neurons.values())
        active_count = sum(
            1 for n in self.neurons.values()
            if n.state.activation > self.dormancy_threshold
        )
        return {
            "total_neurons":      len(self.neurons),
            "active_neurons":     active_count,
            "total_connections":  total_connections,
            "cycle_count":        self._cycle_count,
            "last_fired":         len(self._last_fired),
            "type_counts":        type_counts,
            "hebbian_updates":    self.hebbian.get_stats()["update_count"],
        }

    # ── Internal growth and maintenance ──────────────────────────────────────

    def _get_or_create_neuron_for_feature(
        self, feature: str, signal: CognitiveSignal
    ) -> str:
        """
        Find existing neuron for a feature, or create a new one.
        This is how the network grows — novel features spawn new neurons.
        """
        label = feature.lower()
        if label in self.label_index:
            return self.label_index[label]

        # Create new sensory/association neuron for this feature
        neuron = SensoryNeuron(label=label)
        neuron.update_feature(label, 1.0)
        self._add_neuron(neuron)

        # Connect to existing neurons with similar features
        self._connect_to_similar(neuron, top_k=5)

        return neuron.id

    def _grow_if_needed(self, activation: ActivationVector):
        """
        If activation is strong but sparse (novel concept),
        grow a new association neuron to represent it.
        """
        if not activation.activations:
            return

        max_act = max(activation.activations.values())
        if max_act < self.growth_threshold:
            return

        # Only grow occasionally
        if self._cycle_count % 10 != 0:
            return

        new_neuron = AssociationNeuron()
        self._add_neuron(new_neuron)

        # Connect to top active neurons
        top_active = sorted(
            activation.activations.items(), key=lambda x: x[1], reverse=True
        )[:5]
        for nid, strength in top_active:
            src = self.neurons.get(nid)
            if src:
                src.connect_to(new_neuron.id, weight=strength * 0.5)
                new_neuron.connect_to(nid, weight=strength * 0.3)

    def _connect_to_similar(self, neuron: MicroNeuron, top_k: int = 5):
        """Connect a new neuron to existing neurons with similar features."""
        if not neuron.features:
            return

        similarities: List[Tuple[str, float]] = []
        for nid, existing in self.neurons.items():
            if nid == neuron.id:
                continue
            sim = neuron.feature_similarity(existing)
            if sim > 0.1:
                similarities.append((nid, sim))

        similarities.sort(key=lambda x: x[1], reverse=True)
        for nid, sim in similarities[:top_k]:
            neuron.connect_to(nid, weight=sim * 0.6)
            self.neurons[nid].connect_to(neuron.id, weight=sim * 0.4)

    def _add_neuron(self, neuron: MicroNeuron):
        self.neurons[neuron.id] = neuron
        self.type_index[neuron.type].add(neuron.id)
        if neuron.label:
            self.label_index[neuron.label.lower()] = neuron.id

    def prune_dormant(self):
        """
        Remove neurons that have been inactive for too long.
        Keeps the network lean and prevents unbounded growth.
        Protects output neurons and memory neurons from pruning.
        """
        now = time.time()
        protected_types = {NeuronType.OUTPUT, NeuronType.MEMORY, NeuronType.META}
        to_remove = []

        for nid, neuron in self.neurons.items():
            if neuron.type in protected_types:
                continue
            if (
                neuron.state.activation < self.dormancy_threshold
                and now - neuron.last_active > self.dormancy_age_s
                and neuron.state.fire_count < 3
            ):
                to_remove.append(nid)

        for nid in to_remove:
            self._remove_neuron(nid)

        if to_remove:
            logger.debug(f"Pruned {len(to_remove)} dormant neurons")

    def _remove_neuron(self, neuron_id: str):
        neuron = self.neurons.pop(neuron_id, None)
        if neuron is None:
            return
        self.type_index[neuron.type].discard(neuron_id)
        if neuron.label and self.label_index.get(neuron.label.lower()) == neuron_id:
            del self.label_index[neuron.label.lower()]
        # Remove incoming connections from other neurons
        for other in self.neurons.values():
            other.connections.pop(neuron_id, None)
            other.incoming.pop(neuron_id, None)
