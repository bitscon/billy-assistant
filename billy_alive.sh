#!/bin/bash

echo "=== 🚀 Billy Alive Script ==="
cd ~/Projects/billy-assistant || { echo "❌ Project folder not found"; exit 1; }

# 🔍 Step 0: Check Git status before anything else
echo ""
echo "=== 🧹 Quick Git Check ==="
./git_status_easy.sh
echo ""

# 📝 Step 1: Commit changes
echo "📝 Enter your commit message:"
read commit_msg
git add .
git commit -m "$commit_msg"
git push

echo "✅ Code pushed to GitHub."

# 🔒 Step 2: SSH into AI server and build/push images
ssh billybs@ai << 'REMOTE_EOF'
cd ~/billy-assistant || exit 1
git pull
docker build -t localhost:5000/billy-assistant:latest .
docker push localhost:5000/billy-assistant:latest

cd ~/billy-memory || exit 1
docker-compose build
docker-compose push
exit
REMOTE_EOF

echo "✅ AI server done. You can update Portainer now!"

# 🔍 Step 3: Quick assistant healthcheck
echo ""
echo "🔍 Verifying assistant endpoints..."

ask=$(curl -s -X POST http://ai:5001/ask -H "Content-Type: application/json" -d '{"question":"ping"}' | jq -r '.response')
search=$(curl -s -X POST http://ai:5001/search -H "Content-Type: application/json" -d '{"query":"ping"}' | jq -r '.provider')
summarize=$(curl -s -X POST http://ai:5001/summarize -H "Content-Type: application/json" -d '{"query":"ping"}' | jq -r '.summary')
status=$(curl -s http://ai:5001/admin/status | jq -r '.status')
role=$(curl -s http://ai:5001/profile/role | jq -r '.role')

echo "- Checking /ask... \"$ask\""
echo "- Checking /search... \"$search\""
echo "- Checking /summarize... \"$summarize\""
echo "- Checking /admin/status... \"$status\""
echo "- Checking /profile/role... \"$role\""

# 🎉 Final message
echo ""
echo "🎉 All steps done. Billy is ALIVE and operational!"
echo "📦 Please update the stack(s) in Portainer manually to complete deployment!"
