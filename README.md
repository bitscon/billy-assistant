# 🧠 Billy Assistant

Billy is a personal assistant server, self-hosted with Docker, Flask, DuckDuckGo search, and Qdrant memory storage.

---
## 🚀 Quick Commands

| Action | Command |
|:------:|:-------:|
| Push code to production + verify | `./billy_alive.sh` |
| End of day push + notes | `./end_of_day.sh` |

---
## 📚 Documentation

- [Memory System](docs/memory.md)
- [Architecture Overview](docs/architecture.md)
- [Deployment Guide](docs/deployment.md)

---
## 🛠️ Stacks

| Stack | Purpose |
|:-----:|:-------:|
| `billy-assistant` | Core Assistant API and Logic |
| `billy-memory`    | Vector DB (Qdrant) for Memory Storage |
