from flask import Flask, request, jsonify
import os
import time
from app.memory import create_collection, save_memory, search_memory

app = Flask(__name__)
create_collection()

@app.route("/", methods=["GET"])
def home():
    return "Good day, Chad. How may I assist you?"

@app.route("/memory/save", methods=["POST"])
def memory_save():
    data = request.get_json()
    text = data.get("text")
    if not text:
        return jsonify({"error": "Missing 'text' field."}), 400
    save_memory(text)
    return jsonify({"status": "Memory saved"}), 200

@app.route("/memory/search", methods=["POST"])
def memory_search():
    data = request.get_json()
    query = data.get("query")
    if not query:
        return jsonify({"error": "Missing 'query' field."}), 400
    results = search_memory(query)
    return jsonify(results)

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)
