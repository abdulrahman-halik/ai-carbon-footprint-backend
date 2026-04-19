from typing import List, Dict, Any
import math


class InMemoryVectorStore:
    def __init__(self):
        self._vectors: List[List[float]] = []
        self._docs: List[Dict[str, Any]] = []

    def add(self, docs: List[Dict[str, Any]], vectors: List[List[float]]):
        for doc, vec in zip(docs, vectors):
            self._docs.append(doc)
            self._vectors.append(vec)

    def _cosine(self, a: List[float], b: List[float]) -> float:
        dot = sum(x * y for x, y in zip(a, b))
        na = math.sqrt(sum(x * x for x in a)) or 1.0
        nb = math.sqrt(sum(y * y for y in b)) or 1.0
        return dot / (na * nb)

    def search(self, query_vector: List[float], top_k: int = 5):
        scores = []
        for i, v in enumerate(self._vectors):
            try:
                sc = self._cosine(query_vector, v)
            except Exception:
                sc = 0.0
            scores.append((i, sc))
        scores.sort(key=lambda x: x[1], reverse=True)
        results = []
        for idx, score in scores[:top_k]:
            results.append({"doc": self._docs[idx], "score": float(score)})
        return results

    def clear(self):
        self._vectors.clear()
        self._docs.clear()
