"""
ingest.py
Load, chunk, embed, and store all documents in ChromaDB.
Run this once before starting the app: python ingest.py
"""

import os
import glob
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_core.documents import Document
from sentence_transformers import SentenceTransformer
import chromadb

DOCUMENTS_DIR = "documents"
CHROMA_PATH = "chroma_db"
COLLECTION_NAME = "rutgers_cs"
CHUNK_SIZE = 500
CHUNK_OVERLAP = 100
EMBED_MODEL = "all-MiniLM-L6-v2"


def load_documents(directory: str) -> list[Document]:
    docs = []
    paths = glob.glob(os.path.join(directory, "*.txt"))
    if not paths:
        raise FileNotFoundError(f"No .txt files found in '{directory}'")
    for path in sorted(paths):
        with open(path, "r", encoding="utf-8") as f:
            text = f.read()
        source = os.path.basename(path)
        docs.append(Document(page_content=text, metadata={"source": source}))
        print(f"  Loaded: {source} ({len(text)} chars)")
    return docs


def chunk_documents(docs: list[Document]) -> list[Document]:
    splitter = RecursiveCharacterTextSplitter(
        chunk_size=CHUNK_SIZE,
        chunk_overlap=CHUNK_OVERLAP,
        separators=["\n\n", "\n", ". ", " ", ""],
    )
    chunks = []
    for doc in docs:
        split = splitter.split_documents([doc])
        for i, chunk in enumerate(split):
            chunk.metadata["chunk_index"] = i
        chunks.extend(split)
    return chunks


def embed_and_store(chunks: list[Document]) -> None:
    print(f"\nEmbedding {len(chunks)} chunks with {EMBED_MODEL}...")
    model = SentenceTransformer(EMBED_MODEL)
    texts = [c.page_content for c in chunks]
    embeddings = model.encode(texts, show_progress_bar=True, batch_size=64)

    client = chromadb.PersistentClient(path=CHROMA_PATH)

    # Delete existing collection so re-runs start fresh
    try:
        client.delete_collection(COLLECTION_NAME)
    except Exception:
        pass

    collection = client.create_collection(
        name=COLLECTION_NAME,
        metadata={"hnsw:space": "cosine"},
    )

    ids = [f"chunk_{i}" for i in range(len(chunks))]
    metadatas = [c.metadata for c in chunks]

    collection.add(
        ids=ids,
        embeddings=embeddings.tolist(),
        documents=texts,
        metadatas=metadatas,
    )
    print(f"Stored {len(chunks)} chunks in ChromaDB at '{CHROMA_PATH}'")


def print_sample_chunks(chunks: list[Document], n: int = 5) -> None:
    import random
    print(f"\n--- {n} sample chunks ---")
    for chunk in random.sample(chunks, min(n, len(chunks))):
        print(f"\nSource: {chunk.metadata['source']}")
        print(f"Length: {len(chunk.page_content)} chars")
        print(chunk.page_content[:300])
        print("...")


if __name__ == "__main__":
    print("=== Ingestion pipeline ===\n")
    print("Loading documents...")
    docs = load_documents(DOCUMENTS_DIR)
    print(f"\nLoaded {len(docs)} documents")

    print("\nChunking...")
    chunks = chunk_documents(docs)
    print(f"Produced {len(chunks)} chunks")

    print_sample_chunks(chunks)

    embed_and_store(chunks)
    print("\nIngestion complete.")