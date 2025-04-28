import os
import time
import random
import requests
from flask import Flask, request, jsonify

app = Flask(__name__)

QDRANT_URL = os.getenv("QDRANT_URL", "http://qdrant:6333")
OLLAMA_URL = os.getenv("OLLAMA_URL", "http://192.168.1.112:11434/api/embeddings")
COLLECTION_NAME = "billy_memories"

def ensure_collection():
    """Make sure the memory collection exists."""
    try:
        res = requests.get(f"{QDRANT_URL}/collections/{COLLECTION_NAME}")
        if res.status_code == 404:
            schema = {
                "vectors": {
                    "size": 768,
                    "distance": "Cosine"
                }
            }
            create = requests.put(f"{QDRANT_URL}/collections/{COLLECTION_NAME}", json={"vector_size": 768})
            return create.ok
        return True
    except Exception as e:
        print(f"[Error] Collection check error: {e}")
        return False

def save_memory(text):
    try:
        # 1. Embed the text
        embed_res = requests.post(OLLAMA_URL, json={"model": "nomic-embed-text", "prompt": text})
        embed_res.raise_for_status()
        embedding = embed_res.json()["embedding"]

        # 2. Build payload
        payload = {
            "points": [
                {
                    "id": int(time.time() * 1000),
                    "vector": embedding,
                    "payload": {
                        "text": text
                    }
                }
            ]
        }

        # 3. Ensure collection exists
        if not ensure_collection():
            print("[Error] ❌ Failed to ensure collection.")
            return False

        # 4. Save memory to Qdrant
        save_res = requests.put(f"{QDRANT_URL}/collections/{COLLECTION_NAME}/points", json=payload)
        save_res.raise_for_status()
        return True
    except Exception as e:
        print(f"[Error] Save memory error: {e}")
        return False

def search_memory(query):
    """Search Billy's memories for matching text."""
    try:
        ensure_collection()
        res = requests.post(
            f"{QDRANT_URL}/collections/{COLLECTION_NAME}/points/scroll",
            json={"limit": 50}
        )
        res.raise_for_status()
        data = res.json()
        points = data.get("result", [])

        matches = []
        for point in points:
            text = point.get("payload", {}).get("text", "")
            if query.lower() in text.lower():
                matches.append(text)
        return matches[:3]
    except Exception as e:
        print(f"[Error] Search memory error: {e}")
        return {"error": str(e)}

@app.route("/", methods=["GET"])
def home():
    return "Good day, Chad. How may I assist you?"

@app.route("/memory/save", methods=["POST"])
def api_save_memory():
    text = request.json.get("text")
    if not text:
        return jsonify({"error": "Missing text"}), 400
    if save_memory(text):
        return jsonify({"status": "Memory saved"})
    else:
        return jsonify({"error": "Failed to save memory"}), 500

@app.route("/memory/search", methods=["POST"])
def api_search_memory():
    query = request.json.get("query")
    if not query:
        return jsonify({"error": "Missing query"}), 400
    results = search_memory(query)
    return jsonify(results)

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)