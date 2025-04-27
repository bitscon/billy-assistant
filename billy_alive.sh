#!/bin/bash
set -e

echo "=== 🚀 Billy Alive Script ==="
echo "📂 At: $(pwd)"

# Commit Code
echo "📝 Enter your commit message: "
read commit_message
git add .
git commit -m "$commit_message"
git push
echo "✅ Code pushed to GitHub."

# SSH into AI server
echo "🔒 SSH into ai server..."
ssh billybs@ai << 'INNER_SSH'
  set -e
  cd ~/billy-assistant

  echo "📂 Pulling latest code..."
  git pull

  echo "🐳 Rebuilding Docker image..."
  docker build -t localhost:5000/billy-assistant:latest . || { echo "❌ Docker build failed."; exit 1; }
  
  echo "🚀 Pushing to local registry..."
  docker push localhost:5000/billy-assistant:latest || { echo "❌ Docker push failed."; exit 1; }

  echo "✅ AI server done. You can update Portainer now!"
INNER_SSH

# Remind to update
echo "📦 Please update the stack(s) in Portainer manually to complete deployment!"

# Health check
echo "🔍 Verifying assistant endpoints..."

check_url() {
  url=$1
  expect=$2
  result=$(curl -s --max-time 5 "$url")
  if echo "$result" | grep -qi "$expect"; then
    echo "- Checking $url... OK"
  else
    echo "- Checking $url... ❌ Unexpected response!"
  fi
}

check_url "http://ai:5001/" "Good day"
check_url "http://ai:5001/memory/save" "Missing text"
check_url "http://ai:5001/memory/search" "Missing query"

# Celebration sound (optional)
echo -e "\a"
sleep 0.5
echo -e "\a"
sleep 0.5
echo -e "\a"

echo "🎉 All steps done. Billy is ALIVE and operational!"
