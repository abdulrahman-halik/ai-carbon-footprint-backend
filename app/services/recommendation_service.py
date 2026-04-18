from typing import List, Dict, Any
from app.vectorstore.embeddings import embed_texts
from app.vectorstore.store import InMemoryVectorStore

# Single global store for now. In production you would swap this for FAISS/Chroma.
_STORE = InMemoryVectorStore()


def index_documents(docs: List[Dict[str, Any]]) -> Dict[str, Any]:
    """Index documents into the in-memory vector store.

    Each document should be a dict with at least a `text` key and optional `meta`.
    This endpoint is guarded behind authentication at the API layer to avoid abuse.
    """
    texts = [d.get('text', '') for d in docs]
    vectors = embed_texts(texts)
    _STORE.add(docs, vectors)
    return {"indexed": len(docs)}


def search_insights(query: str, top_k: int = 3) -> Dict[str, Any]:
    """Search the indexed documents and return helpful snippets and an assembled insight.

    This method intentionally avoids calling external LLMs; it provides an extractive
    aggregation of the top matching documents which can be safely shown to users.
    """
    if not query or not query.strip():
        return {"query": query, "results": [], "insight": ""}

    qvec = embed_texts([query])[0]
    hits = _STORE.search(qvec, top_k=top_k)

    results = []
    snippets = []
    for h in hits:
        doc = h.get('doc', {})
        text = doc.get('text', '')
        meta = doc.get('meta', {})
        results.append({"text": text, "meta": meta, "score": h.get('score', 0.0)})
        if text:
            snippets.append(text.strip())

    # Build a concise insight by joining top snippets and trimming length.
    insight = "\n\n".join(snippets)[:2000]

    return {"query": query, "results": results, "insight": insight}
