from typing import Any, Dict, List, Optional, Tuple
from enum import Enum
from .tfidf import TFIDFVectorizer
from .minhash import MinHasher
from .lsh import LSHIndex


class SimilarityMethod(Enum):
    TFIDF = "tfidf"
    MINHASH = "minhash"
    LSH = "lsh"
    HYBRID = "hybrid"


class TaskSimilarity:
    def __init__(
        self,
        method: SimilarityMethod = SimilarityMethod.HYBRID,
        tfidf_max_features: int = 1000,
        minhash_num_perm: int = 128,
        lsh_num_bands: int = 16
    ):
        self.method = method
        
        self.tfidf = TFIDFVectorizer(max_features=tfidf_max_features)
        self.minhasher = MinHasher(num_perm=minhash_num_perm)
        self.lsh = LSHIndex(
            num_bands=lsh_num_bands,
            rows_per_band=minhash_num_perm // lsh_num_bands
        )
        
        self.task_index: Dict[str, Dict[str, Any]] = {}
        self.tfidf_fitted = False
    
    def add_task(self, task_id: str, task_description: str, metadata: Optional[Dict[str, Any]] = None) -> None:
        self.task_index[task_id] = {
            "description": task_description,
            "metadata": metadata or {}
        }
        
        if self.method in [SimilarityMethod.MINHASH, SimilarityMethod.LSH, SimilarityMethod.HYBRID]:
            tokens = self.minhasher.tokenize(task_description)
            signature = self.minhasher.compute_signature(tokens)
            self.task_index[task_id]["minhash_signature"] = signature
            
            if self.method in [SimilarityMethod.LSH, SimilarityMethod.HYBRID]:
                self.lsh.add(task_id, signature)
        
        if self.method in [SimilarityMethod.TFIDF, SimilarityMethod.HYBRID]:
            if self.tfidf_fitted:
                vector = self.tfidf.transform(task_description)
                self.task_index[task_id]["tfidf_vector"] = vector
    
    def fit_tfidf(self) -> None:
        if self.method not in [SimilarityMethod.TFIDF, SimilarityMethod.HYBRID]:
            return
        
        descriptions = [task["description"] for task in self.task_index.values()]
        
        if descriptions:
            self.tfidf.fit(descriptions)
            self.tfidf_fitted = True
            
            for task_id, task_data in self.task_index.items():
                vector = self.tfidf.transform(task_data["description"])
                task_data["tfidf_vector"] = vector
    
    def find_similar(
        self,
        query_description: str,
        k: int = 5,
        threshold: float = 0.5
    ) -> List[Tuple[str, float]]:
        if self.method == SimilarityMethod.TFIDF:
            return self._find_similar_tfidf(query_description, k, threshold)
        
        elif self.method == SimilarityMethod.MINHASH:
            return self._find_similar_minhash(query_description, k, threshold)
        
        elif self.method == SimilarityMethod.LSH:
            return self._find_similar_lsh(query_description, k, threshold)
        
        elif self.method == SimilarityMethod.HYBRID:
            return self._find_similar_hybrid(query_description, k, threshold)
        
        return []
    
    def _find_similar_tfidf(
        self,
        query_description: str,
        k: int,
        threshold: float
    ) -> List[Tuple[str, float]]:
        if not self.tfidf_fitted:
            return []
        
        query_vector = self.tfidf.transform(query_description)
        
        similarities = []
        for task_id, task_data in self.task_index.items():
            if "tfidf_vector" in task_data:
                similarity = self.tfidf.cosine_similarity(query_vector, task_data["tfidf_vector"])
                if similarity >= threshold:
                    similarities.append((task_id, similarity))
        
        similarities.sort(key=lambda x: x[1], reverse=True)
        return similarities[:k]
    
    def _find_similar_minhash(
        self,
        query_description: str,
        k: int,
        threshold: float
    ) -> List[Tuple[str, float]]:
        query_tokens = self.minhasher.tokenize(query_description)
        query_signature = self.minhasher.compute_signature(query_tokens)
        
        similarities = []
        for task_id, task_data in self.task_index.items():
            if "minhash_signature" in task_data:
                similarity = self.minhasher.jaccard_similarity(
                    query_signature,
                    task_data["minhash_signature"]
                )
                if similarity >= threshold:
                    similarities.append((task_id, similarity))
        
        similarities.sort(key=lambda x: x[1], reverse=True)
        return similarities[:k]
    
    def _find_similar_lsh(
        self,
        query_description: str,
        k: int,
        threshold: float
    ) -> List[Tuple[str, float]]:
        query_tokens = self.minhasher.tokenize(query_description)
        query_signature = self.minhasher.compute_signature(query_tokens)
        
        candidates = self.lsh.query_with_scores(query_signature, threshold)
        
        candidates.sort(key=lambda x: x[1], reverse=True)
        return candidates[:k]
    
    def _find_similar_hybrid(
        self,
        query_description: str,
        k: int,
        threshold: float
    ) -> List[Tuple[str, float]]:
        lsh_results = self._find_similar_lsh(query_description, k * 2, threshold * 0.7)
        
        candidate_ids = {task_id for task_id, _ in lsh_results}
        
        if self.tfidf_fitted:
            query_vector = self.tfidf.transform(query_description)
            
            combined_scores = {}
            
            for task_id in candidate_ids:
                task_data = self.task_index[task_id]
                
                minhash_score = next(
                    (score for tid, score in lsh_results if tid == task_id),
                    0.0
                )
                
                tfidf_score = 0.0
                if "tfidf_vector" in task_data:
                    tfidf_score = self.tfidf.cosine_similarity(
                        query_vector,
                        task_data["tfidf_vector"]
                    )
                
                combined_score = 0.6 * tfidf_score + 0.4 * minhash_score
                
                if combined_score >= threshold:
                    combined_scores[task_id] = combined_score
            
            results = sorted(combined_scores.items(), key=lambda x: x[1], reverse=True)
            return results[:k]
        
        else:
            return lsh_results[:k]
    
    def get_task_metadata(self, task_id: str) -> Optional[Dict[str, Any]]:
        if task_id in self.task_index:
            return self.task_index[task_id]["metadata"]
        return None
    
    def remove_task(self, task_id: str) -> None:
        if task_id in self.task_index:
            if self.method in [SimilarityMethod.LSH, SimilarityMethod.HYBRID]:
                self.lsh.remove(task_id)
            
            del self.task_index[task_id]
    
    def get_statistics(self) -> Dict[str, Any]:
        stats = {
            "total_tasks": len(self.task_index),
            "method": self.method.value,
            "tfidf_fitted": self.tfidf_fitted
        }
        
        if self.method in [SimilarityMethod.LSH, SimilarityMethod.HYBRID]:
            stats["lsh_stats"] = self.lsh.get_statistics()
        
        return stats
