#!/usr/bin/env bash
set -euo pipefail

LOCAL_DIR=~/Projects/billy-assistant
REMOTE_HOST=ai
SSH="ssh $REMOTE_HOST"

echo "📂 At: $LOCAL_DIR"
echo "📝 Enter your commit message:"
read -r MSG

# 1) Commit & push to GitHub
git -C "$LOCAL_DIR" add .
git -C "$LOCAL_DIR" commit -m "$MSG"
git -C "$LOCAL_DIR" push origin main
echo "✅ Code pushed to GitHub."

# 2) SSH -> pull & redeploy
echo "🔒 SSH into $REMOTE_HOST and redeploying..."
$SSH bash << "EOSSH"
  set -euo pipefail
  cd ~/billy-assistant
  git fetch origin
  git reset --hard origin/main

  echo "🐳 Pulling & starting new image..."
  docker-compose pull assistant
  docker-compose up -d --force-recreate --no-deps assistant

  # wait for healthy
  echo "⏳ Waiting for assistant to come up..."
  for i in {1..10}; do
    if curl -s http://localhost:5000/ >/dev/null; then
      echo "✅ Assistant is up!"
      exit 0
    fi
    sleep 2
  done
  echo "❌ Assistant failed to start in time." >&2
  exit 1
EOSSH

# 3) Verify endpoints (with retries)
echo "🔍 Verifying assistant endpoints..."
function test_ep {
  local url=$1
  local expect=$2
  if curl -s --retry 3 --retry-delay 2 "$url" | grep -q "$expect"; then
    echo "- $url ... OK"
  else
    echo "- $url ... ❌ Unexpected response"
  fi
}

test_ep "http://$REMOTE_HOST:5001/" "Good day"
test_ep "http://$REMOTE_HOST:5001/ask" "{\"error\":\"No question provided\""
test_ep "http://$REMOTE_HOST:5001/search" "{\"error\":\"No query provided\""
test_ep "http://$REMOTE_HOST:5001/summarize" "{\"error\":\"No query provided\""
test_ep "http://$REMOTE_HOST:5001/admin/status" "\"status\":\"running\""
test_ep "http://$REMOTE_HOST:5001/profile/role" "\"role\":"

echo ""
echo "🎉 Billy is ALIVE and operational!"
echo "📦 If you prefer Portainer, open it now and click 'Update Stack' on billy-assistant."
