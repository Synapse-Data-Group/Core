"""
CLM - Cognitive Language Model
reasoning/consolidation.py

Consolidation engine — the "sleep cycle" of the cognitive system.

The critique identified the core problem:
  "Without consolidation, long-term learning becomes noisy, redundant,
   and unstable. This is probably the single highest ROI feature."

Biological analogy:
  awake  = learning from signals (cognitive loop)
  sleep  = restructuring knowledge (this module)

Algorithms used (all pure Python stdlib, zero dependencies):

1. EBBINGHAUS DECAY on episodic memory
   R = e^(-t/S) — episodes fade unless reinforced.
   Stable episodes (high S, high R) → promoted to semantic memory.
   Source: Ebbinghaus (1885), FSRS (2022).

2. ONLINE TF-IDF for cross-episode concept extraction
   TF(t,d)  = count(t,d) / total_terms(d)
   IDF(t)   = log(N / (1 + df(t)))  [smoothed]
   TF-IDF(t,d) = TF × IDF
   Concepts with high TF-IDF across multiple episodes are
   domain-specific knowledge worth promoting to semantic memory.
   Concepts with very low IDF (appear everywhere) are stopwords — skip.
   Source: Salton & McGill (1983), incremental variant.

3. DENSITY-BASED EPISODE CLUSTERING (DBSCAN-inspired)
   Distance metric: 1 - Jaccard(concepts_A, concepts_B)
   Episodes within distance ε of each other form a cluster.
   Each cluster → one compressed semantic insight.
   No k needed. Noise episodes (isolated) are kept but not promoted.
   Source: Ester et al. (1996), pure Python O(n²) for small n.

4. PAGERANK on ConceptGraph for importance-weighted pruning
   (Delegated to ConceptGraph.run_hygiene_cycle())

5. CONFIDENCE RECALIBRATION
   After consolidation, recalibrate semantic memory confidence scores
   based on how many episodes support each insight.
   confidence = 1 - 1/(1 + supporting_episodes)  [logistic]
"""

from __future__ import annotations
import json
import math
import time
from collections import defaultdict
from dataclasses import dataclass, field
from typing import Any, Dict, List, Optional, Set, Tuple, TYPE_CHECKING

if TYPE_CHECKING:
    from clm.memory.episodic import EpisodicMemory
    from clm.memory.semantic import SemanticMemory
    from clm.reasoning.concept_graph import ConceptGraph


# ── Episodic memory stability model ──────────────────────────────────────────

@dataclass
class EpisodicStability:
    """
    Tracks Ebbinghaus stability for an episodic memory entry.
    R(t) = e^(-t/S)
    S increases with each reinforcement (FSRS-inspired).
    """
    episode_id:      str
    stability:       float = 2.0    # Initial stability in hours
    last_reinforced: float = field(default_factory=time.time)
    reinforcement_count: int = 0

    def retrievability(self, now: Optional[float] = None) -> float:
        t = ((now or time.time()) - self.last_reinforced) / 3600.0
        return math.exp(-t / max(self.stability, 0.1))

    def reinforce(self):
        now = time.time()
        r   = self.retrievability(now)
        self.stability          = self.stability * (1.0 + 0.2 * r)
        self.last_reinforced    = now
        self.reinforcement_count += 1

    def should_promote(self, threshold: float = 0.6) -> bool:
        """True if this episode is stable enough to promote to semantic memory."""
        return (
            self.reinforcement_count >= 2
            and self.retrievability() >= threshold
        )

    def should_prune(self, threshold: float = 0.05) -> bool:
        """True if this episode has decayed below the pruning threshold."""
        return self.retrievability() < threshold


