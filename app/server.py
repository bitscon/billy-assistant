import os
import time
import random
import requests
from flask import Flask, request, jsonify

app = Flask(__name__)

QDRANT_URL = os.getenv("QDRANT_URL", "http://qdrant:6333")
COLLECTION_NAME = "billy_memories"

def ensure_collection():
    res = requests.get(f"{QDRANT_URL}/collections/{COLLECTION_NAME}")
    if res.status_code == 404:
        requests.put(f"{QDRANT_URL}/collections/{COLLECTION_NAME}", json={"vector_size": 768})
    return True

def embed_text(text):
    try:
        res = requests.post(
            os.getenv("OLLAMA_URL", "http://localhost:11434/api/embeddings"),
            json={"model": "nomic-embed-text", "prompt": text}
        )
        res.raise_for_status()
        return res.json()["embedding"]
    except Exception as e:
        print(f"❌ Embedding error: {e}")
        return None

def save_memory(text):
    ensure_collection()
    vector = embed_text(text)
    if not vector:
        print("❌ Embedding failed or empty.")
        return False
    payload = {"text": text}
    doc = {
        "id": int(time.time() * 1000),
        "vector": vector,
        "payload": payload
    }
    try:
        res = requests.put(
            f"{QDRANT_URL}/collections/{COLLECTION_NAME}/points",
            json={"points": [doc]}
        )
        res.raise_for_status()
        return True
    except requests.exceptions.RequestException as e:
        print(f"❌ Error saving to Qdrant: {e}")
        print(f"Response content: {res.content}")
        return False

def search_memory(query):
    try:
        ensure_collection()
        res = requests.post(
            f"{QDRANT_URL}/collections/{COLLECTION_NAME}/points/scroll",
            json={"limit": 50}
        )
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
