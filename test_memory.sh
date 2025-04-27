#!/bin/bash
set -e

echo "🧠 Testing Billy's Memory System (Upgraded)..."

# 1. Save a memory
echo "Saving memory #1..."
curl -s -X POST http://ai:5001/memory/save \
  -H "Content-Type: application/json" \
  -d '{"text":"Billy is an extremely smart assistant who loves to help Chad."}' | jq

# 2. Save another memory
echo "Saving memory #2..."
curl -s -X POST http://ai:5001/memory/save \
  -H "Content-Type: application/json" \
  -d '{"text":"Billy enjoys researching new AI tools and helping with IT consulting."}' | jq

# 3. Search for keyword 'consulting'
echo "Searching for 'consulting'..."
curl -s -X POST http://ai:5001/memory/search \
  -H "Content-Type: application/json" \
  -d '{"query":"consulting"}' | jq

# 4. Search for keyword 'Chad'
echo "Searching for 'Chad'..."
curl -s -X POST http://ai:5001/memory/search \
  -H "Content-Type: application/json" \
  -d '{"query":"Chad"}' | jq

echo "✅ Memory test (upgrade) completed!"
