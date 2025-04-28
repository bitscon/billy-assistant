import os
import logging
import uuid
from typing import Dict, List, Union
import requests
from flask import Flask, jsonify, request
from flask_cors import CORS
from flask_jwt_extended import JWTManager, jwt_required
from flask_limiter import Limiter
from flask_limiter.util import get_remote_address

app = Flask(__name__)

# Configurations
app.config["JWT_SECRET_KEY"] = os.getenv("JWT_SECRET_KEY", "your-secret-key")  # Change in production
CORS(app, resources={r"/api/*": {"origins": "*"}})  # Restrict origins in production
jwt = JWTManager(app)
limiter = Limiter(app, key_func=get_remote_address, default_limits=["200 per day", "50 per hour"])

qdrant_url = os.getenv("QDRANT_URL") or "http://qdrant:6333"
ollama_url = os.getenv("OLLAMA_URL") or "http://ollama:11434"
collection_name = os.getenv("COLLECTION_NAME", "billy_memories")
embedding_model = os.getenv("EMBEDDING_MODEL", "nomic-embed-text")
chat_model = os.getenv("CHAT_MODEL", "llama3")
vector_size = int(os.getenv("VECTOR_SIZE", 768))

# Logging setup
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Memory Management
def ensure_collection() -> bool:
    """
    Ensure Qdrant collection exists.
    
    Returns:
        bool: True if collection exists or was created, False otherwise.
    """
    try:
        res = requests.get(f"{qdrant_url}/collections/{collection_name}")
        if res.status_code == 404:
            schema = {
                "vectors": {
                    "size": vector_size,
                    "distance": "Cosine"
                }
            }
            create = requests.put(f"{qdrant_url}/collections/{collection_name}", json=schema)
            if not create.ok:
                logger.error(f"Failed to create collection: {create.text}")
                return False
        elif not res.ok:
            logger.error(f"Collection check failed: {res.text}")
            return False
        return True
    except requests.RequestException as e:
        logger.error(f"Collection check error: {e}")
        return False

def embed_text(text: str) -> Union[List[float], None]:
    """
    Generate text embedding using Ollama.
    
    Args:
        text: The text to embed.
    
    Returns:
        List[float]: The embedding vector, or None if failed.
    """
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
    """
    Save a piece of memory into Qdrant.
    
    Args:
        text: The text to save as a memory.
    
    Returns:
        bool: True if saved successfully, False otherwise.
    """
    try:
        if not isinstance(text, str) or len(text) > 1000:
            logger.error("Invalid text input")
            return False
        embedding = embed_text(text)
        if embedding is None:
            logger.error("Failed to generate embedding")
            return False
        payload = {
            "points": [
                {
                    "id": str(uuid.uuid4()),
                    "vector": embedding,
                    "payload": {"text": text}
                }
            ]
        }
        res = requests.put(
            f"{qdrant_url}/collections/{collection_name}/points",
            json=payload,
            timeout=10
        )
        res.raise_for_status()
        return True
    except requests.RequestException as e:
        logger.error(f"Save memory error: {e}")
        return False

def search_memory(query: str, limit: int = 5) -> Union[List[str], Dict[str, str]]:
    """
    Find relevant memories based on the query using vector search.
    
    Args:
        query: The search query string.
        limit: Maximum number of results to return.
    
    Returns:
        Union[List[str], Dict[str, str]]: List of matching memory texts, or error dict if failed.
    """
    try:
        embedding = embed_text(query)
        if embedding is None:
            return {"error": "Failed to generate query embedding"}
        res = requests.post(
            f"{qdrant_url}/collections/{collection_name}/points/search",
            json={"vector": embedding, "limit": limit, "with_payload": True},
            timeout=10
        )
        res.raise_for_status()
        points = res.json().get("result", [])
        matches = [point["payload"]["text"] for point in points if "payload" in point and "text" in point["payload"]]
        return matches
    except requests.RequestException as e:
        logger.error(f"Search error: {e}")
        return {"error": f"Search failed: {str(e)}"}

# Error Response Helper
def error_response(message: str, status_code: int) -> tuple:
    """
    Create a standardized error response.
    
    Args:
        message: The error message.
        status_code: HTTP status code.
    
    Returns:
        tuple: JSON response and status code.
    """
    return jsonify({"error": message}), status_code

# Routes
@app.before_first_request
def initialize():
    """Initialize the Qdrant collection before the first request."""
    if not ensure_collection():
        raise RuntimeError("Failed to initialize Qdrant collection")

@app.route("/", methods=["GET"])
def home() -> str:
    """Root endpoint for basic greeting."""
    return "Good day, Chad. How may I assist you?"

@app.route("/api/memory/save", methods=["POST"])
@jwt_required()
@limiter.limit("10 per minute")
def api_save_memory() -> tuple:
    """
    Save a memory to Qdrant.
    
    Expects JSON: {"text": "memory text"}
    
    Returns:
        tuple: JSON response and status code.
    """
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
    """
    Search for memories matching the query.
    
    Expects JSON: {"query": "search text"}
    
    Returns:
        tuple: JSON response and status code.
    """
    data = request.json
    if not data or not isinstance(data.get("query"), str):
        return error_response("Missing or invalid query", 400)
    results = search_memory(data["query"])
    if isinstance(results, dict) and "error" in results:
        return error_response(results["error"], 500)
    return jsonify({"results": results}), 200

@app.route("/api/chat", methods=["POST"])
@jwt_required()
@limiter.limit("20 per minute")
def chat() -> tuple:
    """
    Chat with Billy: search memory and generate response.
    
    Expects JSON: {"prompt": "user message"}
    
    Returns:
        tuple: JSON response and status code.
    """
    data = request.json
    if not data or not isinstance(data.get("prompt"), str):
        return error_response("Missing or invalid prompt", 400)
    
    try:
        # Search memory
        memories = search_memory(data["prompt"])
        if isinstance(memories, dict) and "error" in memories:
            return error_response(memories["error"], 500)
        memory_context = "\n".join(memories) if memories else "No relevant memories found."

        # Build prompt
        final_prompt = f"""You are Billy, Chad's AI Assistant.
Use the following memories if relevant:

{memory_context}

Answer Chad's question:
{data["prompt"]}
"""

        # Call Ollama
        res = requests.post(
            f"{ollama_url}/api/chat",
            json={
                "model": chat_model,
                "messages": [
                    {"role": "system", "content": "You are a helpful personal assistant named Billy."},
                    {"role": "user", "content": final_prompt}
                ]
            },
            timeout=30
        )
        res.raise_for_status()
        response = res.json()
        if "message" not in response or "content" not in response["message"]:
            return error_response("Invalid Ollama response", 500)
        reply = response["message"]["content"]

        # Save conversation
        save_memory(f"User: {data['prompt']}")
        save_memory(f"Billy: {reply}")

        return jsonify({"response": reply}), 200
    except requests.RequestException as e:
        logger.error(f"Chat error: {e}")
        return error_response("Chat processing failed", 500)

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)