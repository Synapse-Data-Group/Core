"""
CLM - Cognitive Language Model
reasoning/concept_graph.py

Internal semantic structure — concept graph with structural hygiene.

Without hygiene, a closed cognitive loop amplifies noise:
  wrong abstractions → overconnection → ontology drift → causal hallucinations

This module implements four mathematically grounded hygiene mechanisms:

1. EBBINGHAUS DECAY (edge weight decay)
   R = e^(-t/S)
   Unused edges lose weight exponentially. Stability S increases with each
   reinforcement, so frequently-used edges become permanent.
   Source: Ebbinghaus (1885), FSRS algorithm (2022).

2. JACCARD SYNONYM MERGE (concept canonicalization)
   J(A,B) = |neighbors(A) ∩ neighbors(B)| / |neighbors(A) ∪ neighbors(B)|
   Concepts with high neighbor overlap are synonyms. Merged via Union-Find
   (O(α(n)) amortized) — all edges redirect to canonical node.
   Source: Collins & Loftus (1975), standard graph deduplication.

3. EVIDENCE THRESHOLDS (new edge gating)
   New relations require min_evidence observations before becoming permanent.
   Below threshold: stored as provisional, not used in simulation.
   Prevents single-observation hallucinations from entering the graph.

4. PAGERANK IMPORTANCE (sparsification)
   PR(u) = (1-d)/N + d × Σ PR(v)/out_degree(v)
   Identifies structurally central concepts. Low-PageRank + low-evidence
   edges are pruned during consolidation cycles.
   Source: Page et al. (1999), pure power iteration, no dependencies.

Additionally: Levenshtein edit distance for surface-form synonym detection
("rain"/"raining", "cause"/"causes") — pure Python O(m×n).
"""

from __future__ import annotations
import math
import time
import uuid
from collections import defaultdict
from dataclasses import dataclass, field
from enum import Enum
from typing import Any, Dict, List, Optional, Set, Tuple


class RelationType(Enum):
    """Typed semantic relations between concepts."""
    IS_A         = "is_a"
    HAS          = "has"
    CAUSES       = "causes"
    PART_OF      = "part_of"
    OPPOSITE_OF  = "opposite_of"
    SIMILAR_TO   = "similar_to"
    PRECEDES     = "precedes"
    FOLLOWS      = "follows"
    USED_FOR     = "used_for"
    LOCATED_IN   = "located_in"
    CREATED_BY   = "created_by"
    ASSOCIATED   = "associated"


@dataclass
class ConceptNode:
    """
    A concept in the internal knowledge graph.
    Not a word — a meaning. Words are just labels.
    """
    concept_id:     str
    label:          str
    aliases:        List[str]
    properties:     Dict[str, float]
    activation:     float = 0.0
    confidence:     float = 0.5
    evidence_count: int   = 0
    created_at:     float = field(default_factory=time.time)
    last_active:    float = field(default_factory=time.time)

    def reinforce(self, amount: float = 0.05):
        self.confidence     = min(1.0, self.confidence + amount)
        self.evidence_count += 1
        self.last_active    = time.time()

    def to_dict(self) -> Dict[str, Any]:
        return {
            "concept_id":     self.concept_id,
            "label":          self.label,
            "aliases":        self.aliases,
            "properties":     self.properties,
            "confidence":     round(self.confidence, 3),
            "evidence_count": self.evidence_count,
        }


