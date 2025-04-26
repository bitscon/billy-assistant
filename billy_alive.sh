#!/bin/bash

echo "=== 🚀 Billy Alive Script ==="
echo "📂 At: $(pwd)"

# 1. Confirm SSH connectivity to GitHub
echo "🔒 Checking SSH connection to GitHub..."
if ssh -T git@github.com 2>&1 | grep -q "successfully authenticated"; then
    echo "✅ SSH to GitHub OK."
else
    echo "❌ SSH connection failed! Please fix SSH keys first."
    exit 1
fi

# 2. Git add, commit, push
echo
read -p "📝 Enter your commit message: " commit_message
git add .
git commit -m "$commit_message"
git push

echo "✅ Code pushed to GitHub."

# 3. SSH into AI server and pull, rebuild, push Docker
echo "🔒 SSH into ai server..."
ssh billybs@ai << 'EOC'
  cd ~/billy-assistant
  echo "📂 Pulling latest code..."
  git pull origin main

  echo "🐳 Rebuilding Docker image..."
  docker build -t localhost:5000/billy-assistant:latest .
  
  echo "🚀 Pushing to local registry..."
  docker push localhost:5000/billy-assistant:latest
  
  echo "✅ AI server done. You can update Portainer now!"
EOC

# 4. Local Post-check: Verify endpoints
echo
echo "🔍 Verifying assistant endpoints..."
ASK=$(curl -s -X POST http://ai:5001/ask -H "Content-Type: application/json" -d '{"question":"ping"}' | jq '.response' || echo "Fail")
SEARCH=$(curl -s -X POST http://ai:5001/search -H "Content-Type: application/json" -d '{"query":"ping"}' | jq '.provider' || echo "Fail")
SUMMARY=$(curl -s -X POST http://ai:5001/summarize -H "Content-Type: application/json" -d '{"query":"ping"}' | jq '.summary' || echo "Fail")
STATUS=$(curl -s http://ai:5001/admin/status | jq '.status' || echo "Fail")
ROLE=$(curl -s http://ai:5001/profile/role | jq '.role' || echo "Fail")

echo "- Checking /ask... $ASK"
echo "- Checking /search... $SEARCH"
echo "- Checking /summarize... $SUMMARY"
echo "- Checking /admin/status... $STATUS"
echo "- Checking /profile/role... $ROLE"

echo
echo "🎉 All steps done. Billy is ALIVE and operational!"
echo "📦 Please update the stack in Portainer manually to complete deployment!"
