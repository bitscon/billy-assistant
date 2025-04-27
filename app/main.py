import os
import time
import requests
import numpy as np
from flask import Flask, request, jsonify
from sentence_transformers import SentenceTransformer

app = Flask(__name__)
qdrant_url = os.getenv("QDRANT_URL", "http://qdrant:6333")

# 🧠 Load real embedding model
embedder = SentenceTransformer('all-MiniLM-L6-v2')

def embed_text(text):
    # Use real sentence embeddings
    return embedder.encode(text).tolist()

def save_memory(text):
    vector = embed_text(text)
    payload = {"text": text}
    doc = {
        "vector": vector,
        "payload": payload,
        "id": int(time.time() * 1000)
    }
    res = requests.put(f"{qdrant_url}/collections/billy_memories/points", json={"points": [doc]})
    return res.ok

def search_memory(query, top_k=5):
    try:
        query_vector = embed_text(query)
        res = requests.post(f"{qdrant_url}/collections/billy_memories/points/search", json={
            "vector": query_vector,
            "limit": top_k
        })
        matches = res.json().get("result", [])
        return [match.get("payload", {}) for match in matches]
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
