import hashlib
from typing import List
from abc import ABC, abstractmethod


class EmbeddingFunction(ABC):
    @abstractmethod
    def embed_text(self, text: str) -> List[float]:
        pass
    
    @abstractmethod
    def embed_batch(self, texts: List[str]) -> List[List[float]]:
        pass
    
    @property
    @abstractmethod
    def dimension(self) -> int:
        pass


class SimpleEmbedding(EmbeddingFunction):
    def __init__(self, dimension: int = 384):
        self._dimension = dimension
    
    def embed_text(self, text: str) -> List[float]:
        text_hash = hashlib.sha256(text.encode()).digest()
        
        embedding = []
        for i in range(0, len(text_hash), 2):
            if len(embedding) >= self._dimension:
                break
            byte_val = int.from_bytes(text_hash[i:i+2], 'big')
            embedding.append((byte_val / 65535.0) * 2 - 1)
        
        while len(embedding) < self._dimension:
            embedding.append(0.0)
        
        magnitude = sum(x * x for x in embedding) ** 0.5
        if magnitude > 0:
            embedding = [x / magnitude for x in embedding]
        
        return embedding
    
    def embed_batch(self, texts: List[str]) -> List[List[float]]:
        return [self.embed_text(text) for text in texts]
    
    @property
    def dimension(self) -> int:
        return self._dimension
