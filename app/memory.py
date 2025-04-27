import os
import random
import time
from qdrant_client import QdrantClient
from qdrant_client.models import PointStruct, VectorParams, Distance

QDRANT_URL = os.getenv("QDRANT_URL", "http://qdrant:6333")
COLLECTION_NAME = "billy_memories"

# Connect to Qdrant
qdrant = QdrantClient(url=QDRANT_URL)

# Ensure collection exists
def ensure_collection():
    if COLLECTION_NAME not in [c.name for c in qdrant.get_collections().collections]:
        qdrant.recreate_collection(
            collection_name=COLLECTION_NAME,
            vectors_config=VectorParams(size=64, distance=Distance.COSINE),
        )

# Embed text (fake embedder for now)
def embed(text):
    return [random.random() for _ in range(64)]

# Save memory
def save_memory(text):
    ensure_collection()
    vector = embed(text)
    point = PointStruct(
        id=int(time.time() * 1000),
        vector=vector,
        payload={"text": text}
    )
    qdrant.upsert(collection_name=COLLECTION_NAME, points=[point])
    return True

# Search memory
def search_memory(query):
    ensure_collection()
    vector = embed(query)
    hits = qdrant.search(
        collection_name=COLLECTION_NAME,
        query_vector=vector,
        limit=5,
        with_payload=True
    )
    return [hit.payload for hit in hits]
