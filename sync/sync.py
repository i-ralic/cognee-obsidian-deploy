"""Run one Obsidian vault → cognee sync in the foreground, optionally on an interval.

Foreground matters: cognee only runs forget-on-delete (orphan cleanup) when
remember() is awaited in the calling process, never for background runs.

After remember(), ``link_edges.materialise`` turns the connector's ``links`` column into
``links_to`` edges between the note documents (SYNC_LINK_EDGES=false to skip).

Exit code 0 = the sync finished and the cursor advanced; non-zero = it failed and
staging/memory were left as they were. ``SYNC_INTERVAL_SECONDS > 0`` loops inside one
event loop (see ``main_async``).
"""

import asyncio
import json
import os
import pathlib
import sys
import time

import cognee
from cognee_community_connector_obsidian import obsidian_source

import link_edges

DATASET = os.environ.get("COGNEE_DATASET", "obsidian_vault")
VAULT = os.environ.get("OBSIDIAN_VAULT_PATH", "/vault")
INTERVAL = int(os.environ.get("SYNC_INTERVAL_SECONDS", "0") or 0)
STATE_DIR = pathlib.Path(os.environ.get("SYNC_STATE_DIR", "/cognee-storage/sync"))
LINK_EDGES = os.environ.get("SYNC_LINK_EDGES", "true").lower() not in ("0", "false", "no")

# Memory, measured in this image (README "Resources"): the process sits at ~2.7 GiB once
# cognee, torch and GLiNER are loaded, and every chunk GLiNER scores in one forward pass adds
# ~250 MiB. cognee hands GLiNER up to ``chunks_per_batch`` chunks per call (default 2000 = every
# chunk of the document). 4 chunks per call keeps the peak under 4 GiB on long notes.
DATA_PER_BATCH = int(os.environ.get("SYNC_DATA_PER_BATCH", "4") or 4)
CHUNKS_PER_BATCH = int(os.environ.get("SYNC_CHUNKS_PER_BATCH", "4") or 4)
CHUNK_SIZE = int(os.environ.get("SYNC_CHUNK_SIZE", "0") or 0) or None  # None = cognee's automatic size

REMEMBER_KWARGS = {
    "primary_key": "id", "write_disposition": "merge", "max_rows_per_table": 0,
    "data_per_batch": DATA_PER_BATCH, "chunks_per_batch": CHUNKS_PER_BATCH, "chunk_size": CHUNK_SIZE,
}


async def run_once() -> None:
    started = time.time()
    result = await cognee.remember(obsidian_source(VAULT), dataset_name=DATASET, **REMEMBER_KWARGS)
    remember_s = time.time() - started
    edges = await link_edges.materialise(DATASET) if LINK_EDGES else {"skipped": True}
    elapsed = time.time() - started
    STATE_DIR.mkdir(parents=True, exist_ok=True)
    record = {"finished_at": time.time(), "elapsed_s": round(elapsed, 1), "remember_s": round(remember_s, 1),
              "dataset": DATASET, "link_edges": edges, "result": str(result)[:2000]}
    (STATE_DIR / "last_success.json").write_text(json.dumps(record))
    print(f"sync ok in {elapsed:.0f}s (remember {remember_s:.0f}s): {result}", flush=True)
    print(f"link_edges: {json.dumps(edges)}", flush=True)


async def main_async() -> int:
    # One event loop for the whole process. cognee binds its database engines and
    # connection pools to the loop that first used them; a fresh asyncio.run() per
    # iteration fails on the second pass with "Event loop is closed" (seen in
    # proof/loop_attempt1/). So the loop lives inside the coroutine and sleeps with
    # asyncio.sleep, and a failed iteration is reported and retried next interval.
    while True:
        try:
            await run_once()
        except Exception as exc:  # noqa: BLE001 - report and keep the loop alive
            print(f"sync FAILED: {exc!r}", file=sys.stderr, flush=True)
            if INTERVAL <= 0:
                return 1
        if INTERVAL <= 0:
            return 0
        await asyncio.sleep(INTERVAL)


def main() -> int:
    return asyncio.run(main_async())


if __name__ == "__main__":
    sys.exit(main())
