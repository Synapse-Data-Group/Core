import time
import json
from typing import Dict, List, Set, Optional, Any, Tuple
from collections import defaultdict
import re


class KnowledgeNode:
    def __init__(self, node_id: str, concept: str, node_type: str = "concept"):
        self.node_id = node_id
        self.concept = concept
        self.node_type = node_type
        self.created_at = time.time()
        self.mentions = 0
        self.confidence = 0.5
        self.metadata: Dict[str, Any] = {}
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            "node_id": self.node_id,
            "concept": self.concept,
            "node_type": self.node_type,
            "mentions": self.mentions,
            "confidence": self.confidence,
            "metadata": self.metadata
        }


class KnowledgeEdge:
    def __init__(self, source_id: str, target_id: str, relationship: str, weight: float = 1.0):
        self.source_id = source_id
        self.target_id = target_id
        self.relationship = relationship
        self.weight = weight
        self.created_at = time.time()
        self.reinforcements = 1
    
    def strengthen(self, amount: float = 0.1):
        self.weight = min(1.0, self.weight + amount)
        self.reinforcements += 1
    
    def weaken(self, amount: float = 0.1):
        self.weight = max(0.0, self.weight - amount)
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            "source_id": self.source_id,
            "target_id": self.target_id,
            "relationship": self.relationship,
            "weight": self.weight,
            "reinforcements": self.reinforcements
        }


