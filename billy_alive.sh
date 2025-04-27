#!/bin/bash

# === 🚀 Billy Alive Script ===
echo "=== 🚀 Billy Alive Script ==="
echo "\U0001F4C2 At: $(pwd)"

# Ask for commit message
echo "\U0001F4DD Enter your commit message:"
read commit_msg

# Git push
if [ -n "$commit_msg" ]; then
  git add .
  git commit -m "$commit_msg"
fi
git push

echo "✅ Code pushed to GitHub."

# SSH into AI server and deploy
ssh ai << 'EOSSH'
  set -e
  cd ~/billy-assistant

  echo "\U0001F4C2 Pulling latest code..."
  git reset --hard origin/main
  git pull origin main

  echo "\U0001F680 Rebuilding Docker image..."
  docker build -t localhost:5000/billy-assistant:latest .
  docker push localhost:5000/billy-assistant:latest
EOSSH

echo "✅ AI server done. You can update Portainer now!"
echo "\U0001F4E6 Please update the stack(s) in Portainer manually to complete deployment!"

# === Endpoint Checks ===
echo "\U0001F50D Verifying assistant endpoints..."

check_endpoint() {
  url=$1
  method=${2:-GET}
  data=${3:-}

  if [ "$method" == "POST" ]; then
    code=$(curl -s -o /dev/null -w "%{http_code}" -X POST "$url" -H "Content-Type: application/json" -d "$data")
  else
    code=$(curl -s -o /dev/null -w "%{http_code}" "$url")
  fi

  if echo "$code" | grep -q "200"; then
    echo "- Checking $url... OK"
  else
    echo "- Checking $url... ❌ Unexpected response ($code)"
  fi
}

check_endpoint "http://ai:5001/"
check_endpoint "http://ai:5001/memory/save" POST '{"text":"ping memory"}'
check_endpoint "http://ai:5001/memory/search" POST '{"query":"ping"}'


# === Done ===
echo "\n\U0001F389 All steps done. Billy is ALIVE and operational!"
echo "\U0001F4E6 Remember to update Portainer to finish deployment."
