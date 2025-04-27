#!/bin/bash
echo "=== 🧹 Billy Git Status Check ==="
cd ~/Projects/billy-assistant || { echo "❌ Failed to cd into project folder"; exit 1; }
git status -s

echo ""
echo "🛑 '?' = Untracked (new files)"
echo "📝 'M' = Modified (needs commit)"
echo "✅ Blank output = Clean! Ready to push."