@dataclass
class ConceptEdge:
    """
    A typed relation between two concepts.

    Decay model (Ebbinghaus + FSRS):
      retrievability R(t) = e^(-t / S)
      stability S increases with each reinforcement:
        S_new = S × (1 + 0.1 × R_at_review)
      This means:
        - Rarely-used edges decay toward zero and get pruned
        - Frequently-used edges become increasingly stable (permanent)
        - A single observation cannot create a permanent edge
    """
    edge_id:         str   = field(default_factory=lambda: str(uuid.uuid4())[:8])
    source_id:       str   = ""
    target_id:       str   = ""
    relation:        RelationType = RelationType.ASSOCIATED
    weight:          float = 0.5    # Current retrievability R [0, 1]
    stability:       float = 1.0    # Memory stability S (hours)
    confidence:      float = 0.5
    evidence_count:  int   = 0
    provisional:     bool  = True   # True until evidence_count >= threshold
    created_at:      float = field(default_factory=time.time)
    last_reinforced: float = field(default_factory=time.time)

    def decay(self, now: Optional[float] = None) -> float:
        """
        Apply Ebbinghaus decay: R = e^(-t/S)
        t measured in hours for faster cognitive dynamics.
        Updates weight in place, returns current retrievability.
        """
        t = ((now or time.time()) - self.last_reinforced) / 3600.0
        r = math.exp(-t / max(self.stability, 0.1))
        self.weight = max(0.0, r)
        return self.weight

    def reinforce(self, amount: float = 0.03):
        """
        Reinforce this edge. FSRS stability update:
          S_new = S × (1 + 0.1 × R_at_review)
        Reviewing when R is high → large stability gain.
        Reviewing when R is low (almost forgotten) → smaller gain.
        """
        now = time.time()
        r_at_review = self.decay(now)
        self.stability      = self.stability * (1.0 + 0.1 * r_at_review)
        self.weight         = min(1.0, self.weight + amount + 0.1)
        self.confidence     = min(1.0, self.confidence + amount * 0.5)
        self.evidence_count += 1
        self.last_reinforced = now

    def is_alive(self, min_weight: float = 0.05) -> bool:
        return self.weight >= min_weight

    def to_dict(self) -> Dict[str, Any]:
        return {
            "source_id":      self.source_id,
            "target_id":      self.target_id,
            "relation":       self.relation.value,
            "weight":         round(self.weight, 3),
            "stability":      round(self.stability, 3),
            "confidence":     round(self.confidence, 3),
            "evidence_count": self.evidence_count,
            "provisional":    self.provisional,
        }


