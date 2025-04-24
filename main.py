from flask import Flask, request, jsonify
import os, json, requests, time
import config

app = Flask(__name__)
PROFILE_PATH = config.PROFILE_PATH
OLLAMA_URL   = config.OLLAMA_URL
DEFAULT_SEARCH_PROVIDER = config.DEFAULT_SEARCH_PROVIDER

LOG_PATH = "data/query_log.json"
START_TIME = time.time()

def load_profile():
    try:
        if os.path.exists(PROFILE_PATH):
            with open(PROFILE_PATH) as f:
                return json.load(f)
    except:
        return {}
    return {}

def save_profile(profile):
    os.makedirs(os.path.dirname(PROFILE_PATH), exist_ok=True)
    with open(PROFILE_PATH, 'w') as f:
        json.dump(profile, f, indent=2)

def append_log(entry):
    os.makedirs(os.path.dirname(LOG_PATH), exist_ok=True)
    try:
        logs = []
        if os.path.exists(LOG_PATH):
            with open(LOG_PATH) as f:
                logs = json.load(f)
        logs.append(entry)
        logs = logs[-50:]
        with open(LOG_PATH, "w") as f:
            json.dump(logs, f, indent=2)
    except Exception as e:
        print(f"Log error: {e}")

def get_greeting(profile):
    name = profile.get('name')
    style = profile.get('style','').lower()
    if name:
        if style == 'direct':
            return f"{name}, what can I do for you?"
        if style == 'formal':
            return f"Good day, {name}. How may I assist you?"
        return f"Hello {name}! How can I assist you today?"
    return "Hello from BillyB! You can set your profile via POST to /profile."

@app.route('/')
def index():
    return get_greeting(load_profile())

@app.route('/profile', methods=['GET','POST'])
def profile_route():
    if request.method == 'POST':
        data = request.json or {}
        save_profile(data)
        return jsonify(status="saved"), 200
    return jsonify(load_profile()), 200

@app.route('/profile/role', methods=['GET','POST'])
def profile_role():
    profile = load_profile()
    if request.method == 'POST':
        role = (request.json or {}).get("role", "").strip()
        if role:
            profile["role"] = role
            save_profile(profile)
            return jsonify(status="role updated")
        else:
            return jsonify(error="Empty role"), 400
    return jsonify(role=profile.get("role", "You are a helpful assistant."))

@app.route('/profile/favorite', methods=['POST'])
def add_favorite():
    profile = load_profile()
    data = request.json or {}
    favs = profile.get("favorites", [])
    favs.append(data)
    profile["favorites"] = favs[-20:]
    save_profile(profile)
    return jsonify(status="favorite added", total=len(profile["favorites"]))

@app.route('/profile/favorites', methods=['GET'])
def get_favorites():
    profile = load_profile()
    return jsonify(profile.get("favorites", []))

@app.route('/ask', methods=['POST'])
def ask():
    q = (request.json or {}).get('question','').strip()
    if not q:
        return jsonify(error="No question provided"), 400
    log = {
        "type": "ask",
        "question": q,
        "timestamp": time.time()
    }
    result = {
        "response": f"(Echo) You asked: '{q}'",
        "note": "This is a fallback response. Real LLM support is paused until Ollama publishes a compatible Docker image."
    }
    log["response"] = result["response"]
    append_log(log)

    profile = load_profile()
    profile["last_ask"] = {"q": q, "response": result["response"], "timestamp": log["timestamp"]}
    save_profile(profile)

    return jsonify(result), 200

def ddg_search(query):
    r = requests.get("https://api.duckduckgo.com", params={
        "q": query,
        "format": "json",
        "no_redirect": 1,
        "no_html": 1
    })
    r.raise_for_status()
    data = r.json()

    results = []
    if data.get("AbstractText"):
        results.append({
            "title": "DuckDuckGo Instant Answer",
            "snippet": data["AbstractText"],
            "url": data.get("AbstractURL", "")
        })

    for topic in data.get("RelatedTopics", []):
        if "Text" in topic and "FirstURL" in topic:
            results.append({
                "title": topic["Text"].split(" - ")[0],
                "snippet": topic["Text"],
                "url": topic["FirstURL"]
            })

    return results or [{"title": "", "snippet": "No results found.", "url": ""}]

SEARCH_PROVIDERS = {
    "duckduckgo": ddg_search
}

@app.route('/search', methods=['POST'])
def search():
    data = request.get_json() or {}
    query = data.get("query", "").strip()
    provider = data.get("provider", DEFAULT_SEARCH_PROVIDER).lower()

    if not query:
        return jsonify(error="No query provided"), 400
    if provider not in SEARCH_PROVIDERS:
        return jsonify(error=f"Unknown provider '{provider}'"), 400

    try:
        results = SEARCH_PROVIDERS[provider](query)
        append_log({
            "type": "search",
            "query": query,
            "provider": provider,
            "result_count": len(results),
            "timestamp": time.time()
        })

        profile = load_profile()
        profile["last_search"] = {
            "query": query,
            "provider": provider,
            "result_count": len(results),
            "timestamp": time.time()
        }
        save_profile(profile)

        return jsonify(provider=provider, results=results)
    except Exception as e:
        return jsonify(error="Search error", details=str(e)), 500

@app.route('/summarize', methods=['POST'])
def summarize():
    data = request.get_json() or {}
    query = data.get("query", "").strip()

    if not query:
        return jsonify(error="No query provided"), 400

    try:
        results = ddg_search(query)
        top_snippets = [r["snippet"] for r in results if r["snippet"]] or ["No data available."]
        top_snippets = top_snippets[:3]

        summary = " ".join(top_snippets)
        if len(summary) > 350:
            summary = summary[:347] + "..."

        append_log({
            "type": "summarize",
            "query": query,
            "summary": summary,
            "timestamp": time.time()
        })

        return jsonify(
            query=query,
            summary=summary,
            source_count=len(results),
            provider="duckduckgo"
        )

    except Exception as e:
        return jsonify(error="Summarization failed", details=str(e)), 500

@app.route('/admin/status')
def status():
    uptime = round(time.time() - START_TIME, 2)
    return jsonify({
        "status": "running",
        "uptime_sec": uptime,
        "profile": load_profile(),
        "ollama_url": OLLAMA_URL,
        "default_search": DEFAULT_SEARCH_PROVIDER
    })

@app.route('/admin/logs')
def logs():
    if os.path.exists(LOG_PATH):
        with open(LOG_PATH) as f:
            return jsonify(json.load(f))
    return jsonify([])

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)
