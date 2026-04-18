from typing import List
import math
import re
import hashlib

try:
    from sentence_transformers import SentenceTransformer
    _HAS_ST = True
    _ST_MODEL = SentenceTransformer('all-MiniLM-L6-v2')
except Exception:
    _HAS_ST = False
    _ST_MODEL = None


def _normalize(text: str) -> str:
    return re.sub(r'\s+', ' ', text.strip().lower())


def embed_texts(texts: List[str], dim: int = 128) -> List[List[float]]:
    """Return embeddings for a list of texts.

    If `sentence-transformers` is available it will be used; otherwise a
    deterministic, auditable fallback (hashed bag-of-words) is used. The
    fallback is suitable for small datasets and testing but not state-of-the-art.
    """
    if _HAS_ST and _ST_MODEL is not None:
        embs = _ST_MODEL.encode(texts, convert_to_numpy=False)
        # ensure lists
        return [list(e) for e in embs]

    out = []
    for t in texts:
        t = _normalize(t)
        words = re.findall(r"\w+", t)
        vec = [0.0] * dim
        for w in words:
            h = int(hashlib.sha256(w.encode('utf-8')).hexdigest(), 16)
            idx = h % dim
            vec[idx] += 1.0
        # L2 normalize
        norm = math.sqrt(sum(x * x for x in vec)) or 1.0
        vec = [x / norm for x in vec]
        out.append(vec)
    return out
