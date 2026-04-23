import json
from typing import Any, Dict, List, Optional, Tuple
from abc import ABC, abstractmethod
from ..documents.document import Document


class VectorStore(ABC):
    @abstractmethod
    def add_documents(self, documents: List[Document], embeddings: List[List[float]]) -> List[str]:
        pass
    
    @abstractmethod
    def similarity_search(
        self,
        query_embedding: List[float],
        k: int = 4,
        filter_dict: Optional[Dict[str, Any]] = None
    ) -> List[Tuple[Document, float]]:
        pass
    
    @abstractmethod
    def delete(self, ids: List[str]) -> None:
        pass
    
    @abstractmethod
    def get(self, ids: List[str]) -> List[Document]:
        pass


class InMemoryVectorStore(VectorStore):
    def __init__(self):
        self.documents: Dict[str, Document] = {}
        self.embeddings: Dict[str, List[float]] = {}
        self.next_id = 0
    
    def add_documents(self, documents: List[Document], embeddings: List[List[float]]) -> List[str]:
        if len(documents) != len(embeddings):
            raise ValueError("Number of documents must match number of embeddings")
        
        ids = []
        for doc, embedding in zip(documents, embeddings):
            doc_id = doc.doc_id or f"doc_{self.next_id}"
            self.next_id += 1
            
            self.documents[doc_id] = doc
            self.embeddings[doc_id] = embedding
            ids.append(doc_id)
        
        return ids
    
    def similarity_search(
        self,
        query_embedding: List[float],
        k: int = 4,
        filter_dict: Optional[Dict[str, Any]] = None
    ) -> List[Tuple[Document, float]]:
        results = []
        
        for doc_id, doc in self.documents.items():
            if filter_dict and not self._matches_filter(doc, filter_dict):
                continue
            
            embedding = self.embeddings[doc_id]
            similarity = self._cosine_similarity(query_embedding, embedding)
            results.append((doc, similarity))
        
        results.sort(key=lambda x: x[1], reverse=True)
        return results[:k]
    
    def delete(self, ids: List[str]) -> None:
        for doc_id in ids:
            if doc_id in self.documents:
                del self.documents[doc_id]
            if doc_id in self.embeddings:
                del self.embeddings[doc_id]
    
    def get(self, ids: List[str]) -> List[Document]:
        return [self.documents[doc_id] for doc_id in ids if doc_id in self.documents]
    
    def save(self, file_path: str) -> None:
        data = {
            "documents": {doc_id: doc.to_dict() for doc_id, doc in self.documents.items()},
            "embeddings": self.embeddings,
            "next_id": self.next_id
        }
        
        with open(file_path, 'w', encoding='utf-8') as f:
            json.dump(data, f, indent=2)
    
    def load(self, file_path: str) -> None:
        with open(file_path, 'r', encoding='utf-8') as f:
            data = json.load(f)
        
        self.documents = {
            doc_id: Document.from_dict(doc_data)
            for doc_id, doc_data in data["documents"].items()
        }
        self.embeddings = data["embeddings"]
        self.next_id = data["next_id"]
    
    def _cosine_similarity(self, vec1: List[float], vec2: List[float]) -> float:
        dot_product = sum(a * b for a, b in zip(vec1, vec2))
        magnitude1 = sum(a * a for a in vec1) ** 0.5
        magnitude2 = sum(b * b for b in vec2) ** 0.5
        
        if magnitude1 == 0 or magnitude2 == 0:
            return 0.0
        
        return dot_product / (magnitude1 * magnitude2)
    
    def _matches_filter(self, doc: Document, filter_dict: Dict[str, Any]) -> bool:
        for key, value in filter_dict.items():
            if key not in doc.metadata or doc.metadata[key] != value:
                return False
        return True
    
    def get_statistics(self) -> Dict[str, Any]:
        return {
            "total_documents": len(self.documents),
            "total_embeddings": len(self.embeddings),
            "next_id": self.next_id
        }
