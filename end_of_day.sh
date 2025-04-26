#!/bin/bash

# === BillyB End-of-Day Checklist ===

echo "=== 💡 BillyB End-of-Day Checklist ==="

# Test if app is running
echo "🔍 Verifying assistant is online..."
if curl -s http://localhost:5001/ > /dev/null; then
  echo "✔️ Assistant is online."
else
  echo "❌ Assistant is NOT online!"
  exit 1
fi

# Test important endpoints
echo "🔧 Testing critical endpoints..."
for endpoint in search ask admin/status summarize; do
  if curl -s http://localhost:5001/$endpoint > /dev/null; then
    echo "✔️ /$endpoint passed"
  else
    echo "❌ /$endpoint failed!"
    exit 1
  fi
done

# Prompt for work summary
echo -n "📝 What did you work on today? (1-liner): "
read work_summary

# Prompt for commit message
echo -n "💬 Commit message (default: same as above): "
read commit_message

if [ -z "$commit_message" ]; then
  commit_message="$work_summary"
fi

# Log to progress file
echo "- $work_summary ($(date))" >> billyb-assistant-progress-report-1.0.txt

# Update project plan timestamp
echo "🔄 Updating project plan timestamp..."
echo "# Last update: $(date)" >> assistant-project-plan.txt

# Git operations
echo "📦 Git add, commit, and push..."
git add .
git commit -m "$commit_message"
git push

# Reminder Tip
echo ""
echo "📚 Tip: If SSH asks for trust (first time), just type 'yes' to accept the server fingerprint!"
echo ""

echo "✅ All done! Synced, tested, and pushed."
