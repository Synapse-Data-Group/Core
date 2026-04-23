"""
CLM - Cognitive Language Model
reasoning/simulation.py

Internal simulation workspace — deliberative cognition before output.

The critique identified the core problem:
  "Simulation only works if the system has a predictive world model.
   Otherwise you're just sampling activation chains and scoring them
   heuristically. That's not simulation — that's guided association."

This module answers: WHAT IS BEING SIMULATED?

Answer: ConceptGraph traversal sequences, scored by the Viterbi algorithm.

The simulation domain is typed relation paths through the concept graph:
  State      = active concept node (canonical ID)
  Transition = edge weight × relation_type_prior × stability
  Emission   = alignment with current activation pattern
  Score      = log P(path) = Σ log(transition) + Σ log(emission)

This is a Hidden Markov Model where:
  - Hidden states = internal concept sequence (what the system "thinks about")
  - Observations  = current activation pattern (what just fired)
  - Transitions   = ConceptGraph edges (what the system believes connects to what)

The Viterbi algorithm finds the MOST PROBABLE concept sequence given
current activations. This is the simulation: not "what might happen"
but "what is the most coherent internal narrative given what I know."

Algorithm: Viterbi (max-product variant of belief propagation)
  O(T × N²) where T = simulation steps, N = active concepts
  Pure Python, no numpy, no dependencies.

Why Viterbi over raw activation sampling:
  - Finds globally optimal path, not locally greedy
  - Handles uncertainty via log-probabilities
  - Naturally prunes incoherent paths
  - Gives a traceable reasoning chain (explainable)
  - Complexity is tractable for small N (5-20 active concepts)

Secondary: N-best paths via beam search for diversity.
"""

from __future__ import annotations
import math
import time
from dataclasses import dataclass, field
from typing import Any, Dict, List, Optional, Set, Tuple, TYPE_CHECKING

if TYPE_CHECKING:
    from clm.reasoning.concept_graph import ConceptGraph, RelationType


# ── Relation type transition priors ──────────────────────────────────────────
# How likely is each relation type to be a valid cognitive transition?
# These are priors — updated by feedback over time.
# Higher = more likely to appear in a coherent reasoning chain.

_RELATION_TRANSITION_PRIOR: Dict[str, float] = {
    "causes":      0.90,   # Causal reasoning is highly coherent
    "is_a":        0.85,   # Taxonomic reasoning is stable
    "part_of":     0.80,   # Compositional reasoning
    "has":         0.75,   # Property attribution
    "used_for":    0.75,   # Functional reasoning
    "precedes":    0.70,   # Temporal reasoning
    "follows":     0.70,
    "located_in":  0.65,
    "created_by":  0.65,
    "similar_to":  0.60,   # Analogical — less certain
    "opposite_of": 0.55,   # Contrastive — useful but weaker
    "associated":  0.40,   # Weakest — pure co-occurrence
}


@dataclass
class SimulationPath:
    """
    A single simulated concept sequence — one Viterbi path.

    concept_sequence: ordered list of concept labels traversed
    relation_sequence: ordered list of relation types used
    log_score: log P(path) — higher is more probable/coherent
    coherence: normalized [0,1] coherence score
    novelty: fraction of path that goes beyond current activation
    causal_depth: number of CAUSES transitions (reasoning depth)
    """
    concept_sequence:  List[str]
    relation_sequence: List[str]
    log_score:         float
    coherence:         float
    novelty:           float
    causal_depth:      int
    simulation_time_ms: float = 0.0

    @property
    def composite_score(self) -> float:
        """
        Composite score for path selection:
          0.5 × coherence + 0.3 × novelty + 0.2 × causal_depth_bonus
        Coherence dominates — incoherent paths are never selected.
        """
        causal_bonus = min(1.0, self.causal_depth * 0.25)
        return 0.5 * self.coherence + 0.3 * self.novelty + 0.2 * causal_bonus

    def to_dict(self) -> Dict[str, Any]:
        return {
            "concepts":       self.concept_sequence,
            "relations":      self.relation_sequence,
            "log_score":      round(self.log_score, 4),
            "coherence":      round(self.coherence, 3),
            "novelty":        round(self.novelty, 3),
            "causal_depth":   self.causal_depth,
            "composite":      round(self.composite_score, 3),
        }