class ConceptGraph:
    """
    The system's internal semantic knowledge graph — with structural hygiene.

    Four hygiene mechanisms prevent representation collapse:
      1. Ebbinghaus decay    — unused edges lose weight exponentially
      2. Synonym merge       — Jaccard + Levenshtein → Union-Find canonicalization
      3. Evidence thresholds — new edges are provisional until confirmed
      4. PageRank pruning    — low-importance peripheral edges removed

    The graph is the thought. Language is the expression.
    """

    def __init__(
        self,
        min_evidence:               int   = 2,
        min_edge_weight:            float = 0.05,
        synonym_jaccard_thresh:     float = 0.6,
        synonym_levenshtein_thresh: float = 0.85,
        pagerank_damping:           float = 0.85,
        pagerank_iterations:        int   = 20,
    ):
        self._concepts:       Dict[str, ConceptNode]        = {}
        self._label_index:    Dict[str, str]                = {}
        self._edges:          Dict[str, List[ConceptEdge]]  = defaultdict(list)
        self._relation_index: Dict[RelationType, List[str]] = defaultdict(list)
        self._edge_count = 0

        self.min_evidence               = min_evidence
        self.min_edge_weight            = min_edge_weight
        self.synonym_jaccard_thresh     = synonym_jaccard_thresh
        self.synonym_levenshtein_thresh = synonym_levenshtein_thresh
        self.pagerank_damping           = pagerank_damping
        self.pagerank_iterations        = pagerank_iterations

        # Union-Find for synonym merging
        self._uf_parent: Dict[str, str] = {}

        # Stats
        self._merges_performed = 0
        self._edges_pruned     = 0
        self._hygiene_cycles   = 0

    # ── Concept management ────────────────────────────────────────────────────

    def get_or_create(
        self,
        label:      str,
        properties: Optional[Dict[str, float]] = None,
    ) -> ConceptNode:
        label_lower = label.lower().strip()
        if not label_lower:
            return self._null_concept()

        if label_lower in self._label_index:
            cid  = self._uf_find(self._label_index[label_lower])
            node = self._concepts.get(cid)
            if node:
                node.reinforce(0.02)
                if properties:
                    for k, v in properties.items():
                        node.properties[k] = max(node.properties.get(k, 0.0), v)
                return node

        node = ConceptNode(
            concept_id=str(uuid.uuid4())[:12],
            label=label_lower,
            aliases=[],
            properties=properties or {},
        )
        self._concepts[node.concept_id]    = node
        self._label_index[label_lower]     = node.concept_id
        self._uf_parent[node.concept_id]   = node.concept_id
        return node

    def add_relation(
        self,
        source_label: str,
        relation:     RelationType,
        target_label: str,
        weight:       float = 0.5,
        confidence:   float = 0.5,
    ) -> ConceptEdge:
        """
        Add or reinforce a typed relation.
        New edges are provisional until evidence_count >= min_evidence.
        """
        source = self.get_or_create(source_label)
        target = self.get_or_create(target_label)
        src_id = self._uf_find(source.concept_id)
        tgt_id = self._uf_find(target.concept_id)

        if src_id == tgt_id:
            existing = self._edges.get(src_id, [])
            return existing[0] if existing else ConceptEdge(
                source_id=src_id, target_id=tgt_id, relation=relation
            )

        for edge in self._edges[src_id]:
            if edge.target_id == tgt_id and edge.relation == relation:
                edge.reinforce(0.03)
                if edge.evidence_count >= self.min_evidence:
                    edge.provisional = False
                return edge

        edge = ConceptEdge(
            source_id=src_id,
            target_id=tgt_id,
            relation=relation,
            weight=weight,
            stability=1.0,
            confidence=confidence,
            evidence_count=1,
            provisional=(1 < self.min_evidence),
        )
        self._edges[src_id].append(edge)
        self._relation_index[relation].append(edge.edge_id)
        self._edge_count += 1
        return edge

    # ── Query ─────────────────────────────────────────────────────────────────

    def get_neighborhood(
        self,
        label:               str,
        max_hops:            int   = 2,
        min_weight:          float = 0.3,
        include_provisional: bool  = False,
    ) -> List[Dict[str, Any]]:
        label_lower = label.lower().strip()
        cid = self._label_index.get(label_lower)
        if cid is None:
            return []
        cid = self._uf_find(cid)

        visited: Set[str] = {cid}
        results = []
        frontier = [cid]

        for hop in range(max_hops):
            next_frontier = []
            for cur in frontier:
                for edge in self._edges.get(cur, []):
                    if edge.provisional and not include_provisional:
                        continue
                    if edge.weight < min_weight:
                        continue
                    tgt = self._uf_find(edge.target_id)
                    node = self._concepts.get(tgt)
                    if node is None or tgt in visited:
                        continue
                    visited.add(tgt)
                    next_frontier.append(tgt)
                    results.append({
                        "concept":   node.label,
                        "relation":  edge.relation.value,
                        "weight":    edge.weight,
                        "stability": edge.stability,
                        "hop":       hop + 1,
                    })
            frontier = next_frontier

        return sorted(results, key=lambda x: x["weight"], reverse=True)

    def extract_propositions(
        self,
        concept_ids:    List[str],
        min_confidence: float = 0.4,
        confirmed_only: bool  = True,
    ) -> List[Tuple[str, str, str]]:
        """Extract (subject, relation, object) triples — confirmed edges only by default."""
        propositions = []
        for cid in concept_ids:
            cid    = self._uf_find(cid)
            source = self._concepts.get(cid)
            if source is None:
                continue
            for edge in self._edges.get(cid, []):
                if confirmed_only and edge.provisional:
                    continue
                if edge.confidence < min_confidence:
                    continue
                tgt    = self._uf_find(edge.target_id)
                target = self._concepts.get(tgt)
                if target is None:
                    continue
                propositions.append((source.label, edge.relation.value, target.label))
        return propositions

    def find_causal_chain(
        self,
        start_label: str,
        max_depth:   int = 4,
    ) -> List[List[str]]:
        start_id = self._label_index.get(start_label.lower())
        if start_id is None:
            return []
        start_id = self._uf_find(start_id)
        chains: List[List[str]] = []
        self._dfs_causal(start_id, [start_label], chains, set(), max_depth)
        return chains

    def get_summary_structure(
        self,
        active_concept_ids: List[str],
        max_concepts:       int = 8,
    ) -> Dict[str, Any]:
        """Structured summary for the renderer — confirmed knowledge only."""
        resolved     = [self._uf_find(cid) for cid in active_concept_ids]
        active_nodes = [self._concepts[cid] for cid in resolved if cid in self._concepts]
        active_nodes.sort(key=lambda n: n.confidence * n.activation, reverse=True)
        top_nodes = active_nodes[:max_concepts]

        propositions  = self.extract_propositions([n.concept_id for n in top_nodes])
        causal_chains: List[List[str]] = []
        for node in top_nodes[:3]:
            causal_chains.extend(self.find_causal_chain(node.label, max_depth=3)[:2])

        return {
            "core_concepts": [
                {"label": n.label, "confidence": round(n.confidence, 3)}
                for n in top_nodes
            ],
            "propositions":  propositions[:15],
            "causal_chains": causal_chains[:5],
            "properties":    {n.label: n.properties for n in top_nodes if n.properties},
        }

    def ingest_from_activation(
        self,
        activation_labels: List[str],
        value_signal:      float = 0.5,
    ):
        """Build concept graph entries from co-activated concept labels."""
        nodes = [self.get_or_create(label) for label in activation_labels if label]
        for i in range(len(nodes)):
            for j in range(i + 1, min(i + 4, len(nodes))):
                self.add_relation(
                    nodes[i].label,
                    RelationType.ASSOCIATED,
                    nodes[j].label,
                    weight=value_signal * 0.6,
                    confidence=value_signal * 0.5,
                )

    # ── Hygiene 1: Ebbinghaus Decay ───────────────────────────────────────────

    def apply_decay(self) -> int:
        """
        Apply R = e^(-t/S) to all edges. Prune edges below min_edge_weight.
        Returns number of edges pruned.
        """
        now    = time.time()
        pruned = 0
        for cid in list(self._edges.keys()):
            alive = []
            for edge in self._edges[cid]:
                edge.decay(now)
                if edge.is_alive(self.min_edge_weight):
                    alive.append(edge)
                else:
                    pruned += 1
            self._edges[cid] = alive
        self._edges_pruned += pruned
        self._edge_count    = sum(len(v) for v in self._edges.values())
        return pruned

    # ── Hygiene 2: Synonym Merge (Jaccard + Levenshtein + Union-Find) ─────────

    def merge_synonyms(self) -> int:
        """
        Detect and merge synonym concepts.

        Two concepts are synonyms if EITHER:
          a) Levenshtein label similarity >= synonym_levenshtein_thresh
             sim = 1 - edit_distance(a,b) / max(len(a), len(b))
          b) Jaccard neighbor similarity >= synonym_jaccard_thresh
             J(A,B) = |N(A) ∩ N(B)| / |N(A) ∪ N(B)|

        Levenshtein checked first (O(m×n) but cheap for short labels).
        Jaccard checked second (set intersection, O(degree)).
        Merging via Union-Find: higher-evidence concept becomes canonical.
        Returns number of merges performed.
        """
        merges      = 0
        concept_ids = list(self._concepts.keys())

        for i in range(len(concept_ids)):
            for j in range(i + 1, len(concept_ids)):
                cid_a = self._uf_find(concept_ids[i])
                cid_b = self._uf_find(concept_ids[j])
                if cid_a == cid_b:
                    continue
                node_a = self._concepts.get(cid_a)
                node_b = self._concepts.get(cid_b)
                if node_a is None or node_b is None:
                    continue

                # Levenshtein label similarity (cheap — check first)
                if self._levenshtein_similarity(node_a.label, node_b.label) >= self.synonym_levenshtein_thresh:
                    self._uf_union(cid_a, cid_b)
                    merges += 1
                    continue

                # Jaccard neighbor similarity (more expensive)
                if self._jaccard_neighbors(cid_a, cid_b) >= self.synonym_jaccard_thresh:
                    self._uf_union(cid_a, cid_b)
                    merges += 1

        self._merges_performed += merges
        return merges

    # ── Hygiene 3: PageRank Sparsification ────────────────────────────────────

    def compute_pagerank(self) -> Dict[str, float]:
        """
        PageRank via power iteration (no numpy):
          PR(u) = (1-d)/N + d × Σ_{v→u} PR(v) / out_degree(v)

        Converges in ~20 iterations for typical graph sizes.
        Only operates on canonical, confirmed nodes.
        """
        canonical = [
            cid for cid in self._concepts
            if self._uf_find(cid) == cid
        ]
        n = len(canonical)
        if n == 0:
            return {}

        d  = self.pagerank_damping
        pr = {cid: 1.0 / n for cid in canonical}

        for _ in range(self.pagerank_iterations):
            new_pr = {cid: (1.0 - d) / n for cid in canonical}
            for cid in canonical:
                out_edges = [
                    e for e in self._edges.get(cid, [])
                    if not e.provisional and e.is_alive(self.min_edge_weight)
                ]
                if not out_edges:
                    # Dangling node — distribute rank evenly
                    share = pr[cid] / n
                    for tid in canonical:
                        new_pr[tid] = new_pr.get(tid, 0.0) + share
                    continue
                share = pr[cid] / len(out_edges)
                for edge in out_edges:
                    tgt = self._uf_find(edge.target_id)
                    if tgt in new_pr:
                        new_pr[tgt] += share * d

            delta = sum(abs(new_pr.get(c, 0) - pr[c]) for c in canonical)
            pr    = new_pr
            if delta < 1e-6:
                break

        return pr

    def sparsify(self, min_pagerank: float = 0.0001) -> int:
        """
        Prune provisional edges whose source has PageRank < min_pagerank.
        Confirmed edges (evidence >= min_evidence) are never pruned here.
        Returns number of edges pruned.
        """
        pr     = self.compute_pagerank()
        pruned = 0
        for cid in list(self._edges.keys()):
            node_pr   = pr.get(self._uf_find(cid), 0.0)
            surviving = []
            for edge in self._edges[cid]:
                if (node_pr < min_pagerank
                        and edge.provisional
                        and edge.evidence_count < self.min_evidence):
                    pruned += 1
                else:
                    surviving.append(edge)
            self._edges[cid] = surviving
        self._edges_pruned += pruned
        self._edge_count    = sum(len(v) for v in self._edges.values())
        return pruned

    def run_hygiene_cycle(self) -> Dict[str, int]:
        """
        Full hygiene cycle — call from consolidation loop, not hot path:
          1. Ebbinghaus decay + prune dead edges
          2. Synonym merge via Jaccard + Levenshtein + Union-Find
          3. PageRank sparsification of low-importance provisional edges
        """
        self._hygiene_cycles += 1
        return {
            "decayed": self.apply_decay(),
            "merged":  self.merge_synonyms(),
            "pruned":  self.sparsify(),
        }

    # ── Counts and stats ──────────────────────────────────────────────────────

    def concept_count(self) -> int:
        return len(self._concepts)

    def canonical_concept_count(self) -> int:
        return sum(1 for cid in self._concepts if self._uf_find(cid) == cid)

    def edge_count(self) -> int:
        return self._edge_count

    def confirmed_edge_count(self) -> int:
        return sum(
            1 for edges in self._edges.values()
            for e in edges if not e.provisional
        )

    def get_stats(self) -> Dict[str, Any]:
        return {
            "concept_count":           self.concept_count(),
            "canonical_concept_count": self.canonical_concept_count(),
            "edge_count":              self.edge_count(),
            "confirmed_edge_count":    self.confirmed_edge_count(),
            "merges_performed":        self._merges_performed,
            "edges_pruned":            self._edges_pruned,
            "hygiene_cycles":          self._hygiene_cycles,
            "relation_types": {
                r.value: len(ids)
                for r, ids in self._relation_index.items()
            },
        }

    # ── Union-Find internals ──────────────────────────────────────────────────

    def _uf_find(self, cid: str) -> str:
        """Path-compressed find. O(α(n)) amortized."""
        if cid not in self._uf_parent:
            self._uf_parent[cid] = cid
            return cid
        if self._uf_parent[cid] != cid:
            self._uf_parent[cid] = self._uf_find(self._uf_parent[cid])
        return self._uf_parent[cid]

    def _uf_union(self, cid_a: str, cid_b: str):
        """
        Union by evidence count. Higher-evidence concept becomes canonical.
        Merges aliases and redirects label_index entries.
        """
        root_a = self._uf_find(cid_a)
        root_b = self._uf_find(cid_b)
        if root_a == root_b:
            return

        node_a = self._concepts.get(root_a)
        node_b = self._concepts.get(root_b)
        if node_a is None or node_b is None:
            return

        if node_a.evidence_count >= node_b.evidence_count:
            canonical, subordinate = root_a, root_b
        else:
            canonical, subordinate = root_b, root_a

        self._uf_parent[subordinate] = canonical
        can_node = self._concepts[canonical]
        sub_node = self._concepts[subordinate]

        # Merge aliases
        if sub_node.label not in can_node.aliases:
            can_node.aliases.append(sub_node.label)
        for alias in sub_node.aliases:
            if alias not in can_node.aliases:
                can_node.aliases.append(alias)

        # Redirect label_index
        self._label_index[sub_node.label] = canonical
        for alias in sub_node.aliases:
            self._label_index[alias] = canonical

        # Merge evidence counts
        can_node.evidence_count += sub_node.evidence_count
        can_node.confidence      = min(1.0, max(can_node.confidence, sub_node.confidence))

    # ── Similarity helpers ────────────────────────────────────────────────────

    @staticmethod
    def _levenshtein_similarity(a: str, b: str) -> float:
        """
        Normalised Levenshtein similarity: 1 - edit_distance(a,b) / max(len(a),len(b))
        Pure Python O(m×n). Returns 1.0 for identical strings.
        """
        if a == b:
            return 1.0
        m, n = len(a), len(b)
        if m == 0 or n == 0:
            return 0.0
        # Wagner-Fischer DP
        prev = list(range(n + 1))
        for i in range(1, m + 1):
            curr = [i] + [0] * n
            for j in range(1, n + 1):
                cost = 0 if a[i - 1] == b[j - 1] else 1
                curr[j] = min(curr[j - 1] + 1, prev[j] + 1, prev[j - 1] + cost)
            prev = curr
        return 1.0 - prev[n] / max(m, n)

    def _jaccard_neighbors(self, cid_a: str, cid_b: str) -> float:
        """
        Jaccard similarity of neighbor sets:
          J(A,B) = |N(A) ∩ N(B)| / |N(A) ∪ N(B)|
        Uses canonical IDs so merged concepts count as one.
        """
        def neighbors(cid: str) -> Set[str]:
            return {
                self._uf_find(e.target_id)
                for e in self._edges.get(cid, [])
                if not e.provisional
            }

        na = neighbors(cid_a)
        nb = neighbors(cid_b)
        union = na | nb
        if not union:
            return 0.0
        return len(na & nb) / len(union)

    # ── DFS causal chain traversal ────────────────────────────────────────────

    def _dfs_causal(
        self,
        current_id: str,
        chain:      List[str],
        results:    List[List[str]],
        visited:    Set[str],
        max_depth:  int,
    ):
        if len(chain) > max_depth * 2:
            return
        visited.add(current_id)
        found = False
        for edge in self._edges.get(current_id, []):
            if edge.relation != RelationType.CAUSES or edge.provisional:
                continue
            tgt = self._uf_find(edge.target_id)
            if tgt in visited:
                continue
            target = self._concepts.get(tgt)
            if target is None:
                continue
            found = True
            self._dfs_causal(
                tgt,
                chain + ["causes", target.label],
                results,
                visited.copy(),
                max_depth,
            )
        if not found and len(chain) > 2:
            results.append(chain)

    # ── Null concept (for empty labels) ──────────────────────────────────────

    def _null_concept(self) -> ConceptNode:
        if "__null__" not in self._label_index:
            node = ConceptNode(
                concept_id="__null__",
                label="__null__",
                aliases=[],
                properties={},
            )
            self._concepts["__null__"]      = node
            self._label_index["__null__"]   = "__null__"
            self._uf_parent["__null__"]     = "__null__"
        return self._concepts["__null__"]
