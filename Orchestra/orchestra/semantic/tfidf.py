import math
from typing import Dict, List, Set
from collections import Counter


class TFIDFVectorizer:
    def __init__(self, max_features: int = 1000, min_df: int = 1):
        self.max_features = max_features
        self.min_df = min_df
        
        self.vocabulary: Dict[str, int] = {}
        self.idf: Dict[str, float] = {}
        self.document_count = 0
    
    def fit(self, documents: List[str]) -> None:
        self.document_count = len(documents)
        
        doc_frequencies = Counter()
        
        for doc in documents:
            terms = set(self._tokenize(doc))
            for term in terms:
                doc_frequencies[term] += 1
        
        valid_terms = [
            term for term, freq in doc_frequencies.items()
            if freq >= self.min_df
        ]
        
        if len(valid_terms) > self.max_features:
            valid_terms = sorted(
                valid_terms,
                key=lambda t: doc_frequencies[t],
                reverse=True
            )[:self.max_features]
        
        self.vocabulary = {term: idx for idx, term in enumerate(valid_terms)}
        
        for term in self.vocabulary:
            df = doc_frequencies[term]
            self.idf[term] = math.log((self.document_count + 1) / (df + 1)) + 1
    
    def transform(self, document: str) -> Dict[int, float]:
        terms = self._tokenize(document)
        term_counts = Counter(terms)
        
        total_terms = len(terms)
        
        vector = {}
        
        for term, count in term_counts.items():
            if term in self.vocabulary:
                tf = count / total_terms if total_terms > 0 else 0
                tfidf = tf * self.idf[term]
                vector[self.vocabulary[term]] = tfidf
        
        magnitude = math.sqrt(sum(v * v for v in vector.values()))
        if magnitude > 0:
            vector = {k: v / magnitude for k, v in vector.items()}
        
        return vector
    
    def fit_transform(self, documents: List[str]) -> List[Dict[int, float]]:
        self.fit(documents)
        return [self.transform(doc) for doc in documents]
    
    def _tokenize(self, text: str) -> List[str]:
        text = text.lower()
        
        for char in '.,!?;:()[]{}"\'-_/\\':
            text = text.replace(char, ' ')
        
        tokens = text.split()
        
        stopwords = {
            'a', 'an', 'and', 'are', 'as', 'at', 'be', 'by', 'for', 'from',
            'has', 'he', 'in', 'is', 'it', 'its', 'of', 'on', 'that', 'the',
            'to', 'was', 'will', 'with'
        }
        
        tokens = [t for t in tokens if t not in stopwords and len(t) > 2]
        
        return tokens
    
    def cosine_similarity(self, vec1: Dict[int, float], vec2: Dict[int, float]) -> float:
        common_keys = set(vec1.keys()) & set(vec2.keys())
        
        if not common_keys:
            return 0.0
        
        dot_product = sum(vec1[k] * vec2[k] for k in common_keys)
        
        return dot_product
