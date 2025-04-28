import os
import time
import random
import requests
from flask import Flask, request, jsonify

app = Flask(__name__)
qdrant_url = os.getenv("QDRANT_URL", "http://qdrant:6333")
ollama_url = os.getenv("OLLAMA_URL", "http://localhost:11434/api/embeddings")

def embed_text(text):
    try:
        res = requests.post(ollama_url, json={"model": "nomic-embed-text", "prompt": text})
        res.raise_for_status()
        embedding = res.json()["embedding"]
        return embedding
    except Exception as e:
        print(f"Embedding error: {e}")
        return None

def save_memory(text):
    vector = embed_text(text)
    if vector is None:
        print("❌ Failed to get embedding.")
        return False
    payload = {"text": text}
    doc = {
        "vector": vector,
        "payload": payload,
        "id": int(time.time() * 1000)
    }
    try:
        res = requests.put(f"{qdrant_url}/collections/billy_memories/points", json={"points": [doc]})
        res.raise_for_status()
        return True
    except Exception as e:
        print(f"Save memory error: {e}")
        return False

def search_memory(query):
    try:
        res = requests.post(f"{qdrant_url}/collections/billy_memories/points/scroll", json={"limit": 50})
        res.raise_for_status()
        memories = res.json().get("result", [])
        matches = []
        for memory in memories:
            if query.lower() in memory.get("payload", {}).get("text", "").lower():
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

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)
