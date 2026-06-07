from typing import List, Dict, Any
from app.vectorstore.embeddings import embed_texts
from app.vectorstore.store import InMemoryVectorStore

# Single global store for now. In production you would swap this for FAISS/Chroma.
_STORE = InMemoryVectorStore()

DEFAULT_INSIGHTS = [
    {
        "text": "To reduce your carbon footprint, focus on small, consistent changes. You can significantly reduce emissions by commuting with public transport, biking, or walking instead of driving.",
        "meta": {"category": "transport"}
    },
    {
        "text": "Food choices matter. Switching to a plant-based diet or replacing high-footprint meats with vegetarian options a few times a week effectively reduces your carbon emissions.",
        "meta": {"category": "diet"}
    },
    {
        "text": "Improve home energy efficiency to cut your footprint. Use smart stats, LED light bulbs, monitor your AC usage, and switch off appliances when not in use. Consider renewable energy if possible.",
        "meta": {"category": "energy"}
    },
    {
        "text": "Conserving water helps reduce energy used for heating and processing. Fix leaks, take shorter showers, and run full loads in washing machines.",
        "meta": {"category": "water"}
    },
    {
        "text": "Reduce, reuse, recycle. Managing your waste properly by recycling plastic, glass, and paper, and composting food waste minimizes landfill methane emissions.",
        "meta": {"category": "waste"}
    }
]

def _seed_store_if_empty():
    # Only need to do this statically for the in-memory store
    texts = [d['text'] for d in DEFAULT_INSIGHTS]
    vectors = embed_texts(texts)
    _STORE.add(DEFAULT_INSIGHTS, vectors)

_seed_store_if_empty()


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
