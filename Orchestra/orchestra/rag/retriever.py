from typing import Any, Dict, List, Optional
from abc import ABC, abstractmethod
from .vector_store import VectorStore
from .embeddings import EmbeddingFunction
from ..documents.document import Document


class Retriever(ABC):
    @abstractmethod
    def retrieve(self, query: str, k: int = 4, **kwargs) -> List[Document]:
        pass


class VectorRetriever(Retriever):
    def __init__(
        self,
        vector_store: VectorStore,
        embedding_function: EmbeddingFunction,
        score_threshold: Optional[float] = None
    ):
        self.vector_store = vector_store
        self.embedding_function = embedding_function
        self.score_threshold = score_threshold
    
    def retrieve(
        self,
        query: str,
        k: int = 4,
        filter_dict: Optional[Dict[str, Any]] = None,
        **kwargs
    ) -> List[Document]:
        query_embedding = self.embedding_function.embed_text(query)
        
        results = self.vector_store.similarity_search(
            query_embedding,
            k=k,
            filter_dict=filter_dict
        )
        
        if self.score_threshold is not None:
            results = [(doc, score) for doc, score in results if score >= self.score_threshold]
        
        return [doc for doc, score in results]
    
    def retrieve_with_scores(
        self,
        query: str,
        k: int = 4,
        filter_dict: Optional[Dict[str, Any]] = None,
        **kwargs
    ) -> List[tuple]:
        query_embedding = self.embedding_function.embed_text(query)
        
        results = self.vector_store.similarity_search(
            query_embedding,
            k=k,
            filter_dict=filter_dict
        )
        
        if self.score_threshold is not None:
            results = [(doc, score) for doc, score in results if score >= self.score_threshold]
        
        return results


class HybridRetriever(Retriever):
    def __init__(
        self,
        vector_retriever: VectorRetriever,
        keyword_weight: float = 0.5,
        vector_weight: float = 0.5
    ):
        self.vector_retriever = vector_retriever
        self.keyword_weight = keyword_weight
        self.vector_weight = vector_weight
    
    def retrieve(
        self,
        query: str,
        k: int = 4,
        **kwargs
    ) -> List[Document]:
        vector_results = self.vector_retriever.retrieve_with_scores(query, k=k * 2)
        
        keyword_results = self._keyword_search(query, k=k * 2)
        
        combined_scores = {}
        
        for doc, score in vector_results:
            doc_key = id(doc)
            combined_scores[doc_key] = {
                "doc": doc,
                "vector_score": score,
                "keyword_score": 0.0
            }
        
        for doc, score in keyword_results:
            doc_key = id(doc)
            if doc_key in combined_scores:
                combined_scores[doc_key]["keyword_score"] = score
            else:
                combined_scores[doc_key] = {
                    "doc": doc,
                    "vector_score": 0.0,
                    "keyword_score": score
                }
        
        final_results = []
        for doc_key, scores in combined_scores.items():
            final_score = (
                scores["vector_score"] * self.vector_weight +
                scores["keyword_score"] * self.keyword_weight
            )
            final_results.append((scores["doc"], final_score))
        
        final_results.sort(key=lambda x: x[1], reverse=True)
        
        return [doc for doc, score in final_results[:k]]
    
    def _keyword_search(self, query: str, k: int) -> List[tuple]:
        query_terms = set(query.lower().split())
        
        all_docs = self.vector_retriever.vector_store.documents.values()
        
        scored_docs = []
        for doc in all_docs:
            doc_terms = set(doc.content.lower().split())
            overlap = len(query_terms.intersection(doc_terms))
            
            if overlap > 0:
                score = overlap / len(query_terms)
                scored_docs.append((doc, score))
        
        scored_docs.sort(key=lambda x: x[1], reverse=True)
        return scored_docs[:k]
