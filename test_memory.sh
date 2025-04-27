#!/bin/bash

echo "🧠 Testing Billy's Memory System..."

# Save memory
echo "Saving a memory..."
curl -s -X POST http://ai:5001/memory/save \
  -H "Content-Type: application/json" \
  -d '{"text":"Billy is an amazing assistant"}'
echo
sleep 1

# Search memory
echo "Searching for memory..."
curl -s -X POST http://ai:5001/memory/search \
  -H "Content-Type: application/json" \
  -d '{"query":"amazing"}'
echo

echo "✅ Memory test completed!"
