# 🤖 BillyB Assistant

BillyB is a Dockerized, Flask-based personal assistant with modular endpoints for search, summarization, AI responses, and profile memory.

## 🔧 Features

- Modular `/ask`, `/search`, `/summarize` endpoints
- Memory via JSON-stored user profiles
- DuckDuckGo-based fallback search
- Flask REST API with `/admin/*` controls
- Docker + Portainer deployable
- End-of-day dev sync script

## 📂 Project Files

- `main.py` – Core Flask app
- `Dockerfile` – Builds the assistant container
- `docker-compose.yml` – Defines the assistant + Ollama services
- `assistant-project-plan.txt` – Master roadmap
- `billyb-assistant-progress-report-1.0.txt` – Daily progress tracker

## 💡 Ideas & Future Plans

We track upcoming ideas, integrations, and creative features in the [`ideas/`](./ideas/) directory.

Explore:
- [`features.md`](./ideas/features.md) – Core roadmap features
- [`integrations.md`](./ideas/integrations.md) – Third-party tools to integrate
- [`fun-stuff.md`](./ideas/fun-stuff.md) – Personality modes and easter eggs

## 🧠 Get Involved

Feel free to fork, submit issues, or suggest ideas.  
This is just the beginning — your assistant should reflect *you*.

## 🛠️ Author

**Chad McCormack**  
🧪 Innovating tech, automating everything, refusing to be boring.

## 🚀 Push to Production Options

### 1. Regular Push

```bash
cd ~/Projects/billy-assistant
./push_to_prod.sh

