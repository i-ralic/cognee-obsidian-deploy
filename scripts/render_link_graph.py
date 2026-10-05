"""Render the vault's wikilink graph as a PNG from the connector's ``links`` column.

Stand-in for an Obsidian graph-view screenshot when none can be taken: the picture is
drawn from connector output (the dlt staging table), not from Obsidian, and is labelled so.

  docker compose exec -T postgres psql -U cognee -d dlt_database_obsidian_vault -tA -F $'\t' \
    -c "SELECT id, title, links FROM obsidian_vault.obsidian_notes ORDER BY id" > links.tsv
  python scripts/render_link_graph.py links.tsv proof/link_graph_from_connector.png

Needs networkx + matplotlib (not part of the stack; any Python with both will do).
"""

from __future__ import annotations

import json
import sys

import matplotlib
import networkx as nx

matplotlib.use("Agg")
import matplotlib.pyplot as plt  # noqa: E402


def main(tsv: str, out: str) -> None:
    graph = nx.DiGraph()
    titles: dict[str, str] = {}
    for line in open(tsv, encoding="utf-8"):
        if not line.strip():
            continue
        note_id, title, links = line.rstrip("\n").split("\t", 2)
        titles[note_id] = title
        graph.add_node(note_id)
        for link in json.loads(links):
            if link.get("kind") == "note" and link.get("resolved") and link["resolved"] != note_id:
                graph.add_edge(note_id, link["resolved"])
    indeg = dict(graph.in_degree())
    undirected = graph.to_undirected()
    components = sorted(nx.connected_components(undirected), key=len, reverse=True)
    giant = graph.subgraph(components[0])
    rest = [c for c in components[1:]]
    # Force-directed layout of the giant component only; small components and isolated
    # notes are listed in the caption instead of being flung to the corners.
    pos = nx.kamada_kawai_layout(giant.to_undirected())
    fig, ax = plt.subplots(figsize=(18, 14), dpi=110)
    # A handful of long chains stretch the layout; frame the 2nd..98th percentile so the
    # core is readable (nodes outside the frame are still drawn, just off-canvas).
    import numpy as np

    xs = np.array([p[0] for p in pos.values()])
    ys = np.array([p[1] for p in pos.values()])
    ax.set_xlim(np.percentile(xs, 2) - 0.02, np.percentile(xs, 98) + 0.02)
    ax.set_ylim(np.percentile(ys, 2) - 0.02, np.percentile(ys, 98) + 0.02)
    sizes = [30 + 22 * indeg.get(n, 0) for n in giant.nodes]
    colors = ["#c0392b" if n.startswith("collections/") else "#2c6fbb" for n in giant.nodes]
    nx.draw_networkx_edges(giant, pos, ax=ax, alpha=0.10, arrows=False, width=0.6, edge_color="#333")
    nx.draw_networkx_nodes(giant, pos, ax=ax, node_size=sizes, node_color=colors, alpha=0.85, linewidths=0)
    hubs = sorted(giant.nodes, key=lambda n: -indeg.get(n, 0))[:14]
    labels = {n: f"{titles.get(n, n)[:30]} ({indeg.get(n, 0)})" for n in hubs}
    for n, text in labels.items():
        x, y = pos[n]
        ax.annotate(text, (x, y), fontsize=8, ha="center", va="bottom", xytext=(0, 6), textcoords="offset points",
                    bbox={"boxstyle": "round,pad=0.2", "fc": "white", "ec": "none", "alpha": 0.8})
    small = sum(len(c) for c in rest)
    ax.set_title(
        f"Wikilink graph of the vault, rendered from the connector's `links` column (dlt table obsidian_notes): "
        f"{graph.number_of_nodes()} notes, {graph.number_of_edges()} links_to edges.\n"
        f"Shown: the connected component of {len(giant)} notes (Kamada-Kawai layout, framed on the 2nd-98th percentile); "
        f"{small} notes in {len(rest)} smaller components or isolated are not drawn. "
        "Red = collection pages, blue = articles; node size = inbound links; labels = the 14 most linked-to notes (inbound count).\n"
        "Rendered from connector output with networkx, NOT an Obsidian screenshot (see REPORT.md).",
        fontsize=10, loc="left",
    )
    ax.axis("off")
    fig.tight_layout()
    fig.savefig(out)
    print(out, graph.number_of_nodes(), "nodes", graph.number_of_edges(), "edges")


if __name__ == "__main__":
    main(sys.argv[1], sys.argv[2])
