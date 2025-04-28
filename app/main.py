import os
import time
import requests
from flask import Flask, request, jsonify

app = Flask(__name__)
qdrant_url = os.getenv("QDRANT_URL", "http://qdrant:6333")
ollama_url = os.getenv("OLLAMA_URL", "http://localhost:11434")
embedding_model = os.getenv("EMBEDDING_MODEL", "nomic-embed-text")

def embed_text(text):
    """Use Ollama to embed text properly."""
    try:
        payload = {
            "model": embedding_model,
            "prompt": text
        }
        response = requests.post(f"{ollama_url}/api/embeddings", json=payload)
        response.raise_for_status()
        return response.json()["embedding"]
    except Exception as e:
        print(f"Embedding error: {e}")
        return None

def save_memory(text):
    vector = embed_text(text)
    if vector is None:
        return False

    doc = {
        "vector": vector,
        "payload": {"text": text},
        "id": str(int(time.time() * 1000))
    }
    try:
        response = requests.put(
            f"{qdrant_url}/collections/billy_memories/points",
            json={"points": [doc]}
        )
        response.raise_for_status()
        return True
    except Exception as e:
        print(f"Save memory error: {e}")
        return False

def search_memory(query):
    """Perform a vector similarity search."""
    vector = embed_text(query)
    if vector is None:
        return []

    try:
        response = requests.post(
            f"{qdrant_url}/collections/billy_memories/points/search",
            json={
                "vector": vector,
                "limit": 5
            }
        )
        response.raise_for_status()
        results = response.json().get("result", [])
        return [item.get("payload", {}) for item in results]
    except Exception as e:
        print(f"Search error: {e}")
        return []

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
