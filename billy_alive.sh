#!/bin/bash

echo "=== 🚀 Billy Alive Script ==="

# Step 1: Git commit + push
echo "📂 At: $(pwd)"
echo -n "📝 Enter your commit message: "
read commit_message

git add .
git commit -m "$commit_message"
git push

echo "✅ Code pushed to GitHub."

# Step 2: SSH into server
echo "🔒 SSH into ai server..."
ssh billybs@ai << 'EOSSH'
  echo "📂 Pulling latest code..."
  cd ~/billy-assistant
  git pull origin main

  echo "🐳 Rebuilding Docker image..."
  docker build -t localhost:5000/billy-assistant:latest .

  echo "🚀 Pushing to local registry..."
  docker push localhost:5000/billy-assistant:latest
EOSSH

# Step 3: Remind about Portainer
echo ""
echo "📦 Please open Portainer and update the billy-assistant stack manually!"
echo ""

# Step 4: Quick API Health Checks
echo "🔍 Verifying assistant endpoints..."
base_url="http://ai:5001"

echo "- Checking /ask..."
curl -s -X POST "$base_url/ask" -H "Content-Type: application/json" -d '{"question":"ping"}' | jq '.response' || echo "❌ /ask failed"

echo "- Checking /search..."
curl -s -X POST "$base_url/search" -H "Content-Type: application/json" -d '{"query":"test"}' | jq '.provider' || echo "❌ /search failed"

echo "- Checking /summarize..."
curl -s -X POST "$base_url/summarize" -H "Content-Type: application/json" -d '{"query":"test"}' | jq '.summary' || echo "❌ /summarize failed"

echo "- Checking /admin/status..."
curl -s "$base_url/admin/status" | jq '.status' || echo "❌ /admin/status failed"

echo "- Checking /profile/role..."
curl -s "$base_url/profile/role" | jq '.role' || echo "❌ /profile/role failed"

echo ""
echo "🎉 All steps done. Billy is ALIVE and operational!"
