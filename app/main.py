import os
import time
import random
import requests
from flask import Flask, request, jsonify

app = Flask(__name__)
qdrant_url = os.getenv("QDRANT_URL", "http://qdrant:6333")
collection_name = "billy_memories"

def embed_text(text):
    # Placeholder: fake embedding vector
    return [random.random() for _ in range(64)]

def ensure_collection():
    try:
        res = requests.get(f"{qdrant_url}/collections/{collection_name}")
        if res.status_code == 404:
            # Create the collection if it doesn't exist
            create_res = requests.put(f"{qdrant_url}/collections/{collection_name}", json={
                "vectors": {
                    "size": 64,
                    "distance": "Cosine"
                }
            })
            return create_res.ok
        return True
    except Exception as e:
        print(f"Error ensuring collection: {e}")
        return False

def save_memory(text):
    if not ensure_collection():
        return False
    vector = embed_text(text)
    doc = {
        "id": int(time.time() * 1000),
        "vector": vector,
        "payload": {"text": text}
    }
    try:
        res = requests.put(f"{qdrant_url}/collections/{collection_name}/points", json={"points": [doc]})
        return res.ok
    except Exception as e:
        print(f"Error saving memory: {e}")
        return False

def search_memory(query):
    if not ensure_collection():
        return {"error": "Cannot ensure collection exists."}
    try:
        res = requests.post(f"{qdrant_url}/collections/{collection_name}/points/scroll", json={"limit": 50})
        if res.status_code != 200:
            return {"error": f"Qdrant scroll error: {res.text}"}
        memories = res.json().get("result", [])
        matches = []
        for memory in memories:
            if isinstance(memory, dict) and query.lower() in memory.get("payload", {}).get("text", "").lower():
                matches.append(memory.get("payload", {}))
        return matches
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

@app.route("/memory/setup", methods=["POST"])
def api_memory_setup():
    if ensure_collection():
        return jsonify({"status": "Memory collection ready"})
    else:
        return jsonify({"error": "Failed to create memory collection"}), 500

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)
