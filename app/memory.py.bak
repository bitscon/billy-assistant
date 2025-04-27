from qdrant_client import QdrantClient
from qdrant_client.models import PointStruct
import os

QDRANT_URL = os.getenv("QDRANT_URL", "http://qdrant:6333")
COLLECTION_NAME = "billy_memory"

client = QdrantClient(url=QDRANT_URL)

def ensure_collection():
    if COLLECTION_NAME not in client.get_collections().collections:
        client.recreate_collection(
            collection_name=COLLECTION_NAME,
            vectors_config={"size": 1536, "distance": "Cosine"}
        )

def save_memory(id, vector, payload):
    ensure_collection()
    client.upsert(
        collection_name=COLLECTION_NAME,
        points=[PointStruct(id=id, vector=vector, payload=payload)]
    )

def search_memory(query_vector, limit=5):
    ensure_collection()
    results = client.search(
        collection_name=COLLECTION_NAME,
        query_vector=query_vector,
        limit=limit
    )
    return results
