#!/bin/bash
# Test Billy's memory system with real embeddings

echo "🧠 Testing Billy's Memory System..."

# Function to POST a memory
save_memory() {
  echo "💾 Saving memory: $1"
  curl -s -X POST http://ai:5001/memory/save \
    -H "Content-Type: application/json" \
    -d "{\"text\":\"$1\"}"
  echo ""
}

# Function to search a memory
search_memory() {
  echo "🔎 Searching for: $1"
  curl -s -X POST http://ai:5001/memory/search \
    -H "Content-Type: application/json" \
    -d "{\"query\":\"$1\"}"
  echo ""
}

# Save memories
save_memory "Billy loves helping Chad with IT consulting."
save_memory "Billy enjoys researching new AI tools."

# Search
search_memory "consulting"
search_memory "AI tools"

echo ""
echo "✅ Memory test completed!"
