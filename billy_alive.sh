#!/bin/bash
echo "=== 🚀 Billy Alive Script ==="
cd ~/Projects/billy-assistant || { echo "❌ Project folder not found"; exit 1; }

read -p "📝 Enter your commit message: " message
git add .
git commit -m "$message"
git push

ssh ai << 'EOSSH'
cd ~/billy-assistant || { echo "❌ Server project folder not found"; exit 1; }
git pull origin main
docker build -t localhost:5000/billy-assistant:latest .
docker push localhost:5000/billy-assistant:latest
EOSSH

echo "✅ AI server done. You can update Portainer now!"

# Local test endpoints
echo "🔍 Verifying assistant endpoints..."
endpoints=(/ask /search /summarize /admin/status /profile/role)
for ep in "${endpoints[@]}"; do
    echo -n "- Checking $ep... "
    curl -s http://ai:5001$ep | head -c 100
    echo
done

echo "🎉 All steps done. Billy is ALIVE and operational!"
echo "📦 Please update the stack(s) in Portainer manually to complete deployment!"
