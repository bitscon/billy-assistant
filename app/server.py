import os
import time
import random
import requests
from flask import Flask, request, jsonify

app = Flask(__name__)

qdrant_url = os.getenv("QDRANT_URL", "http://qdrant:6333")
ollama_url = os.getenv("OLLAMA_URL", "http://192.168.1.112:11434/api/embeddings")
collection_name = "billy_memories"

def ensure_collection():
    """Make sure the memory collection exists."""
    try:
        res = requests.get(f"{qdrant_url}/collections/{collection_name}")
        if res.status_code == 404:
            schema = {
                "vectors": {
                    "size": 768,
                    "distance": "Cosine"
                }
            }
            create = requests.put(f"{qdrant_url}/collections/{collection_name}", json={"vector_size": 768})
            return create.ok
        return True
    except Exception as e:
        print(f"Collection check error: {e}")
        return False

def save_memory(text):
    try:
        # 1. Embed the text
        embed_res = requests.post(ollama_url, json={"model": "nomic-embed-text", "prompt": text})
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
            print("❌ Failed to ensure collection.")
            return False

        # 4. Save memory to Qdrant
        save_res = requests.put(f"{qdrant_url}/collections/{collection_name}/points", json=payload)
        save_res.raise_for_status()
        return True
    except Exception as e:
        print(f"Save memory error: {e}")
        return False

def search_memory(query):
    """Simple scroll and search text match."""
    try:
        res = requests.post(f"{qdrant_url}/collections/{collection_name}/points/scroll", json={"limit": 50})
        res.raise_for_status()
        points = res.json().get("result", [])
        matches = []
        for point in points:
            text = point.get("payload", {}).get("text", "")
            if query.lower() in text.lower():
                matches.append(text)
        return matches[:3]
    except Exception as e:
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