class KnowledgeGraph:
    def __init__(self):
        self.nodes: Dict[str, KnowledgeNode] = {}
        self.edges: List[KnowledgeEdge] = []
        self.concept_index: Dict[str, str] = {}
        self.node_counter = 0
        self.extraction_history: List[Dict[str, Any]] = []
    
    def extract_concepts(self, text: str, source: str = "unknown") -> List[str]:
        """Extract key concepts from text"""
        
        text_lower = text.lower()
        
        important_words = []
        words = re.findall(r'\b[a-z]{4,}\b', text_lower)
        
        stop_words = {
            'that', 'this', 'with', 'from', 'have', 'been', 'will', 'would',
            'could', 'should', 'about', 'which', 'their', 'there', 'these',
            'those', 'when', 'where', 'what', 'while', 'through', 'during'
        }
        
        for word in words:
            if word not in stop_words and len(word) > 3:
                important_words.append(word)
        
        word_freq = defaultdict(int)
        for word in important_words:
            word_freq[word] += 1
        
        concepts = [word for word, freq in sorted(word_freq.items(), key=lambda x: x[1], reverse=True)[:10]]
        
        noun_phrases = re.findall(r'\b[A-Z][a-z]+(?:\s+[A-Z][a-z]+)*\b', text)
        concepts.extend([phrase.lower() for phrase in noun_phrases[:5]])
        
        self.extraction_history.append({
            "source": source,
            "concepts_extracted": len(concepts),
            "timestamp": time.time()
        })
        
        return concepts
    
    def add_concept(self, concept: str, concept_type: str = "concept", 
                   metadata: Optional[Dict[str, Any]] = None) -> KnowledgeNode:
        """Add a concept to the knowledge graph"""
        
        concept_normalized = concept.lower().strip()
        
        if concept_normalized in self.concept_index:
            node_id = self.concept_index[concept_normalized]
            node = self.nodes[node_id]
            node.mentions += 1
            node.confidence = min(1.0, node.confidence + 0.05)
            return node
        
        self.node_counter += 1
        node_id = f"node_{self.node_counter}"
        
        node = KnowledgeNode(node_id, concept_normalized, concept_type)
        if metadata:
            node.metadata = metadata
        
        self.nodes[node_id] = node
        self.concept_index[concept_normalized] = node_id
        
        return node
    
    def add_relationship(self, concept1: str, concept2: str, relationship: str = "relates_to",
                        weight: float = 1.0):
        """Add a relationship between two concepts"""
        
        node1 = self.add_concept(concept1)
        node2 = self.add_concept(concept2)
        
        existing_edge = self._find_edge(node1.node_id, node2.node_id, relationship)
        
        if existing_edge:
            existing_edge.strengthen()
        else:
            edge = KnowledgeEdge(node1.node_id, node2.node_id, relationship, weight)
            self.edges.append(edge)
    
    def _find_edge(self, source_id: str, target_id: str, relationship: str) -> Optional[KnowledgeEdge]:
        """Find an existing edge"""
        
        for edge in self.edges:
            if (edge.source_id == source_id and edge.target_id == target_id and 
                edge.relationship == relationship):
                return edge
        return None
    
    def process_debate_content(self, content: str, agent_id: str, message_type: str):
        """Process debate content and update knowledge graph"""
        
        concepts = self.extract_concepts(content, f"{agent_id}_{message_type}")
        
        for concept in concepts:
            self.add_concept(concept, "debate_concept", {
                "agent_id": agent_id,
                "message_type": message_type,
                "timestamp": time.time()
            })
        
        for i in range(len(concepts) - 1):
            self.add_relationship(concepts[i], concepts[i + 1], "co_occurs_with", 0.5)
        
        if message_type == "proposal":
            for concept in concepts[:3]:
                self.add_relationship("proposal", concept, "contains", 0.8)
        elif message_type == "challenge":
            for concept in concepts[:3]:
                self.add_relationship("challenge", concept, "questions", 0.7)
    
    def query_related_concepts(self, concept: str, max_results: int = 5) -> List[Tuple[str, float]]:
        """Query concepts related to a given concept"""
        
        concept_normalized = concept.lower().strip()
        
        if concept_normalized not in self.concept_index:
            return []
        
        node_id = self.concept_index[concept_normalized]
        
        related = []
        for edge in self.edges:
            if edge.source_id == node_id:
                target_node = self.nodes[edge.target_id]
                related.append((target_node.concept, edge.weight))
            elif edge.target_id == node_id:
                source_node = self.nodes[edge.source_id]
                related.append((source_node.concept, edge.weight))
        
        related.sort(key=lambda x: x[1], reverse=True)
        return related[:max_results]
    
    def get_concept_context(self, concept: str) -> Dict[str, Any]:
        """Get full context for a concept"""
        
        concept_normalized = concept.lower().strip()
        
        if concept_normalized not in self.concept_index:
            return {"found": False}
        
        node_id = self.concept_index[concept_normalized]
        node = self.nodes[node_id]
        
        related = self.query_related_concepts(concept)
        
        return {
            "found": True,
            "concept": node.concept,
            "mentions": node.mentions,
            "confidence": node.confidence,
            "related_concepts": related,
            "metadata": node.metadata
        }
    
    def find_shortest_path(self, concept1: str, concept2: str) -> Optional[List[str]]:
        """Find shortest path between two concepts"""
        
        concept1_norm = concept1.lower().strip()
        concept2_norm = concept2.lower().strip()
        
        if concept1_norm not in self.concept_index or concept2_norm not in self.concept_index:
            return None
        
        start_id = self.concept_index[concept1_norm]
        end_id = self.concept_index[concept2_norm]
        
        adjacency = defaultdict(list)
        for edge in self.edges:
            adjacency[edge.source_id].append(edge.target_id)
            adjacency[edge.target_id].append(edge.source_id)
        
        queue = [(start_id, [start_id])]
        visited = {start_id}
        
        while queue:
            current_id, path = queue.pop(0)
            
            if current_id == end_id:
                return [self.nodes[node_id].concept for node_id in path]
            
            for neighbor_id in adjacency[current_id]:
                if neighbor_id not in visited:
                    visited.add(neighbor_id)
                    queue.append((neighbor_id, path + [neighbor_id]))
        
        return None
    
    def get_most_central_concepts(self, top_n: int = 10) -> List[Tuple[str, int]]:
        """Get most central concepts by degree centrality"""
        
        degree = defaultdict(int)
        
        for edge in self.edges:
            degree[edge.source_id] += 1
            degree[edge.target_id] += 1
        
        concept_degrees = [
            (self.nodes[node_id].concept, deg)
            for node_id, deg in degree.items()
        ]
        
        concept_degrees.sort(key=lambda x: x[1], reverse=True)
        return concept_degrees[:top_n]
    
    def export_graph(self, filepath: str):
        """Export knowledge graph to JSON"""
        
        graph_data = {
            "nodes": [node.to_dict() for node in self.nodes.values()],
            "edges": [edge.to_dict() for edge in self.edges],
            "stats": self.get_stats()
        }
        
        with open(filepath, 'w') as f:
            json.dump(graph_data, f, indent=2)
    
    def import_graph(self, filepath: str):
        """Import knowledge graph from JSON"""
        
        with open(filepath, 'r') as f:
            graph_data = json.load(f)
        
        for node_data in graph_data["nodes"]:
            node = KnowledgeNode(node_data["node_id"], node_data["concept"], node_data["node_type"])
            node.mentions = node_data["mentions"]
            node.confidence = node_data["confidence"]
            node.metadata = node_data["metadata"]
            self.nodes[node.node_id] = node
            self.concept_index[node.concept] = node.node_id
        
        for edge_data in graph_data["edges"]:
            edge = KnowledgeEdge(
                edge_data["source_id"],
                edge_data["target_id"],
                edge_data["relationship"],
                edge_data["weight"]
            )
            edge.reinforcements = edge_data["reinforcements"]
            self.edges.append(edge)
    
    def get_stats(self) -> Dict[str, Any]:
        """Get knowledge graph statistics"""
        
        return {
            "total_nodes": len(self.nodes),
            "total_edges": len(self.edges),
            "total_concepts": len(self.concept_index),
            "avg_node_degree": len(self.edges) * 2 / len(self.nodes) if self.nodes else 0,
            "most_central": self.get_most_central_concepts(5),
            "extractions": len(self.extraction_history)
        }
