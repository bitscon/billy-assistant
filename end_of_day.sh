#!/bin/bash

RED=$(tput setaf 1)
GREEN=$(tput setaf 2)
BOLD=$(tput bold)
RESET=$(tput sgr0)

echo "${BOLD}=== 💡 BillyB End-of-Day Checklist ===${RESET}"

# Step 1: Sanity check
echo "${BOLD}🔍 Verifying assistant is online...${RESET}"
curl -s http://localhost:5001/ > /dev/null

if [ $? -ne 0 ]; then
  echo "${RED}❌ Assistant is NOT responding on http://localhost:5001/"
  echo "Please check your container before pushing."
  exit 1
else
  echo "${GREEN}✔️ Assistant is online.${RESET}"
fi

# Step 2: Endpoint curl tests
echo "${BOLD}🔧 Testing critical endpoints...${RESET}"

declare -A tests=(
  ["/ask"]="POST"
  ["/search"]="POST"
  ["/summarize"]="POST"
  ["/admin/status"]="GET"
)

for endpoint in "${!tests[@]}"; do
  if [ "${tests[$endpoint]}" == "POST" ]; then
    curl -s -X POST "http://localhost:5001$endpoint" \
      -H "Content-Type: application/json" \
      -d '{"query":"test"}' > /dev/null
  else
    curl -s "http://localhost:5001$endpoint" > /dev/null
  fi

  if [ $? -eq 0 ]; then
    echo "${GREEN}✔️ $endpoint passed${RESET}"
  else
    echo "${RED}❌ $endpoint failed${RESET}"
  fi
done

# Step 3: Optional daily dev note
echo -n "${BOLD}📝 What did you work on today? (1-liner): ${RESET}"
read WORK_NOTE

echo -n "${BOLD}💬 Commit message (default: same as above): ${RESET}"
read COMMIT_MSG
COMMIT_MSG=${COMMIT_MSG:-$WORK_NOTE}

echo "• Logging to progress report..."
echo "- [$(date '+%Y-%m-%d %H:%M:%S')] $WORK_NOTE" >> billyb-assistant-progress-report-1.0.txt

echo "• Adding timestamp to project plan..."
echo "# Last updated: $(date '+%Y-%m-%d %H:%M:%S')" >> assistant-project-plan.txt

# Step 4: Git add/commit/push
echo "${BOLD}📦 Git add, commit, and push...${RESET}"
git add app/ main.py Dockerfile docker-compose.yml *.txt README.md .gitignore end_of_day.sh
git commit -m "$COMMIT_MSG"
git push

echo "${GREEN}${BOLD}✅ All done! Synced, tested, and pushed.${RESET}"