@dataclass
class ConsolidationReport:
    """Summary of a consolidation cycle."""
    episodes_processed:   int
    episodes_promoted:    int
    episodes_pruned:      int
    insights_created:     int
    insights_updated:     int
    clusters_found:       int
    concepts_extracted:   int
    graph_hygiene:        Dict[str, int]
    duration_ms:          float
    timestamp:            float = field(default_factory=time.time)

    def to_dict(self) -> Dict[str, Any]:
        return {
            "episodes_processed": self.episodes_processed,
            "episodes_promoted":  self.episodes_promoted,
            "episodes_pruned":    self.episodes_pruned,
            "insights_created":   self.insights_created,
            "insights_updated":   self.insights_updated,
            "clusters_found":     self.clusters_found,
            "concepts_extracted": self.concepts_extracted,
            "graph_hygiene":      self.graph_hygiene,
            "duration_ms":        round(self.duration_ms, 2),
        }


class ConsolidationEngine:
    """
    The consolidation engine — runs periodically to restructure knowledge.

    Call run_cycle() from a background thread or after N episodes.
    Never call from the hot cognitive loop path.

    Pipeline:
      1. Apply Ebbinghaus decay to all tracked episodes
      2. Prune fully-decayed episodes
      3. Extract cross-episode concepts via online TF-IDF
      4. Cluster similar episodes via Jaccard-DBSCAN
      5. Compress each cluster into a semantic insight
      6. Promote stable individual episodes to semantic memory
      7. Run ConceptGraph hygiene cycle
      8. Recalibrate confidence scores
    """

    def __init__(
        self,
        episodes_per_cycle:     int   = 50,
        min_cluster_size:       int   = 2,
        cluster_epsilon:        float = 0.4,   # Jaccard distance threshold
        promotion_threshold:    float = 0.6,   # Min retrievability to promote
        pruning_threshold:      float = 0.05,  # Max retrievability before pruning
        min_idf:                float = 0.5,   # Min IDF to consider a concept significant
        max_stopword_freq:      float = 0.8,   # Concepts in >80% of episodes = stopwords
    ):
        self.episodes_per_cycle  = episodes_per_cycle
        self.min_cluster_size    = min_cluster_size
        self.cluster_epsilon     = cluster_epsilon
        self.promotion_threshold = promotion_threshold
        self.pruning_threshold   = pruning_threshold
        self.min_idf             = min_idf
        self.max_stopword_freq   = max_stopword_freq

        # Stability tracking per episode
        self._stability: Dict[str, EpisodicStability] = {}

        # Online TF-IDF state
        self._doc_count:  int              = 0
        self._doc_freq:   Dict[str, int]   = defaultdict(int)  # term → #docs containing it

        # Stats
        self._cycles_run      = 0
        self._total_promoted  = 0
        self._total_pruned    = 0
        self._total_insights  = 0

    # ── Main cycle ────────────────────────────────────────────────────────────

    def run_cycle(
        self,
        episodic_memory: "EpisodicMemory",
        semantic_memory: "SemanticMemory",
        concept_graph:   "ConceptGraph",
    ) -> ConsolidationReport:
        """
        Run a full consolidation cycle.
        Safe to call from a background thread.
        """
        t0 = time.perf_counter()
        self._cycles_run += 1

        # 1. Load recent episodes
        episodes = episodic_memory.get_recent(n=self.episodes_per_cycle * 2)
        if not episodes:
            elapsed = (time.perf_counter() - t0) * 1000
            return ConsolidationReport(
                episodes_processed=0, episodes_promoted=0, episodes_pruned=0,
                insights_created=0, insights_updated=0, clusters_found=0,
                concepts_extracted=0, graph_hygiene={}, duration_ms=elapsed,
            )

        # 2. Apply Ebbinghaus decay, register new episodes
        now = time.time()
        for ep in episodes:
            eid = ep.get("episode_id") or ep.get("id", "")
            if not eid:
                continue
            if eid not in self._stability:
                self._stability[eid] = EpisodicStability(episode_id=eid)
            # Reinforce if recently accessed (within last hour)
            last_access = ep.get("timestamp", 0)
            if now - last_access < 3600:
                self._stability[eid].reinforce()

        # 3. Prune fully-decayed episodes
        pruned_ids = {
            eid for eid, stab in self._stability.items()
            if stab.should_prune(self.pruning_threshold)
        }
        for eid in pruned_ids:
            del self._stability[eid]
        episodes_pruned = len(pruned_ids)
        self._total_pruned += episodes_pruned

        # 4. Extract concepts from episodes via online TF-IDF
        episode_concepts = self._extract_concepts_tfidf(episodes)
        concepts_extracted = sum(len(v) for v in episode_concepts.values())

        # 5. Cluster similar episodes (Jaccard-DBSCAN)
        clusters = self._dbscan_cluster(episode_concepts)

        # 6. Compress clusters → semantic insights
        insights_created = 0
        insights_updated = 0
        for cluster in clusters:
            cluster_eps = [ep for ep in episodes if ep.get("episode_id") in cluster]
            if not cluster_eps:
                continue
            result = self._compress_cluster(
                cluster_eps, episode_concepts, semantic_memory
            )
            if result == "created":
                insights_created += 1
            elif result == "updated":
                insights_updated += 1

        # 7. Promote stable individual episodes
        episodes_promoted = 0
        for ep in episodes:
            eid = ep.get("episode_id") or ep.get("id", "")
            stab = self._stability.get(eid)
            if stab and stab.should_promote(self.promotion_threshold):
                self._promote_episode(ep, semantic_memory)
                episodes_promoted += 1
        self._total_promoted += episodes_promoted

        # 8. ConceptGraph hygiene cycle
        hygiene_result = concept_graph.run_hygiene_cycle()

        # 9. Recalibrate confidence
        self._recalibrate_confidence(semantic_memory, episode_concepts)

        elapsed = (time.perf_counter() - t0) * 1000
        self._total_insights += insights_created

        return ConsolidationReport(
            episodes_processed=len(episodes),
            episodes_promoted=episodes_promoted,
            episodes_pruned=episodes_pruned,
            insights_created=insights_created,
            insights_updated=insights_updated,
            clusters_found=len(clusters),
            concepts_extracted=concepts_extracted,
            graph_hygiene=hygiene_result,
            duration_ms=elapsed,
        )

    # ── Online TF-IDF concept extraction ─────────────────────────────────────

    def _extract_concepts_tfidf(
        self,
        episodes: List[Dict[str, Any]],
    ) -> Dict[str, List[str]]:
        """
        Extract significant concepts from each episode using TF-IDF.

        TF(t,d)  = count(t,d) / total_terms(d)
        IDF(t)   = log(N / (1 + df(t)))
        TF-IDF   = TF × IDF

        Returns: episode_id → [significant concept labels]
        """
        n_docs = len(episodes)
        if n_docs == 0:
            return {}

        # Build term frequency per episode
        episode_tf: Dict[str, Dict[str, float]] = {}
        for ep in episodes:
            eid   = ep.get("episode_id") or ep.get("id", "")
            terms = self._episode_to_terms(ep)
            if not terms:
                continue
            tf: Dict[str, float] = defaultdict(float)
            for t in terms:
                tf[t] += 1.0
            total = max(len(terms), 1)
            episode_tf[eid] = {t: c / total for t, c in tf.items()}

        # Update global document frequency
        for eid, tf in episode_tf.items():
            for term in tf:
                self._doc_freq[term] += 1
        self._doc_count += n_docs

        # Compute TF-IDF and select significant concepts
        result: Dict[str, List[str]] = {}
        N = max(self._doc_count, 1)

        for eid, tf in episode_tf.items():
            scored: List[Tuple[float, str]] = []
            for term, tf_val in tf.items():
                df  = self._doc_freq.get(term, 1)
                idf = math.log(N / (1.0 + df))
                # Skip stopwords (appear in too many docs)
                if df / N > self.max_stopword_freq:
                    continue
                if idf < self.min_idf:
                    continue
                scored.append((tf_val * idf, term))
            scored.sort(reverse=True)
            result[eid] = [term for _, term in scored[:10]]

        return result

    def _episode_to_terms(self, episode: Dict[str, Any]) -> List[str]:
        """Extract term list from an episode dict."""
        terms: List[str] = []
        # From concept labels in metadata
        for key in ("concepts", "labels", "tags"):
            val = episode.get(key, [])
            if isinstance(val, list):
                terms.extend(str(v).lower().strip() for v in val if v)
        # From content text (simple whitespace tokenization)
        content = episode.get("content") or episode.get("text") or episode.get("input", "")
        if isinstance(content, str):
            tokens = content.lower().split()
            # Keep tokens of length 3-20, skip numbers
            terms.extend(
                t.strip(".,!?;:\"'()[]") for t in tokens
                if 3 <= len(t) <= 20 and not t.isdigit()
            )
        return terms

    # ── DBSCAN-inspired episode clustering ────────────────────────────────────

    def _dbscan_cluster(
        self,
        episode_concepts: Dict[str, List[str]],
    ) -> List[Set[str]]:
        """
        Density-based clustering of episodes by concept overlap.

        Distance: 1 - Jaccard(concepts_A, concepts_B)
        ε: cluster_epsilon (default 0.4 → Jaccard similarity >= 0.6)
        MinPts: min_cluster_size

        Returns list of clusters (sets of episode_ids).
        O(n²) — acceptable for n <= 200 episodes.
        """
        episode_ids = list(episode_concepts.keys())
        n = len(episode_ids)
        if n == 0:
            return []

        concept_sets = {
            eid: set(concepts)
            for eid, concepts in episode_concepts.items()
        }

        # Precompute neighborhood for each episode
        neighbors: Dict[str, List[str]] = {eid: [] for eid in episode_ids}
        for i in range(n):
            for j in range(i + 1, n):
                a, b = episode_ids[i], episode_ids[j]
                dist = self._jaccard_distance(concept_sets[a], concept_sets[b])
                if dist <= self.cluster_epsilon:
                    neighbors[a].append(b)
                    neighbors[b].append(a)

        # DBSCAN expansion
        visited:   Set[str] = set()
        clustered: Set[str] = set()
        clusters:  List[Set[str]] = []

        for eid in episode_ids:
            if eid in visited:
                continue
            visited.add(eid)

            if len(neighbors[eid]) < self.min_cluster_size - 1:
                continue  # Noise point

            # Start new cluster
            cluster: Set[str] = {eid}
            queue = list(neighbors[eid])

            while queue:
                cur = queue.pop(0)
                if cur not in visited:
                    visited.add(cur)
                    if len(neighbors[cur]) >= self.min_cluster_size - 1:
                        queue.extend(
                            nb for nb in neighbors[cur] if nb not in visited
                        )
                if cur not in clustered:
                    cluster.add(cur)
                    clustered.add(cur)

            if len(cluster) >= self.min_cluster_size:
                clusters.append(cluster)

        return clusters

    @staticmethod
    def _jaccard_distance(a: Set[str], b: Set[str]) -> float:
        if not a and not b:
            return 0.0
        union = a | b
        if not union:
            return 1.0
        return 1.0 - len(a & b) / len(union)

    # ── Cluster compression → semantic insight ────────────────────────────────

    def _compress_cluster(
        self,
        cluster_episodes: List[Dict[str, Any]],
        episode_concepts: Dict[str, List[str]],
        semantic_memory:  "SemanticMemory",
    ) -> str:
        """
        Compress a cluster of similar episodes into one semantic insight.

        The insight captures:
          - The shared concepts (intersection of concept sets)
          - The most common content pattern
          - Confidence proportional to cluster size

        Returns "created" or "updated".
        """
        # Find shared concepts across all episodes in cluster
        concept_sets = []
        for ep in cluster_episodes:
            eid = ep.get("episode_id") or ep.get("id", "")
            concepts = episode_concepts.get(eid, [])
            if concepts:
                concept_sets.append(set(concepts))

        if not concept_sets:
            return "skipped"

        # Intersection = concepts shared by all; union = any concept
        shared = concept_sets[0]
        for cs in concept_sets[1:]:
            shared = shared & cs

        # If intersection is empty, use most frequent concepts
        if not shared:
            freq: Dict[str, int] = defaultdict(int)
            for cs in concept_sets:
                for c in cs:
                    freq[c] += 1
            shared = {c for c, f in freq.items() if f >= len(concept_sets) // 2 + 1}

        if not shared:
            return "skipped"

        # Build insight content from most representative episode
        rep_ep = max(
            cluster_episodes,
            key=lambda ep: len(episode_concepts.get(
                ep.get("episode_id") or ep.get("id", ""), []
            ))
        )
        content = (
            rep_ep.get("output")
            or rep_ep.get("response")
            or rep_ep.get("content")
            or " ".join(sorted(shared)[:5])
        )
        if not isinstance(content, str):
            content = str(content)

        # Confidence: logistic function of cluster size
        # 2 episodes → 0.67, 5 → 0.86, 10 → 0.92
        confidence = 1.0 - 1.0 / (1.0 + len(cluster_episodes))

        insight = {
            "content":    content[:500],
            "concepts":   sorted(shared)[:10],
            "confidence": round(confidence, 3),
            "source":     "consolidation",
            "cluster_size": len(cluster_episodes),
        }

        # Check if a similar insight already exists
        existing = semantic_memory.get_relevant_insights(
            " ".join(sorted(shared)[:5]), k=3
        )
        for ex in existing:
            ex_concepts = set(ex.get("concepts", []))
            if len(ex_concepts & shared) / max(len(ex_concepts | shared), 1) > 0.5:
                # Update existing insight
                semantic_memory.update_insight(ex.get("insight_id", ""), insight)
                return "updated"

        semantic_memory.store_insight(insight)
        return "created"

    # ── Episode promotion ─────────────────────────────────────────────────────

    def _promote_episode(
        self,
        episode:         Dict[str, Any],
        semantic_memory: "SemanticMemory",
    ):
        """Promote a stable individual episode to semantic memory."""
        content = (
            episode.get("output")
            or episode.get("response")
            or episode.get("content")
            or ""
        )
        if not content or not isinstance(content, str):
            return

        concepts = episode.get("concepts") or episode.get("labels") or []
        insight = {
            "content":    content[:500],
            "concepts":   concepts[:10],
            "confidence": 0.6,
            "source":     "episode_promotion",
        }
        semantic_memory.store_insight(insight)

    # ── Confidence recalibration ──────────────────────────────────────────────

    def _recalibrate_confidence(
        self,
        semantic_memory:  "SemanticMemory",
        episode_concepts: Dict[str, List[str]],
    ):
        """
        Recalibrate semantic memory confidence based on episodic support.
        Insights supported by more episodes get higher confidence.
        """
        # Build concept → episode count index
        concept_support: Dict[str, int] = defaultdict(int)
        for concepts in episode_concepts.values():
            for c in concepts:
                concept_support[c] += 1

        insights = semantic_memory.get_recent_insights(n=100)
        for insight in insights:
            concepts = insight.get("concepts", [])
            if not concepts:
                continue
            support = sum(concept_support.get(c, 0) for c in concepts)
            if support == 0:
                continue
            # Logistic confidence update
            new_conf = 1.0 - 1.0 / (1.0 + support * 0.5)
            current  = insight.get("confidence", 0.5)
            # Blend: don't drop confidence drastically
            blended  = 0.7 * current + 0.3 * new_conf
            iid = insight.get("insight_id", "")
            if iid:
                semantic_memory.update_insight(iid, {"confidence": round(blended, 3)})

    # ── Stats ─────────────────────────────────────────────────────────────────

    def get_stats(self) -> Dict[str, Any]:
        return {
            "cycles_run":      self._cycles_run,
            "total_promoted":  self._total_promoted,
            "total_pruned":    self._total_pruned,
            "total_insights":  self._total_insights,
            "tracked_episodes": len(self._stability),
            "known_terms":     len(self._doc_freq),
        }
