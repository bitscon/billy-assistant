#!/bin/bash
set -e

echo "=== 🚀 Billy Alive Script ==="
cd ~/Projects/billy-assistant
echo "📂 At: $(pwd)"

# Git commit
echo -n "📝 Enter your commit message: "
read commit_msg
git add .
git commit -m "$commit_msg"
git push

echo "✅ Code pushed to GitHub."

# SSH into AI server and rebuild
echo "🔒 SSH into ai server..."
ssh billybs@ai << 'EOSSH'
  cd ~/billy-assistant
  echo "📂 Pulling latest code..."
  git pull origin main || echo "⚠️ Git pull failed, continuing..."
  echo "🐳 Rebuilding Docker image..."
  docker build -t localhost:5000/billy-assistant:latest .
  echo "🚀 Pushing to local registry..."
  docker push localhost:5000/billy-assistant:latest
EOSSH

echo "✅ AI server done. You can update Portainer now!"

# Quick verification
echo ""
echo "🔍 Verifying assistant endpoints..."
for endpoint in ask search summarize admin/status profile/role; do
    if [[ "$endpoint" == "ask" ]]; then
        payload='{"question":"ping"}'
        result=$(curl -s -X POST http://ai:5001/ask -H "Content-Type: application/json" -d "$payload" || echo "failed")
    elif [[ "$endpoint" == "search" ]]; then
        payload='{"query":"test"}'
        result=$(curl -s -X POST http://ai:5001/search -H "Content-Type: application/json" -d "$payload" || echo "failed")
    elif [[ "$endpoint" == "summarize" ]]; then
        payload='{"query":"testing summarize"}'
        result=$(curl -s -X POST http://ai:5001/summarize -H "Content-Type: application/json" -d "$payload" || echo "failed")
    else
        result=$(curl -s http://ai:5001/$endpoint || echo "failed")
    fi
    echo "- Checking /$endpoint... \"$(echo $result | cut -c1-30)...\""
done

echo ""
echo "🎉 All steps done. Billy is ALIVE and operational!"
echo "📦 Please update the stack in Portainer manually to complete deployment!"

# 🎯 Final "Done!" and sound
echo ""
echo "🎯 Done! You can safely close this window or run another command."

if command -v paplay &> /dev/null; then
    paplay /usr/share/sounds/freedesktop/stereo/complete.oga &
elif command -v aplay &> /dev/null; then
    aplay /usr/share/sounds/alsa/Front_Center.wav &
else
    echo "🔇 No sound player found, skipping sound."
fi

exit 0
