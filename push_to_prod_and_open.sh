#!/bin/bash

echo "=== 🛠️ Billy Assistant: Push to Production + Open Portainer ==="

# Show current project directory
echo "📂 At: $(pwd)"

# Prompt for commit message
echo -n "📝 Please enter a commit message: "
read commit_message

# Git add, commit, and push
git add .
git commit -m "$commit_message"
git push

echo "✅ Code pushed to GitHub."

# SSH into billy server (ai)
echo "🔒 SSH into billy server (ai)..."
ssh billybs@ai << 'EOSSH'
  echo "📂 Pulling latest code..."
  cd ~/billy-assistant
  git pull origin main

  echo "🐳 Rebuilding Docker image..."
  docker build -t localhost:5000/billy-assistant:latest .

  echo "🚀 Pushing to local registry..."
  docker push localhost:5000/billy-assistant:latest
EOSSH

echo ""
echo "📚 Tip: If SSH asks for trust (first time), just type 'yes' to accept the server fingerprint!"
echo ""

echo "📦 Now open Portainer and update the stack manually."
echo "✅ Done! Billy is deployed."
