"""Materialise ``links_to`` edges between note documents from the connector's ``links`` column.

cognee's document path reads only ``id``/``title``/``content``/``url`` from a dlt row; the
structured ``links`` column stays in the dlt staging table. This step closes the loop:

1. map every note path to its TextDocument node: ``Data.system_metadata.external_id`` is the
   note path the connector emitted as ``id``; ``Data.id`` is the document's node id;
2. read ``links`` for every current note from the staging table
   (``dlt_database_<dataset>.<dataset>.obsidian_notes``); keep resolved note links;
3. upsert one ``links_to`` edge per (source document, target document) through cognee's graph
   engine, and delete ``links_to`` edges between this dataset's documents that no longer exist
   (an edited note gets a fresh node, so its old edges are already gone by cascade; a link that
   was removed from an unchanged neighbour is removed here).

Idempotent: a run with no vault change inserts nothing and deletes nothing, and a run that
is interrupted between the delete and the insert leaves a strict subset of the desired edges,
which the next run completes (the two statements are not one transaction: the delete goes
through the relational session, the insert through cognee's graph engine).
Deleting stale edges uses SQL on ``graph_edge``: the postgres_demo adapter has no delete-by-
relationship method, and the graph lives in the same Postgres as the relational store here.
"""

from __future__ import annotations

import json
import os
import re
import time
from typing import Any

from sqlalchemy import select, text
from sqlalchemy.ext.asyncio import create_async_engine

from cognee.infrastructure.databases.graph import get_graph_engine
from cognee.infrastructure.databases.relational import get_relational_config, get_relational_engine
from cognee.modules.data.models import Data, Dataset

RELATION = "links_to"
# The dataset name is interpolated into identifiers (dlt database and schema names); only
# dlt-normalised names are accepted so the SQL below can never be shaped by configuration.
DATASET_NAME_RE = re.compile(r"^[a-z0-9_]+$")


async def _path_to_node(dataset_name: str) -> tuple[str | None, dict[str, str]]:
    engine = get_relational_engine()
    async with engine.get_async_session() as session:
        dataset = (await session.execute(select(Dataset).where(Dataset.name == dataset_name))).scalars().first()
        if dataset is None:
            return None, {}
        rows = (await session.execute(select(Data.id, Data.system_metadata).where(Data.dataset_id == dataset.id))).all()
    mapping = {}
    for data_id, meta in rows:
        if isinstance(meta, dict) and meta.get("external_id"):
            mapping[str(meta["external_id"])] = str(data_id)
    return str(dataset.id), mapping


async def _links_from_staging(dataset_name: str) -> dict[str, list[dict[str, Any]]]:
    cfg = get_relational_config()
    url = (f"postgresql+asyncpg://{cfg.db_username}:{cfg.db_password}@{cfg.db_host}:{cfg.db_port}"
           f"/dlt_database_{dataset_name}")
    engine = create_async_engine(url)
    try:
        async with engine.connect() as conn:
            result = await conn.execute(text(f'SELECT id, links FROM "{dataset_name}".obsidian_notes'))
            rows = result.all()
    finally:
        await engine.dispose()
    out: dict[str, list[dict[str, Any]]] = {}
    for note_id, links in rows:
        parsed = json.loads(links) if isinstance(links, str) else (links or [])
        out[str(note_id)] = [link for link in parsed if link.get("kind") == "note" and link.get("resolved")]
    return out


async def materialise(dataset_name: str) -> dict[str, Any]:
    if not DATASET_NAME_RE.match(dataset_name):
        raise ValueError(f"dataset name must match {DATASET_NAME_RE.pattern}: {dataset_name!r}")
    started = time.time()
    dataset_id, path_to_node = await _path_to_node(dataset_name)
    if not dataset_id:
        return {"error": f"dataset {dataset_name!r} not found"}
    links = await _links_from_staging(dataset_name)

    desired: dict[tuple[str, str], dict[str, Any]] = {}
    unresolved_to_node = 0
    for source_path, note_links in links.items():
        source_node = path_to_node.get(source_path)
        if not source_node:
            continue
        for link in note_links:
            target_node = path_to_node.get(link["resolved"])
            if not target_node or target_node == source_node:
                unresolved_to_node += 1
                continue
            props = desired.setdefault((source_node, target_node), {
                "source": "obsidian_connector", "kind": "wikilink", "count": 0, "embed": False,
                "source_path": source_path, "target_path": link["resolved"]})
            props["count"] += 1
            props["embed"] = props["embed"] or bool(link.get("embed"))

    graph = await get_graph_engine()
    node_ids = list(path_to_node.values())
    rel = get_relational_engine()
    async with rel.get_async_session() as session:
        existing = (await session.execute(
            text("SELECT source_id, target_id FROM graph_edge WHERE relationship_name = :rel "
                 "AND source_id = ANY(:ids) AND target_id = ANY(:ids)"),
            {"rel": RELATION, "ids": node_ids})).all()
        existing_set = {(s, t) for s, t in existing}
        stale = [(s, t) for s, t in existing_set if (s, t) not in desired]
        if stale:
            await session.execute(
                text("DELETE FROM graph_edge WHERE relationship_name = :rel AND source_id = :s AND target_id = :t"),
                [{"rel": RELATION, "s": s, "t": t} for s, t in stale])
            await session.commit()
    new_edges = [(s, t, RELATION, props) for (s, t), props in desired.items() if (s, t) not in existing_set]
    if new_edges:
        await graph.add_edges(new_edges)

    return {
        "dataset_id": dataset_id,
        "documents": len(path_to_node),
        "notes_in_staging": len(links),
        "links_to_desired": len(desired),
        "links_to_inserted": len(new_edges),
        "links_to_removed": len(stale),
        "links_without_document": unresolved_to_node,
        "seconds": round(time.time() - started, 1),
    }


if __name__ == "__main__":  # manual run: python /app/sync/link_edges.py
    import asyncio

    print(json.dumps(asyncio.run(materialise(os.environ.get("COGNEE_DATASET", "obsidian_vault")))))
