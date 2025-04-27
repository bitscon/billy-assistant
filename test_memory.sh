#!/bin/bash

echo "🧠 Testing Billy's Memory System..."

# 1. Save memories
echo "💾 Saving memory 1..."
curl -s -X POST http://ai:5001/memory/save \
  -H "Content-Type: application/json" \
  -d '{"text":"Billy is Chad'\''s brilliant assistant."}'
echo
sleep 1

echo "💾 Saving memory 2..."
curl -s -X POST http://ai:5001/memory/save \
  -H "Content-Type: application/json" \
  -d '{"text":"Billy loves solving IT problems and building AI tools."}'
echo
sleep 1

# 2. Search memories
echo "🔎 Searching for 'assistant'..."
curl -s -X POST http://ai:5001/memory/search \
  -H "Content-Type: application/json" \
  -d '{"query":"assistant"}'
echo
sleep 1

echo "🔎 Searching for 'AI tools'..."
curl -s -X POST http://ai:5001/memory/search \
  -H "Content-Type: application/json" \
  -d '{"query":"AI tools"}'
echo
sleep 1

echo
echo "✅ Memory test completed!"
