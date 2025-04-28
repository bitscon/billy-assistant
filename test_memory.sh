#!/bin/bash

echo "🧠 Testing Billy's Memory System..."

# Memories to save
memories=(
  "Billy loves helping Chad with IT consulting."
  "Billy enjoys researching new AI tools."
)

# Save memories
for memory in "${memories[@]}"; do
  echo "💾 Saving memory: $memory"
  curl -s -X POST http://ai:5001/memory/save \
    -H "Content-Type: application/json" \
    -d "{\"text\":\"$memory\"}"
  echo ""
done

# Queries to search
queries=(
  "consulting"
  "AI tools"
)

# Search memories
for query in "${queries[@]}"; do
  echo "🔎 Searching for: $query"
  result=$(curl -s -X POST http://ai:5001/memory/search \
    -H "Content-Type: application/json" \
    -d "{\"query\":\"$query\"}")
  
  echo "🔍 Result: $result"
  echo ""
done

echo "✅ Memory test completed!"
