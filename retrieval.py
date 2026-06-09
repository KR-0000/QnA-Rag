"""
retrieval.py
Hybrid search: semantic (ChromaDB) + keyword (BM25) fused via Reciprocal Rank Fusion.
"""

import os
import glob
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_core.documents import Document
from sentence_transformers import SentenceTransformer
import chromadb
from rank_bm25 import BM25Okapi

CHROMA_PATH = "chroma_db"
COLLECTION_NAME = "rutgers_cs"
EMBED_MODEL = "all-MiniLM-L6-v2"
TOP_K = 5
RRF_K = 60  # RRF constant; higher = smoother rank blending

_model = None
_collection = None
_bm25 = None
_bm25_corpus: list[str] = []
_bm25_meta: list[dict] = []


def _get_model() -> SentenceTransformer:
    global _model
    if _model is None:
        _model = SentenceTransformer(EMBED_MODEL)
    return _model


def _get_collection():
    global _collection
    if _collection is None:
        client = chromadb.PersistentClient(path=CHROMA_PATH)
        _collection = client.get_collection(COLLECTION_NAME)
    return _collection


def _get_bm25():
    """Build BM25 index from all documents in ChromaDB."""
    global _bm25, _bm25_corpus, _bm25_meta
    if _bm25 is not None:
        return _bm25, _bm25_corpus, _bm25_meta

    collection = _get_collection()
    # Fetch all stored chunks
    result = collection.get(include=["documents", "metadatas"])
    _bm25_corpus = result["documents"]
    _bm25_meta = result["metadatas"]

    tokenized = [doc.lower().split() for doc in _bm25_corpus]
    _bm25 = BM25Okapi(tokenized)
    return _bm25, _bm25_corpus, _bm25_meta


def _semantic_search(query: str, k: int) -> list[dict]:
    """Return top-k chunks by cosine similarity."""
    model = _get_model()
    collection = _get_collection()
    query_embedding = model.encode([query]).tolist()
    results = collection.query(
        query_embeddings=query_embedding,
        n_results=min(k, collection.count()),
        include=["documents", "metadatas", "distances"],
    )
    hits = []
    for doc, meta, dist in zip(
        results["documents"][0],
        results["metadatas"][0],
        results["distances"][0],
    ):
        hits.append({"text": doc, "source": meta.get("source", "unknown"), "score": dist})
    return hits


def _bm25_search(query: str, k: int) -> list[dict]:
    """Return top-k chunks by BM25 keyword score."""
    bm25, corpus, metas = _get_bm25()
    tokenized_query = query.lower().split()
    scores = bm25.get_scores(tokenized_query)
    top_indices = sorted(range(len(scores)), key=lambda i: scores[i], reverse=True)[:k]
    hits = []
    for idx in top_indices:
        hits.append({
            "text": corpus[idx],
            "source": metas[idx].get("source", "unknown"),
            "score": float(scores[idx]),
        })
    return hits


def _reciprocal_rank_fusion(
    semantic_hits: list[dict],
    bm25_hits: list[dict],
    k: int = RRF_K,
) -> list[dict]:
    """Merge two ranked lists using Reciprocal Rank Fusion."""
    scores: dict[str, float] = {}
    data: dict[str, dict] = {}

    for rank, hit in enumerate(semantic_hits):
        key = hit["text"]
        scores[key] = scores.get(key, 0) + 1.0 / (k + rank + 1)
        data[key] = hit

    for rank, hit in enumerate(bm25_hits):
        key = hit["text"]
        scores[key] = scores.get(key, 0) + 1.0 / (k + rank + 1)
        data[key] = hit

    ranked = sorted(scores.items(), key=lambda x: x[1], reverse=True)
    result = []
    for text, rrf_score in ranked:
        entry = dict(data[text])
        entry["rrf_score"] = rrf_score
        result.append(entry)
    return result


def retrieve(query: str, top_k: int = TOP_K) -> list[dict]:
    """
    Hybrid retrieval: semantic + BM25 fused with RRF.
    Returns list of dicts with keys: text, source, rrf_score
    """
    fetch_k = top_k * 3  # fetch more than needed before fusion
    semantic_hits = _semantic_search(query, fetch_k)
    bm25_hits = _bm25_search(query, fetch_k)
    fused = _reciprocal_rank_fusion(semantic_hits, bm25_hits)
    return fused[:top_k]


if __name__ == "__main__":
    test_queries = [
        "What is the minimum score needed to pass CS 112?",
        "Which professor should I take for algorithms CS 344?",
        "How hard is systems programming compared to computer architecture?",
    ]
    for q in test_queries:
        print(f"\nQuery: {q}")
        hits = retrieve(q)
        for i, hit in enumerate(hits):
            print(f"  [{i+1}] source={hit['source']}  rrf={hit['rrf_score']:.4f}")
            print(f"       {hit['text'][:200]}")