@dataclass
class SimulationResult:
    """
    Result of a simulation run — best path + alternatives.
    """
    best_path:         Optional[SimulationPath]
    all_paths:         List[SimulationPath]
    active_concepts:   List[str]
    simulation_steps:  int
    total_time_ms:     float
    graph_size:        int
    used_viterbi:      bool = True

    @property
    def best_concept_sequence(self) -> List[str]:
        if self.best_path:
            return self.best_path.concept_sequence
        return self.active_concepts[:5]

    @property
    def best_coherence(self) -> float:
        if self.best_path:
            return self.best_path.coherence
        return 0.0

    def to_dict(self) -> Dict[str, Any]:
        return {
            "best_path":       self.best_path.to_dict() if self.best_path else None,
            "n_paths":         len(self.all_paths),
            "active_concepts": self.active_concepts[:8],
            "steps":           self.simulation_steps,
            "time_ms":         round(self.total_time_ms, 2),
            "graph_size":      self.graph_size,
            "used_viterbi":    self.used_viterbi,
        }


# Keep backward-compatible alias
SimulationTrajectory = SimulationPath


class SimulationWorkspace:
    """
    Internal simulation workspace using Viterbi over the ConceptGraph.

    Before generating output, the cognitive loop calls simulate() to find
    the most probable concept sequence given current activations and the
    system's belief graph. This sequence guides output generation.

    The system does not generate language during simulation — it reasons
    in concept space, then hands the best path to the renderer.

    Algorithm:
      1. Extract active concept IDs from activation vector
      2. Build local HMM: states = concepts, transitions = graph edges
      3. Run Viterbi to find most probable concept sequence
      4. Run beam search for N-best alternatives (diversity)
      5. Score paths on coherence + novelty + causal depth
      6. Return best path + alternatives to cognitive loop

    Complexity: O(T × N²) per path, T=steps, N=active concepts (≤20)
    Typical runtime: <5ms for N=10, T=5
    """

    def __init__(
        self,
        n_trajectories:   int   = 5,
        simulation_steps: int   = 5,
        beam_width:       int   = 3,
        min_edge_weight:  float = 0.2,
    ):
        self.n_trajectories   = n_trajectories
        self.simulation_steps = simulation_steps
        self.beam_width       = beam_width
        self.min_edge_weight  = min_edge_weight

        self._total_simulations = 0
        self._total_time_ms     = 0.0
        self._viterbi_runs      = 0
        self._fallback_runs     = 0

    def simulate(
        self,
        active_concept_ids: List[str],
        concept_graph:      "ConceptGraph",
        activation_weights: Optional[Dict[str, float]] = None,
    ) -> SimulationResult:
        """
        Run Viterbi simulation over the concept graph.

        active_concept_ids: concept IDs currently active (from activation vector)
        concept_graph: the system's belief graph
        activation_weights: concept_id → activation strength (optional)

        Returns SimulationResult with best path and alternatives.
        """
        t0 = time.perf_counter()
        self._total_simulations += 1

        # Resolve canonical IDs and filter to known concepts
        canonical_ids = []
        seen: Set[str] = set()
        for cid in active_concept_ids:
            can = concept_graph._uf_find(cid)
            if can not in seen and can in concept_graph._concepts:
                canonical_ids.append(can)
                seen.add(can)

        active_labels = [
            concept_graph._concepts[cid].label
            for cid in canonical_ids
            if cid in concept_graph._concepts
        ]

        # Need at least 2 concepts to simulate
        if len(canonical_ids) < 2 or concept_graph.confirmed_edge_count() < 1:
            elapsed = (time.perf_counter() - t0) * 1000
            self._total_time_ms += elapsed
            self._fallback_runs += 1
            return SimulationResult(
                best_path=None,
                all_paths=[],
                active_concepts=active_labels,
                simulation_steps=0,
                total_time_ms=elapsed,
                graph_size=concept_graph.concept_count(),
                used_viterbi=False,
            )

        # Build emission probabilities: P(concept | active)
        # Higher activation weight → higher emission probability
        weights = activation_weights or {}
        total_w = sum(weights.get(cid, 0.5) for cid in canonical_ids) or 1.0
        emission: Dict[str, float] = {
            cid: weights.get(cid, 0.5) / total_w
            for cid in canonical_ids
        }

        # Run Viterbi from each starting concept (beam of starts)
        all_paths: List[SimulationPath] = []
        start_concepts = canonical_ids[:self.beam_width]

        for start_id in start_concepts:
            path = self._viterbi(
                start_id=start_id,
                canonical_ids=canonical_ids,
                concept_graph=concept_graph,
                emission=emission,
                steps=self.simulation_steps,
            )
            if path:
                all_paths.append(path)

        # Also run beam search for diversity
        beam_paths = self._beam_search(
            start_ids=canonical_ids[:2],
            concept_graph=concept_graph,
            emission=emission,
            steps=self.simulation_steps,
            beam_width=self.beam_width,
        )
        all_paths.extend(beam_paths)

        # Deduplicate and score
        all_paths = self._deduplicate(all_paths)
        all_paths.sort(key=lambda p: p.composite_score, reverse=True)

        best = all_paths[0] if all_paths else None
        elapsed = (time.perf_counter() - t0) * 1000
        self._total_time_ms += elapsed
        self._viterbi_runs  += 1

        return SimulationResult(
            best_path=best,
            all_paths=all_paths[:self.n_trajectories],
            active_concepts=active_labels,
            simulation_steps=self.simulation_steps,
            total_time_ms=elapsed,
            graph_size=concept_graph.concept_count(),
            used_viterbi=True,
        )

    # ── Viterbi algorithm ─────────────────────────────────────────────────────

    def _viterbi(
        self,
        start_id:      str,
        canonical_ids: List[str],
        concept_graph: "ConceptGraph",
        emission:      Dict[str, float],
        steps:         int,
    ) -> Optional[SimulationPath]:
        """
        Viterbi algorithm: find most probable concept sequence.

        State space: canonical_ids (active concepts)
        Transitions: ConceptGraph confirmed edges
        Emissions:   activation weights

        DP table: viterbi[t][state] = (log_prob, backpointer)
        Final: traceback from highest-scoring terminal state.

        Log-space arithmetic to avoid underflow.
        """
        n = len(canonical_ids)
        if n == 0:
            return None

        idx = {cid: i for i, cid in enumerate(canonical_ids)}

        # Precompute transition log-probs from graph
        # trans[i][j] = log P(j | i) via graph edge, or -inf if no edge
        LOG_ZERO = float("-inf")
        trans = [[LOG_ZERO] * n for _ in range(n)]

        for i, src_id in enumerate(canonical_ids):
            out_edges = [
                e for e in concept_graph._edges.get(src_id, [])
                if not e.provisional
                and e.is_alive(self.min_edge_weight)
                and concept_graph._uf_find(e.target_id) in idx
            ]
            if not out_edges:
                continue
            for edge in out_edges:
                j = idx.get(concept_graph._uf_find(edge.target_id))
                if j is None:
                    continue
                rel_prior = _RELATION_TRANSITION_PRIOR.get(edge.relation.value, 0.4)
                log_p = math.log(max(edge.weight * rel_prior, 1e-10))
                # Take max if multiple edges between same pair
                if log_p > trans[i][j]:
                    trans[i][j] = log_p

        # Emission log-probs
        log_emit = {
            cid: math.log(max(emission.get(cid, 1.0 / n), 1e-10))
            for cid in canonical_ids
        }

        # Viterbi DP
        start_i = idx.get(start_id, 0)
        # viterbi[state] = (log_prob, path_list)
        viterbi: List[Tuple[float, List[str], List[str]]] = [
            (LOG_ZERO, [], []) for _ in range(n)
        ]
        viterbi[start_i] = (
            log_emit.get(start_id, 0.0),
            [concept_graph._concepts[start_id].label],
            [],
        )

        for _step in range(steps - 1):
            new_viterbi: List[Tuple[float, List[str], List[str]]] = [
                (LOG_ZERO, [], []) for _ in range(n)
            ]
            for j in range(n):
                best_log = LOG_ZERO
                best_path: List[str] = []
                best_rels: List[str] = []

                for i in range(n):
                    if viterbi[i][0] == LOG_ZERO:
                        continue
                    if trans[i][j] == LOG_ZERO:
                        continue
                    log_p = viterbi[i][0] + trans[i][j] + log_emit.get(canonical_ids[j], 0.0)
                    if log_p > best_log:
                        best_log  = log_p
                        # Find the relation used for this transition
                        rel = self._find_relation(
                            canonical_ids[i], canonical_ids[j], concept_graph
                        )
                        best_path = viterbi[i][1] + [concept_graph._concepts[canonical_ids[j]].label]
                        best_rels = viterbi[i][2] + [rel]

                new_viterbi[j] = (best_log, best_path, best_rels)
            viterbi = new_viterbi

        # Find best terminal state
        best_terminal = max(viterbi, key=lambda x: x[0])
        if best_terminal[0] == LOG_ZERO or len(best_terminal[1]) < 2:
            return None

        log_score, concept_seq, rel_seq = best_terminal
        return self._score_path(concept_seq, rel_seq, log_score, canonical_ids, concept_graph)

    # ── Beam search (diversity) ───────────────────────────────────────────────

    def _beam_search(
        self,
        start_ids:     List[str],
        concept_graph: "ConceptGraph",
        emission:      Dict[str, float],
        steps:         int,
        beam_width:    int,
    ) -> List[SimulationPath]:
        """
        Beam search for diverse N-best paths.
        Each beam state: (log_score, concept_path, rel_path, current_id, visited)
        """
        # Initialize beam from start concepts
        beam: List[Tuple[float, List[str], List[str], str, Set[str]]] = []
        for sid in start_ids:
            node = concept_graph._concepts.get(sid)
            if node is None:
                continue
            log_e = math.log(max(emission.get(sid, 0.1), 1e-10))
            beam.append((log_e, [node.label], [], sid, {sid}))

        for _step in range(steps - 1):
            candidates: List[Tuple[float, List[str], List[str], str, Set[str]]] = []
            for log_s, c_path, r_path, cur_id, visited in beam:
                out_edges = [
                    e for e in concept_graph._edges.get(cur_id, [])
                    if not e.provisional
                    and e.is_alive(self.min_edge_weight)
                ]
                if not out_edges:
                    candidates.append((log_s, c_path, r_path, cur_id, visited))
                    continue
                for edge in out_edges:
                    tgt = concept_graph._uf_find(edge.target_id)
                    if tgt in visited:
                        continue
                    tgt_node = concept_graph._concepts.get(tgt)
                    if tgt_node is None:
                        continue
                    rel_prior = _RELATION_TRANSITION_PRIOR.get(edge.relation.value, 0.4)
                    log_t = math.log(max(edge.weight * rel_prior, 1e-10))
                    log_e = math.log(max(emission.get(tgt, 0.1), 1e-10))
                    new_score = log_s + log_t + log_e
                    candidates.append((
                        new_score,
                        c_path + [tgt_node.label],
                        r_path + [edge.relation.value],
                        tgt,
                        visited | {tgt},
                    ))

            if not candidates:
                break
            candidates.sort(key=lambda x: x[0], reverse=True)
            beam = candidates[:beam_width]

        paths = []
        all_ids = list(concept_graph._concepts.keys())
        for log_s, c_path, r_path, _, _ in beam:
            if len(c_path) >= 2:
                paths.append(self._score_path(c_path, r_path, log_s, all_ids, concept_graph))
        return [p for p in paths if p is not None]

    # ── Path scoring ──────────────────────────────────────────────────────────

    def _score_path(
        self,
        concept_seq:   List[str],
        relation_seq:  List[str],
        log_score:     float,
        all_concept_ids: List[str],
        concept_graph: "ConceptGraph",
    ) -> Optional[SimulationPath]:
        if len(concept_seq) < 2:
            return None

        # Coherence: normalize log_score by path length
        # Longer paths get penalized to avoid length bias
        coherence = 1.0 / (1.0 + math.exp(-log_score / max(len(concept_seq), 1)))

        # Novelty: fraction of concepts not in the top active set
        active_labels = {
            concept_graph._concepts[cid].label
            for cid in all_concept_ids
            if cid in concept_graph._concepts
        }
        novel = sum(1 for c in concept_seq if c not in active_labels)
        novelty = novel / max(len(concept_seq), 1)

        # Causal depth: number of CAUSES transitions
        causal_depth = sum(1 for r in relation_seq if r == "causes")

        return SimulationPath(
            concept_sequence=concept_seq,
            relation_sequence=relation_seq,
            log_score=log_score,
            coherence=coherence,
            novelty=novelty,
            causal_depth=causal_depth,
        )

    # ── Helpers ───────────────────────────────────────────────────────────────

    def _find_relation(
        self,
        src_id:        str,
        tgt_id:        str,
        concept_graph: "ConceptGraph",
    ) -> str:
        """Find the highest-weight confirmed relation between two concepts."""
        best_rel   = "associated"
        best_weight = 0.0
        for edge in concept_graph._edges.get(src_id, []):
            if concept_graph._uf_find(edge.target_id) == tgt_id and not edge.provisional:
                if edge.weight > best_weight:
                    best_weight = edge.weight
                    best_rel    = edge.relation.value
        return best_rel

    def _deduplicate(self, paths: List[SimulationPath]) -> List[SimulationPath]:
        """Remove paths with identical concept sequences."""
        seen: Set[str] = set()
        unique = []
        for path in paths:
            key = "→".join(path.concept_sequence)
            if key not in seen:
                seen.add(key)
                unique.append(path)
        return unique

    def get_stats(self) -> Dict[str, Any]:
        avg_ms = (
            self._total_time_ms / self._total_simulations
            if self._total_simulations > 0 else 0.0
        )
        return {
            "total_simulations": self._total_simulations,
            "viterbi_runs":      self._viterbi_runs,
            "fallback_runs":     self._fallback_runs,
            "avg_time_ms":       round(avg_ms, 2),
            "algorithm":         "viterbi+beam_search",
        }
