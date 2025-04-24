import requests
import os

def handle_ask(question, profile):
    ollama_url = os.getenv("OLLAMA_URL", "http://ollama:11434/api/generate")
    try:
        res = requests.post(
            ollama_url,
            json={"model": "llama3", "prompt": question},
            timeout=10
        )
        res.raise_for_status()
        result = res.json()
        return {
            "response": result.get("response", "").strip(),
            "note": "LLM response from Ollama"
        }
    except Exception as e:
        return {
            "response": f"(Echo) You asked: '{question}'",
            "note": "This is a fallback response. Real LLM support is paused until Ollama publishes a compatible Docker image."
        }

def perform_search(query):
    try:
        res = requests.get(
            "https://duckduckgo.com/html",
            params={"q": query},
            timeout=10
        )
        if res.status_code == 200:
            # Simplified stub logic for HTML fallback
            return [{"title": "", "url": "", "snippet": "No results found."}]
        else:
            return [{"title": "", "url": "", "snippet": "Search failed."}]
    except Exception:
        return [{"title": "", "url": "", "snippet": "Search error."}]

def summarize_query(query):
    results = perform_search(query)
    snippets = [r.get("snippet", "") for r in results if r.get("snippet")]
    summary = snippets[0] if snippets else "No results found."
    return {
        "provider": "duckduckgo",
        "query": query,
        "source_count": len(results),
        "summary": summary
    }
