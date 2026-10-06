#!/usr/bin/env sh
# Ask the running API a question over the synced dataset. Without an LLM key cognee
# returns matching text chunks, not a generated answer.
set -eu
Q="${1:?usage: ask.sh \"question\"}"
DATASET="${COGNEE_DATASET:-obsidian_vault}"
curl -sS -X POST "http://localhost:8000/api/v1/search" \
  -H "Content-Type: application/json" \
  -d "{\"searchType\": \"${SEARCH_TYPE:-CHUNKS}\", \"query\": $(printf '%s' "$Q" | python3 -c 'import json,sys; print(json.dumps(sys.stdin.read()))'), \"datasets\": [\"$DATASET\"], \"topK\": ${TOP_K:-5}}"
echo
