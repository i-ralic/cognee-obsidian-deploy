"""Render the synced dataset's graph to self-contained HTML files with cognee's own visualiser.

Used for the proof pack when Obsidian's graph view cannot be screenshotted on the host.

  docker compose run --rm --entrypoint /app/.venv/bin/python sync /app/sync/visualize.py
  docker compose cp <container>:/cognee-storage/proof/ proof/   # or mount a host dir

Writes under SYNC_PROOF_DIR (default /cognee-storage/proof):
  graph_links_to.html   a bounded neighbourhood (400 nodes) around the vector hits for "snippets comments tags"
  graph_full.html       the whole dataset graph, only with VISUALIZE_FULL=true (needs > 5 GiB here)
"""

import asyncio
import os
import pathlib

import cognee

DATASET = os.environ.get("COGNEE_DATASET", "obsidian_vault")
OUT = pathlib.Path(os.environ.get("SYNC_PROOF_DIR", "/cognee-storage/proof"))


async def main() -> None:
    OUT.mkdir(parents=True, exist_ok=True)
    # cognee.visualize_graph returns the HTML (and writes the file); report the files it wrote.
    written = []
    # The whole-graph render (~2,900 nodes / ~9,700 edges here) needs more than the sync
    # container's 5 GiB and gets OOM-killed; it is opt-in (VISUALIZE_FULL=true, raise SYNC_MEM_LIMIT).
    if os.environ.get("VISUALIZE_FULL", "false").lower() in ("1", "true", "yes"):
        await cognee.visualize_graph(str(OUT / "graph_full.html"), dataset=DATASET, full=True, max_nodes=5000)
        written.append(OUT / "graph_full.html")
    await cognee.visualize_graph(
        str(OUT / "graph_links_to.html"), dataset=DATASET, query="snippets comments tags", max_nodes=400
    )
    written.append(OUT / "graph_links_to.html")
    for path in written:
        print(path, path.stat().st_size, "bytes")


if __name__ == "__main__":
    asyncio.run(main())
