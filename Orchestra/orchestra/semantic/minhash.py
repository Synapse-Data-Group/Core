import hashlib
from typing import List, Set


class MinHasher:
    def __init__(self, num_perm: int = 128):
        self.num_perm = num_perm
        self._hash_functions = self._generate_hash_functions()
    
    def _generate_hash_functions(self) -> List:
        hash_funcs = []
        for i in range(self.num_perm):
            seed = i
            hash_funcs.append(lambda x, s=seed: int(hashlib.md5(f"{x}_{s}".encode()).hexdigest(), 16))
        return hash_funcs
    
    def compute_signature(self, tokens: Set[str]) -> List[int]:
        if not tokens:
            return [0] * self.num_perm
        
        signature = []
        
        for hash_func in self._hash_functions:
            min_hash = min(hash_func(token) for token in tokens)
            signature.append(min_hash)
        
        return signature
    
    def jaccard_similarity(self, sig1: List[int], sig2: List[int]) -> float:
        if len(sig1) != len(sig2):
            return 0.0
        
        matches = sum(1 for a, b in zip(sig1, sig2) if a == b)
        return matches / len(sig1)
    
    def tokenize(self, text: str, n: int = 3) -> Set[str]:
        text = text.lower()
        
        for char in '.,!?;:()[]{}"\'-_/\\':
            text = text.replace(char, ' ')
        
        words = text.split()
        
        shingles = set()
        for word in words:
            if len(word) >= n:
                for i in range(len(word) - n + 1):
                    shingles.add(word[i:i+n])
        
        for i in range(len(words) - 1):
            bigram = f"{words[i]}_{words[i+1]}"
            shingles.add(bigram)
        
        return shingles
