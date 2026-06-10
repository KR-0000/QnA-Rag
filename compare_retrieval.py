"""
compare_retrieval.py
Run this once to generate comparison output for the README.
Prints top-3 results for each method on 3 queries.
"""

from sentence_transformers import SentenceTransformer
import chromadb
from rank_bm25 import BM25Okapi

CHROMA_PATH = "chroma_db"
COLLECTION_NAME = "rutgers_cs"
EMBED_MODEL = "all-MiniLM-L6-v2"

model = SentenceTransformer(EMBED_MODEL)
client = chromadb.PersistentClient(path=CHROMA_PATH)
collection = client.get_collection(COLLECTION_NAME)

all_data = collection.get(include=["documents", "metadatas"])
corpus = all_data["documents"]
metas = all_data["metadatas"]
tokenized = [doc.lower().split() for doc in corpus]
bm25 = BM25Okapi(tokenized)

QUERIES = [
    "What is the minimum score needed to pass CS 112?",
    "Which professor should I take for CS 344?",
    "What are the easiest CS electives?",
]

RRF_K = 60


def semantic(query, k=3):
    emb = model.encode([query]).tolist()
    res = collection.query(query_embeddings=emb, n_results=k,
                           include=["documents", "metadatas", "distances"])
    return [(res["documents"][0][i], res["metadatas"][0][i]["source"],
             res["distances"][0][i]) for i in range(k)]


def bm25_search(query, k=3):
    scores = bm25.get_scores(query.lower().split())
    top = sorted(range(len(scores)), key=lambda i: scores[i], reverse=True)[:k]
    return [(corpus[i], metas[i]["source"], float(scores[i])) for i in top]


def hybrid(query, k=3):
    sem = semantic(query, k * 3)
    bm = bm25_search(query, k * 3)
    rrf: dict[str, float] = {}
    data: dict[str, tuple] = {}
    for rank, (text, src, score) in enumerate(sem):
        rrf[text] = rrf.get(text, 0) + 1 / (RRF_K + rank + 1)
        data[text] = (text, src, score)
    for rank, (text, src, score) in enumerate(bm):
        rrf[text] = rrf.get(text, 0) + 1 / (RRF_K + rank + 1)
        data[text] = (text, src, score)
    ranked = sorted(rrf.items(), key=lambda x: x[1], reverse=True)[:k]
    return [(data[t][0], data[t][1], rrf_score) for t, rrf_score in ranked]


for query in QUERIES:
    print(f"\n{'='*70}")
    print(f"QUERY: {query}")

    print("\n--- SEMANTIC ONLY ---")
    for i, (text, src, score) in enumerate(semantic(query)):
        print(f"  [{i+1}] {src} (distance: {score:.4f})")
        print(f"       {text[:180].strip()}")

    print("\n--- BM25 ONLY ---")
    for i, (text, src, score) in enumerate(bm25_search(query)):
        print(f"  [{i+1}] {src} (score: {score:.4f})")
        print(f"       {text[:180].strip()}")

    print("\n--- HYBRID (RRF) ---")
    for i, (text, src, score) in enumerate(hybrid(query)):
        print(f"  [{i+1}] {src} (rrf: {score:.4f})")
        print(f"       {text[:180].strip()}")