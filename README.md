# Billy Assistant

**Self-hosted AI assistant** built with Docker, Flask, and Ollama (LLM backend).  
Designed for secure, local AI tasks with web search, profile memory, and customizable behavior.

---

## 🚀 Features

- `/ask`: Ask questions, get answers (fallback if LLM is offline)
- `/search`: Real-time web results via DuckDuckGo
- `/summarize`: Combines top search snippets into 1 clear answer
- `/profile`: Set name, tone, personality, favorites
- `/admin`: View logs, system status, and debug

---

## 📦 Stack

- Python + Flask (REST API)
- Ollama (self-hosted LLM, fallback mode enabled)
- DuckDuckGo (current search provider)
- Dockerized for easy local deployment

---

## 🔧 Setup

Clone the repo and start with Docker:

\`\`\`bash
git clone git@github.com:bitscon/billy-assistant.git
cd billy-assistant
docker-compose up -d --build
\`\`\`

Access the API via: `http://localhost:5001`

---

## 📖 Endpoints

| Endpoint         | Method | Description                        |
|------------------|--------|------------------------------------|
| `/ask`           | POST   | Ask anything (text only)           |
| `/search`        | POST   | DuckDuckGo search results          |
| `/summarize`     | POST   | Summary of top search snippets     |
| `/admin/logs`    | GET    | Retrieve session logs              |
| `/admin/status`  | GET    | Get app uptime and state           |
| `/profile/*`     | GET/POST | Customize personality, favorites |

---

## 🗂️ Project Structure

\`\`\`bash
billy-assistant/
├── Dockerfile
├── docker-compose.yml
├── main.py
├── requirements.txt
├── data/              # Local user data (volumed)
├── README.md
├── assistant-project-plan.txt
└── billyb-assistant-progress-report-1.0.txt
\`\`\`

---

## 🧪 Testing

Send sample requests with:

\`\`\`bash
curl -X POST http://localhost:5001/ask -H "Content-Type: application/json" -d '{"question":"What is Docker?"}'
\`\`\`

---

## 🔒 Status

🧠 LLM fallback active — real Ollama support pending latest Docker release.  
Check `/admin/status` for live info.

---

## 🏷️ Version

\`v1.0\` — MVP release committed 2025-04-24

---

## 📬 Contact

Maintained by [Chad McCormack](https://github.com/bitscon)  
Questions or ideas? Open an issue or hit me up.
