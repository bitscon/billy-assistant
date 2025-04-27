from flask import Flask, request, jsonify
import time
import os
import requests

from app.memory import save_memory, search_memory  # 🧠 Memory module

app = Flask(__name__)
logs = []

DEFAULT_SEARCH_PROVIDER = os.getenv("DEFAULT_SEARCH_PROVIDER", "duckduckgo")
OLLAMA_URL = os.getenv("OLLAMA_URL", "http://ollama:11434/api/generate")

def log_event(event):
    event["timestamp"] = time.time()
    logs.append(event)

@app.route("/")
def home():
    return "Good day, Chad. How may I assist you?"

@app.route("/ask", methods=["POST"])
def ask():
    data = request.get_json()
    question = data.get("question", "")
    if not question:
        return jsonify({"error": "Missing question"}), 400
    try:
        r = requests.post(OLLAMA_URL, json={"prompt": question}, timeout=10)
        r.raise_for_status()
        result = r.json()["response"]
    except Exception as e:
        result = f"(Echo) You asked: '{question}'"
    log_event({"type": "ask", "question": question, "response": result})
    return jsonify({"response": result})

@app.route("/search", methods=["POST"])
def search():
    data = request.get_json()
    query = data.get("query", "")
    log_event({"type": "search", "query": query})
    return jsonify({"results": [{"title": "", "url": "", "snippet": "No results found."}]})

@app.route("/summarize", methods=["POST"])
def summarize():
    data = request.get_json()
    query = data.get("query", "")
    log_event({"type": "summarize", "query": query})
    return jsonify({"summary": "No results found."})

@app.route("/admin/status")
def status():
    uptime_sec = time.time() - app.start_time
    return jsonify({
        "status": "running",
        "uptime_sec": uptime_sec,
        "profile": app.profile,
        "default_search": DEFAULT_SEARCH_PROVIDER,
        "ollama_url": OLLAMA_URL
    })

@app.route("/admin/logs")
def get_logs():
    return jsonify(logs)

@app.route("/profile/role", methods=["GET", "POST"])
def role():
    if request.method == "GET":
        return jsonify({"role": app.profile.get("role", "")})
    data = request.get_json()
    app.profile["role"] = data.get("role", "")
    return jsonify({"status": "role updated"})

@app.route("/profile/favorite", methods=["POST"])
def favorite():
    data = request.get_json()
    app.profile.setdefault("favorites", []).append({
        "type": data.get("type", ""),
        "content": data.get("content", ""),
        "saved": data.get("saved", True)
    })
    return jsonify({"status": "favorite added", "total": len(app.profile["favorites"])})

@app.route("/profile/favorites", methods=["GET"])
def favorites():
    return jsonify(app.profile.get("favorites", []))

@app.route("/about")
def about():
    log_event({"type": "meta", "event": "about_check", "timestamp": time.time()})
    return jsonify({
        "assistant_name": "Billy",
        "purpose": "Personal assistant and research tool",
        "status": "MVP (expanding memory and capabilities)"
    })

# 🧠 NEW: Save memory
@app.route("/memory/save", methods=["POST"])
def memory_save():
    data = request.get_json()
    vector = data.get("vector")
    payload = data.get("payload", {})
    if not vector or not isinstance(vector, list):
        return jsonify({"error": "Missing or invalid 'vector' field."}), 400
    id = int(time.time() * 1000)
    save_memory(id, vector, payload)
    log_event({"type": "memory_save", "id": id})
    return jsonify({"status": "memory saved", "id": id})

# 🧠 NEW: Search memory
@app.route("/memory/search", methods=["POST"])
def memory_search():
    data = request.get_json()
    query_vector = data.get("vector")
    if not query_vector or not isinstance(query_vector, list):
        return jsonify({"error": "Missing or invalid 'vector' field."}), 400
    results = search_memory(query_vector)
    log_event({"type": "memory_search", "result_count": len(results)})
    return jsonify({"results": [r.dict() for r in results]})

# Initialize
if __name__ == "__main__":
    app.start_time = time.time()
    app.profile = {"name": "Chad", "style": "formal"}
    app.run(host="0.0.0.0", port=5000)
