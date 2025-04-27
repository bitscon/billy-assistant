#!/bin/bash
set -e

echo "=== 🚀 Billy Alive Script ==="
echo "📂 At: $(pwd)"

# Step 1: Commit and Push code
read -p "📝 Enter your commit message: " commit_message
git add .
git commit -m "$commit_message"
git push
echo "✅ Code pushed to GitHub."

# Step 2: SSH into AI server
echo "🔒 SSH into ai server..."
ssh billybs@ai << 'EOSSH'
set -e
cd ~/billy-assistant
echo "📂 Pulling latest code..."
git pull

# Rebuild billy-assistant stack
echo "🐳 Rebuilding billy-assistant stack..."
docker compose -f docker-compose.yml build
docker compose -f docker-compose.yml push

# Rebuild billy-memory stack
echo "🧠 Rebuilding billy-memory stack..."
cd ~/billy-assistant/stacks/billy-memory
docker compose build
docker compose push

echo "✅ AI server done. You can update Portainer now!"
EOSSH

# Step 3: Final note
echo ""
echo "📦 Please update the stacks in Portainer manually!"
echo ""
echo "🔍 Verifying assistant endpoints..."

# Health check if you want
curl -s http://ai:5001/admin/status | grep "running" && echo "✅ Billy assistant is running!" || echo "❌ Billy assistant not healthy."

echo "🎉 All steps done. Billy is ALIVE and operational!"
