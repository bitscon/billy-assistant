import os
import logging
import uuid
from typing import Dict, List, Union
import requests
from flask import Flask, jsonify, request
from flask_cors import CORS
from flask_jwt_extended import JWTManager, jwt_required, create_access_token
from flask_limiter import Limiter
from flask_limiter.util import get_remote_address

app = Flask(__name__)
app.config["JWT_SECRET_KEY"] = os.getenv("JWT_SECRET_KEY", str(uuid.uuid4()))  # Secure key in prod
CORS(app, resources={r"/api/*": {"origins": "*"}})  # Restrict in prod
jwt = JWTManager(app)
limiter = Limiter(app, key_func=get_remote_address, default_limits=["200 per day", "50 per hour"])

qdrant_url = os.getenv("QDRANT_URL", "http://qdrant:6333")
ollama_url = os.getenv("OLLAMA_URL", "http://ollama:11434")
collection_name = os.getenv("COLLECTION_NAME", "billy_memories")
embedding_model = os.getenv("EMBEDDING_MODEL", "nomic-embed-text")
chat_model = os.getenv("CHAT_MODEL", "llama3")
vector_size = int(os.getenv("VECTOR_SIZE", 768))

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def ensure_collection() -> bool:
    """Ensure Qdrant collection exists."""
    try:
        res = requests.get(f"{qdrant_url}/collections/{collection_name}")
        if res.status_code == 404:
            schema = {"vectors": {"size": vector_size, "distance": "Cosine"}}
            create = requests.put(f"{qdrant_url}/collections/{collection_name}", json=schema)
            if not create.ok:
                logger.error(f"Collection creation failed: {create.text} (status: {create.status_code})")
                return False
        elif not res.ok:
            logger.error(f"Collection check failed: {res.text} (status: {res.status_code})")
            return False
        return True
    except requests.RequestException as e:
        logger.error(f"Collection error: {e}")
        return False

def embed_text(text: str) -> Union[List[float], None]:
    """Generate text embedding using Ollama."""
    try:
        res = requests.post(
            f"{ollama_url}/api/embeddings",
            json={"model": embedding_model, "prompt": text},
            timeout=10
        )
        res.raise_for_status()
        embedding = res.json().get("embedding")
        if not embedding or not isinstance(embedding, list):
            logger.error("Invalid embedding response")
            return None
        return embedding
    except requests.RequestException as e:
        logger.error(f"Embedding error: {e}")
        return None

def save_memory(text: str) -> bool:
    """Save a memory into Qdrant."""
    if not isinstance(text, str) or len(text) > 1000:
        logger.error("Invalid text input")
        return False
    vector = embed_text(text)
    if vector is None:
        logger.error("Failed to generate embedding")
        return False
    doc = {"points": [{"id": str(uuid.uuid4()), "vector": vector, "payload": {"text": text}}]}
    try:
        res = requests.put(
            f"{qdrant_url}/collections/{collection_name}/points",
            json=doc,
            timeout=10
        )
        res.raise_for_status()
        return True
    except requests.RequestException as e:
        logger.error(f"Save error: {e}")
        return False

def search_memory(query: str, limit: int = 5) -> Union[List[str], Dict[str, str]]:
    """Find relevant memories using vector search."""
    try:
        vector = embed_text(query)
        if vector is None:
            return {"error": "Failed to generate embedding"}
        res = requests.post(
            f"{qdrant_url}/collections/{collection_name}/points/search",
            json={"vector": vector, "limit": limit, "with_payload": True},
            timeout=10
        )
        res.raise_for_status()
        return [p["payload"]["text"] for p in res.json().get("result", []) if "payload" in p and "text" in p["payload"]]
    except requests.RequestException as e:
        logger.error(f"Search error: {e}")
        return {"error": str(e)}

def error_response(message: str, status: int) -> tuple:
    """Create a standardized error response."""
    return jsonify({"error": message}), status

@app.before_first_request
def initialize():
    """Initialize Qdrant collection."""
    if not ensure_collection():
        raise RuntimeError("Failed to initialize Qdrant")

@app.route("/", methods=["GET"])
def home() -> str:
    """Root endpoint."""
    return "Good day, Chad. Billy is online."

@app.route("/api/token", methods=["POST"])
@limiter.limit("5 per minute")
def get_token() -> tuple:
    """Generate a JWT token."""
    data = request.json
    username = data.get("username")
    password = data.get("password")
    if not username or not password or username != "chad" or password != os.getenv("USER_PASSWORD", "secure-password-123"):
        return error_response("Unauthorized", 401)
    token = create_access_token(identity=username)
    return jsonify({"access_token": token}), 200

@app.route("/api/memory/save", methods=["POST"])
@jwt_required()
@limiter.limit("10 per minute")
def api_save_memory() -> tuple:
    """Save a memory."""
    data = request.json
    if not data or not isinstance(data.get("text"), str):
        return error_response("Missing or invalid text", 400)
    if save_memory(data["text"]):
        return jsonify({"status": "Memory saved"}), 200
    return error_response("Failed to save memory", 500)

@app.route("/api/memory/search", methods=["POST"])
@jwt_required()
@limiter.limit("20 per minute")
def api_search_memory() -> tuple:
    """Search for memories."""
    data = request.json
    if not data or not isinstance(data.get("query"), str):
        return error_response("Missing or invalid query", 400)
    results = search_memory(data["query"])
    if isinstance(results, dict):
        return error_response(results.get("error", "Search failed"), 500)
    return jsonify({"results": results}), 200

@app.route("/api/chat", methods=["POST"])
@jwt_required()
@limiter.limit("20 per minute")
def api_chat() -> tuple:
    """Chat with Billy."""
    data = request.json
    if not data or not isinstance(data.get("prompt"), str):
        return error_response("Missing or invalid prompt", 400)
    prompt = data["prompt"]
    memories = search_memory(prompt)
    if isinstance(memories, dict):
        return error_response(memories.get("error", "Search failed"), 500)
    memory_context = "\n".join(memories) if memories else "No relevant memories found."
    user_prompt = f"""You are Billy, Chad's AI Assistant.
Relevant memories:\n{memory_context}\n
User: {prompt}
"""
    try:
        res = requests.post(
            f"{ollama_url}/api/chat",
            json={
                "model": chat_model,
                "messages": [
                    {"role": "system", "content": "You are a helpful assistant."},
                    {"role": "user", "content": user_prompt}
                ]
            },
            timeout=30
        )
        res.raise_for_status()
        data = res.json()
        if "message" not in data or "content" not in data["message"]:
            logger.error("Invalid Ollama response")
            return error_response("Invalid chat response", 500)
        reply = data["message"]["content"]
        save_memory(f"User: {prompt}")
        save_memory(f"Billy: {reply}")
        return jsonify({"response": reply}), 200
    except requests.RequestException as e:
        logger.error(f"Chat error: {e}")
        return error_response("Chat failed", 500)

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)