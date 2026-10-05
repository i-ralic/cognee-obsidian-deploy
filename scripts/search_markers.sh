#!/usr/bin/env sh
# Search the API for the three marker facts recorded by mutate_vault.py and print rank per marker.
# Usage: ./scripts/search_markers.sh [proof/mutation.json]
set -eu
REC="${1:-proof/mutation.json}"
python3 - "$REC" <<'PY'
import json, sys, urllib.request
rec = json.load(open(sys.argv[1]))
ds = __import__("os").environ.get("COGNEE_DATASET", "obsidian_vault")
def search(q, k=5):
    body = json.dumps({"searchType": "CHUNKS", "query": q, "datasets": [ds], "topK": k}).encode()
    r = urllib.request.urlopen(urllib.request.Request("http://localhost:8000/api/v1/search", body, {"Content-Type": "application/json"}))
    return json.load(r)
def rank(q, needle):
    hits = search(q)
    for i, h in enumerate(hits, 1):
        if needle.lower() in json.dumps(h).lower():
            return i
    return None
print("edit   marker rank:", rank(rec["edit"]["marker"], rec["edit"]["marker"].split(": ", 1)[1][:40]))
print("add    marker rank:", rank(rec["add"]["marker"], rec["add"]["marker"].split(": ", 1)[1][:40]))
title = rec["delete"]["title"] or rec["delete"]["path"]
print("delete title rank (expect None):", rank(title, title))
PY
