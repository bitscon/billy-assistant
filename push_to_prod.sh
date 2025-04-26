#!/bin/bash
set -e

echo "=== 🛠️ Billy Assistant: Push to Production ==="

# Step 1: Local commit
cd ~/Projects/billy-assistant
echo "📂 At: $(pwd)"
git add .
echo "📝 Please enter a commit message: "
read commit_msg
git commit -m "$commit_msg"
git push origin main
echo "✅ Code pushed to GitHub."

# Step 2: SSH into server and rebuild
echo "🔒 SSH into billy server (ai)..."
ssh billybs@ai << 'EOSSH'
  set -e
  echo "📂 Pulling latest code..."
  cd ~/billy-assistant
  git pull origin main

  echo "🐳 Building Docker image..."
  docker build -t localhost:5000/billy-assistant:latest .

  echo "📦 Pushing image to local registry..."
  docker push localhost:5000/billy-assistant:latest

  echo "🚀 Finished server-side. Remember to update stack in Portainer."
EOSSH

echo "🎉 All done! Open Portainer and redeploy the billy-assistant stack."
