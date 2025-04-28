Billy Assistant
A Flask-based AI assistant that stores memories in Qdrant and uses Ollama for embeddings and chat. Designed to integrate with an iOS app.
Setup

Prerequisites:

Docker and Docker Compose installed.
A machine with IP 192.168.1.112 for hosting.


Clone Repository:
git clone https://github.com/bitscon/billy-assistant.git
cd billy-assistant


Create Docker Network:
docker network create billy-network


Build and Run:
docker build -t localhost:5000/billy-assistant:latest .
docker-compose up -d


Test API:
curl -X POST http://192.168.1.112:5001/api/token -H "Content-Type: application/json" -d '{"username":"chad","password":"secure-password-123"}'



iOS Integration

Use http://192.168.1.112:5001 for API calls.
Add ATS exception in Info.plist for local testing:<key>NSAppTransportSecurity</key>
<dict>
    <key>NSAllowsArbitraryLoads</key>
    <true/>
</dict>


Deploy with HTTPS in production.

Endpoints

POST /api/token: Get JWT token.
POST /api/memory/save: Save a memory.
POST /api/memory/search: Search memories.
POST /api/chat: Chat with Billy.

