"""
Virtual Vector Base - Semantic connection system for neurons

Neurons connect based on semantic similarity, not hardcoded topology.
Enables emergent clustering and dynamic rewiring.
"""

import math
from typing import Dict, List, Tuple, Optional, Set
from dataclasses import dataclass
from collections import defaultdict


@dataclass
class SemanticVector:
    """Semantic representation of a neuron"""
    neuron_id: str
    vector: List[float]
    last_updated: float
    
    def magnitude(self) -> float:
        """Calculate vector magnitude"""
        return math.sqrt(sum(x * x for x in self.vector))
    
    def normalize(self):
        """Normalize vector to unit length"""
        mag = self.magnitude()
        if mag > 0:
            self.vector = [x / mag for x in self.vector]


class VirtualVectorBase:
    """
    Manages semantic vectors for all neurons
    Enables dynamic connection discovery based on similarity
    """
    
    def __init__(self, vector_dimension: int = 128, similarity_threshold: float = 0.7):
        self.dimension = vector_dimension
        self.similarity_threshold = similarity_threshold
        self.vectors: Dict[str, SemanticVector] = {}
        self.connection_cache: Dict[Tuple[str, str], float] = {}
        self.clusters: Dict[str, Set[str]] = defaultdict(set)
    
    def add_neuron(self, neuron_id: str, initial_vector: Optional[List[float]] = None):
        """Add neuron with semantic vector"""
        import random
        import time
        
        if initial_vector is None:
            initial_vector = [random.gauss(0, 0.1) for _ in range(self.dimension)]
        
        vector = SemanticVector(
            neuron_id=neuron_id,
            vector=initial_vector,
            last_updated=time.time()
        )
        vector.normalize()
        self.vectors[neuron_id] = vector
    
    def remove_neuron(self, neuron_id: str):
        """Remove neuron from vector base"""
        if neuron_id in self.vectors:
            del self.vectors[neuron_id]
        
        self.connection_cache = {
            k: v for k, v in self.connection_cache.items()
            if neuron_id not in k
        }
        
        for cluster in self.clusters.values():
            cluster.discard(neuron_id)
    
    def cosine_similarity(self, neuron_a: str, neuron_b: str) -> float:
        """Calculate cosine similarity between two neurons"""
        cache_key = tuple(sorted([neuron_a, neuron_b]))
        if cache_key in self.connection_cache:
            return self.connection_cache[cache_key]
        
        if neuron_a not in self.vectors or neuron_b not in self.vectors:
            return 0.0
        
        vec_a = self.vectors[neuron_a].vector
        vec_b = self.vectors[neuron_b].vector
        
        dot_product = sum(a * b for a, b in zip(vec_a, vec_b))
        
        mag_a = math.sqrt(sum(a * a for a in vec_a))
        mag_b = math.sqrt(sum(b * b for b in vec_b))
        
        if mag_a == 0 or mag_b == 0:
            similarity = 0.0
        else:
            similarity = dot_product / (mag_a * mag_b)
        
        self.connection_cache[cache_key] = similarity
        return similarity
    
    def should_connect(self, neuron_a: str, neuron_b: str) -> bool:
        """Determine if two neurons should be connected"""
        similarity = self.cosine_similarity(neuron_a, neuron_b)
        return similarity > self.similarity_threshold
    
    def find_nearest_neighbors(self, neuron_id: str, k: int = 10) -> List[Tuple[str, float]]:
        """Find k most similar neurons"""
        if neuron_id not in self.vectors:
            return []
        
        similarities = []
        for other_id in self.vectors:
            if other_id != neuron_id:
                sim = self.cosine_similarity(neuron_id, other_id)
                similarities.append((other_id, sim))
        
        similarities.sort(key=lambda x: x[1], reverse=True)
        return similarities[:k]
    
    def update_vector(self, neuron_id: str, activity_pattern: List[float], learning_rate: float = 0.01):
        """
        Update neuron vector based on activity
        Hebbian-like: neurons that fire together, drift together in vector space
        """
        import time
        
        if neuron_id not in self.vectors:
            return
        
        vector = self.vectors[neuron_id]
        
        if len(activity_pattern) != self.dimension:
            return
        
        for i in range(self.dimension):
            vector.vector[i] += learning_rate * activity_pattern[i]
        
        vector.normalize()
        vector.last_updated = time.time()
        
        self.connection_cache = {
            k: v for k, v in self.connection_cache.items()
            if neuron_id not in k
        }
    
    def move_closer(self, neuron_a: str, neuron_b: str, amount: float = 0.05):
        """Move two neuron vectors closer together (Hebbian learning)"""
        if neuron_a not in self.vectors or neuron_b not in self.vectors:
            return
        
        vec_a = self.vectors[neuron_a]
        vec_b = self.vectors[neuron_b]
        
        for i in range(self.dimension):
            direction = vec_b.vector[i] - vec_a.vector[i]
            vec_a.vector[i] += amount * direction
            vec_b.vector[i] -= amount * direction
        
        vec_a.normalize()
        vec_b.normalize()
        
        import time
        vec_a.last_updated = time.time()
        vec_b.last_updated = time.time()
        
        cache_key = tuple(sorted([neuron_a, neuron_b]))
        if cache_key in self.connection_cache:
            del self.connection_cache[cache_key]
    
    def discover_clusters(self, min_cluster_size: int = 5) -> Dict[str, Set[str]]:
        """
        Discover functional clusters based on vector similarity
        Emergent organization - not predefined
        """
        self.clusters.clear()
        visited = set()
        cluster_id = 0
        
        for neuron_id in self.vectors:
            if neuron_id in visited:
                continue
            
            cluster = self._expand_cluster(neuron_id, visited)
            
            if len(cluster) >= min_cluster_size:
                self.clusters[f"cluster_{cluster_id}"] = cluster
                cluster_id += 1
        
        return self.clusters
    
    def _expand_cluster(self, seed_neuron: str, visited: Set[str]) -> Set[str]:
        """Expand cluster from seed neuron using similarity threshold"""
        cluster = {seed_neuron}
        visited.add(seed_neuron)
        queue = [seed_neuron]
        
        while queue:
            current = queue.pop(0)
            neighbors = self.find_nearest_neighbors(current, k=20)
            
            for neighbor_id, similarity in neighbors:
                if neighbor_id not in visited and similarity > self.similarity_threshold:
                    cluster.add(neighbor_id)
                    visited.add(neighbor_id)
                    queue.append(neighbor_id)
        
        return cluster
    
    def get_cluster_for_neuron(self, neuron_id: str) -> Optional[str]:
        """Get cluster ID for a neuron"""
        for cluster_id, neurons in self.clusters.items():
            if neuron_id in neurons:
                return cluster_id
        return None
    
    def create_specialized_vector(self, specialization: str) -> List[float]:
        """
        Create semantic vector for a specialization
        Uses simple hash-based approach for deterministic vectors
        """
        import hashlib
        
        hash_obj = hashlib.md5(specialization.encode())
        hash_bytes = hash_obj.digest()
        
        vector = []
        for i in range(0, len(hash_bytes), 2):
            if i + 1 < len(hash_bytes):
                value = (hash_bytes[i] - 128) / 128.0
                vector.append(value)
        
        while len(vector) < self.dimension:
            vector.append(0.0)
        
        vector = vector[:self.dimension]
        
        mag = math.sqrt(sum(x * x for x in vector))
        if mag > 0:
            vector = [x / mag for x in vector]
        
        return vector
    
    def get_network_statistics(self) -> Dict[str, any]:
        """Get statistics about the vector base"""
        if not self.vectors:
            return {'total_neurons': 0}
        
        avg_connections = 0
        for neuron_id in self.vectors:
            neighbors = self.find_nearest_neighbors(neuron_id, k=10)
            strong_connections = sum(1 for _, sim in neighbors if sim > self.similarity_threshold)
            avg_connections += strong_connections
        
        avg_connections /= len(self.vectors)
        
        return {
            'total_neurons': len(self.vectors),
            'vector_dimension': self.dimension,
            'similarity_threshold': self.similarity_threshold,
            'avg_connections_per_neuron': avg_connections,
            'total_clusters': len(self.clusters),
            'cached_similarities': len(self.connection_cache)
        }
