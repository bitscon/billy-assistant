import os
import time
import requests
import numpy as np

QDRANT_URL = os.getenv("QDRANT_URL", "http://qdrant:6333")

COLLECTION_NAME = "billy_memory"

def embed_text(text, dim=384):
    np.random.seed(abs(hash(text)) % (2**32))
    return np.random.uniform(-1, 1, size=dim).tolist()

def create_collection():
    url = f"{QDRANT_URL}/collections/{COLLECTION_NAME}"
    payload = {
        "vectors": {
            "size": 384,
            "distance": "Cosine"
        }
    }
    requests.put(url, json=payload)

def save_memory(text):
    vector = embed_text(text)
    url = f"{QDRANT_URL}/collections/{COLLECTION_NAME}/points"
    payload = {
        "points": [
            {
                "id": int(time.time() * 1000),
                "vector": vector,
                "payload": {
                    "text": text
                }
            }
        ]
    }
    requests.put(url, json=payload)

def search_memory(query_text):
    vector = embed_text(query_text)
    url = f"{QDRANT_URL}/collections/{COLLECTION_NAME}/points/search"
    payload = {
        "vector": vector,
        "limit": 5,
        "with_payload": True
    }
    res = requests.post(url, json=payload)
    if res.status_code == 200:
        return res.json().get("result", [])
    return []
