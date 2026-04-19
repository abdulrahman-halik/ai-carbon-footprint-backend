from typing import List, Dict, Any
from app.vectorstore.embeddings import embed_texts
from app.services.content_safety_service import contains_sensitive_instruction, sanitize_public_text
from app.vectorstore.store import InMemoryVectorStore

# Single global store for now. In production you would swap this for FAISS/Chroma.
_STORE = InMemoryVectorStore()


def index_documents(docs: List[Dict[str, Any]]) -> Dict[str, Any]:
    """Index documents into the in-memory vector store.

    Each document should be a dict with at least a `text` key and optional `meta`.
    This endpoint is guarded behind authentication at the API layer to avoid abuse.
    """
    approved_docs = []
    for doc in docs:
        raw_text = str(doc.get("text", "") or "")
        if contains_sensitive_instruction(raw_text):
            continue

        sanitized = sanitize_public_text(raw_text, max_length=2000)
        safe_text = sanitized["text"]
        if not safe_text:
            continue

        approved_docs.append({
            "text": safe_text,
            "meta": doc.get("meta", {}),
        })

    if not approved_docs:
        return {"indexed": 0, "rejected": len(docs)}

    texts = [d.get('text', '') for d in approved_docs]
    vectors = embed_texts(texts)
    _STORE.add(approved_docs, vectors)
    return {"indexed": len(approved_docs), "rejected": len(docs) - len(approved_docs)}


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
        sanitized = sanitize_public_text(doc.get('text', ''), max_length=2000)
        text = sanitized['text']
        meta = doc.get('meta', {})
        results.append({"text": text, "meta": meta, "score": h.get('score', 0.0)})
        if text:
            snippets.append(text.strip())

    # Build a concise insight by joining top snippets and trimming length.
    insight = "\n\n".join(snippets)[:2000]

    return {"query": query, "results": results, "insight": insight}
