from typing import Any, Dict, List, Set, Tuple
from collections import defaultdict


class LSHIndex:
    def __init__(self, num_bands: int = 16, rows_per_band: int = 8):
        self.num_bands = num_bands
        self.rows_per_band = rows_per_band
        self.signature_length = num_bands * rows_per_band
        
        self.buckets: Dict[Tuple[int, int], Set[str]] = defaultdict(set)
        self.signatures: Dict[str, List[int]] = {}
    
    def add(self, doc_id: str, signature: List[int]) -> None:
        if len(signature) != self.signature_length:
            raise ValueError(f"Signature length must be {self.signature_length}")
        
        self.signatures[doc_id] = signature
        
        for band_idx in range(self.num_bands):
            start = band_idx * self.rows_per_band
            end = start + self.rows_per_band
            band_signature = tuple(signature[start:end])
            
            bucket_key = (band_idx, hash(band_signature))
            self.buckets[bucket_key].add(doc_id)
    
    def query(self, signature: List[int], threshold: float = 0.5) -> List[str]:
        if len(signature) != self.signature_length:
            raise ValueError(f"Signature length must be {self.signature_length}")
        
        candidates = set()
        
        for band_idx in range(self.num_bands):
            start = band_idx * self.rows_per_band
            end = start + self.rows_per_band
            band_signature = tuple(signature[start:end])
            
            bucket_key = (band_idx, hash(band_signature))
            
            if bucket_key in self.buckets:
                candidates.update(self.buckets[bucket_key])
        
        results = []
        for candidate_id in candidates:
            similarity = self._jaccard_similarity(signature, self.signatures[candidate_id])
            if similarity >= threshold:
                results.append(candidate_id)
        
        return results
    
    def query_with_scores(
        self,
        signature: List[int],
        threshold: float = 0.5
    ) -> List[Tuple[str, float]]:
        if len(signature) != self.signature_length:
            raise ValueError(f"Signature length must be {self.signature_length}")
        
        candidates = set()
        
        for band_idx in range(self.num_bands):
            start = band_idx * self.rows_per_band
            end = start + self.rows_per_band
            band_signature = tuple(signature[start:end])
            
            bucket_key = (band_idx, hash(band_signature))
            
            if bucket_key in self.buckets:
                candidates.update(self.buckets[bucket_key])
        
        results = []
        for candidate_id in candidates:
            similarity = self._jaccard_similarity(signature, self.signatures[candidate_id])
            if similarity >= threshold:
                results.append((candidate_id, similarity))
        
        results.sort(key=lambda x: x[1], reverse=True)
        
        return results
    
    def _jaccard_similarity(self, sig1: List[int], sig2: List[int]) -> float:
        if len(sig1) != len(sig2):
            return 0.0
        
        matches = sum(1 for a, b in zip(sig1, sig2) if a == b)
        return matches / len(sig1)
    
    def remove(self, doc_id: str) -> None:
        if doc_id not in self.signatures:
            return
        
        signature = self.signatures[doc_id]
        
        for band_idx in range(self.num_bands):
            start = band_idx * self.rows_per_band
            end = start + self.rows_per_band
            band_signature = tuple(signature[start:end])
            
            bucket_key = (band_idx, hash(band_signature))
            
            if bucket_key in self.buckets:
                self.buckets[bucket_key].discard(doc_id)
                
                if not self.buckets[bucket_key]:
                    del self.buckets[bucket_key]
        
        del self.signatures[doc_id]
    
    def get_statistics(self) -> Dict[str, Any]:
        return {
            "total_documents": len(self.signatures),
            "total_buckets": len(self.buckets),
            "avg_bucket_size": (
                sum(len(bucket) for bucket in self.buckets.values()) / len(self.buckets)
                if self.buckets else 0
            ),
            "num_bands": self.num_bands,
            "rows_per_band": self.rows_per_band
        }
