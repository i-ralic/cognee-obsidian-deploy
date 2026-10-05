# cognee + Obsidian connector, running without an LLM key, on a real help centre

Runs [cognee](https://github.com/topoteretes/cognee) and the
[Obsidian vault connector](https://github.com/i-ralic/cognee-community/pull/2) in containers with no
LLM API key: the graph is extracted by cognee's local GLiNER model, embeddings come from a local
fastembed model, one Postgres holds all three stores, a second container runs the sync. The vault
is the published content of https://help.cluing.io (repo Collabwriting/help, Astro Starlight),
turned into an Obsidian vault by `scripts/build_vault.py`. Wikilinks become `links_to` edges in the
graph and are counted with SQL, not asserted. Results in [REPORT.md](REPORT.md).

## Three commands

```bash
docker compose up -d            # 1. bring the stack up: postgres + api
docker compose run --rm sync    # 2. run a sync of vault/ (re-run any time; the second run is incremental)
./scripts/ask.sh "How do I share a snippet?"   # 3. ask a question
```

`vault/` is the built vault (297 published pages of help.cluing.io, 577 KB) and is committed, so a
fresh clone syncs without the private source repo. `scripts/build_vault.py` is how it was made;
`vault/vault-manifest.json` records every source → note mapping and the 128 drafts that were
skipped (by path only).

Scheduled syncs: `SYNC_INTERVAL_SECONDS=3600 docker compose --profile sync up -d sync` keeps one
sync container looping; or put `docker compose run --rm sync` in cron.

## The edit / add / delete proof

```bash
docker compose run --rm sync                      # sync 1: 297 emitted, 0 deleted
python3 scripts/mutate_vault.py --vault vault     # one edit, one add, one delete, with marker sentences
docker compose run --rm sync                      # sync 2: the changed notes + re-rendered neighbours, 1 deleted
docker compose run --rm sync                      # sync 3: 0 emitted, 0 deleted
./scripts/search_markers.sh proof/mutation.json   # edit + add markers found; deleted title not found
docker compose run --rm --entrypoint /app/.venv/bin/python sync /app/sync/visualize.py   # graph HTML into the cognee_storage volume
docker compose exec -T postgres psql -U cognee -d cognee_db -v ds=<dataset_id> -f - < scripts/graph_report_dataset.sql
docker compose exec -T postgres psql -U cognee -d cognee_db -v ds=<dataset_id> -f - < scripts/graph_links.sql
```

The `dataset_id` is printed by the sync (`link_edges: {"dataset_id": ...}`). `python3
scripts/mutate_vault.py --vault vault --undo` restores the vault from `proof/mutation.json`.

## Decisions

**The vault is built, not invented.** The help repo has no `.obsidian/` folder and no wikilinks;
its links are site-absolute markdown links. `build_vault.py` copies the published pages (drafts
skipped by `draft: true`; they never leave the private repo), keeps the frontmatter, adds `url`
from `intercom.url` and `tags` from the collection, converts `[text](/en/articles/<slug>/)` to
`[[articles/<slug>|text]]` (path form, which Obsidian resolves from the vault root), converts
Starlight asides to Obsidian callouts, strips MDX, and writes `vault-manifest.json` with every
source → note mapping. The 8 links that point at drafts stay unresolved on purpose: the connector
has to cope with dangling links, and Obsidian shows them the same way.

**Where the sync runs: a second container on the same image, not inside the API.** `remember()`
with a dlt source runs in the process that calls it; it is not an HTTP call. The API process could
do both, but a GLiNER extraction over hundreds of notes is minutes of CPU at ~4.6 GiB (below), and
the published image does not contain the connector. So `sync` is the published cognee image plus
one `pip install --no-deps` of the connector, with its own entrypoint, memory limit and failure
domain. It runs once per `docker compose run --rm sync`, or loops with `SYNC_INTERVAL_SECONDS`.
It always awaits `remember()` in the foreground, because cognee runs forget-on-delete (orphan
cleanup) only for foreground syncs. Both containers see the same data because both talk to the
same Postgres.

**Which databases: one Postgres for all three stores, not the embedded defaults.** cognee's
defaults (SQLite, LanceDB, Ladybug) are file-based, single-process stores; cognee serialises dlt
staging behind a lock *inside one process* and says nothing about two. Two containers writing the
same embedded files is undefined behaviour, so the real choice is "one process" versus "a database
server". Postgres carries relational (`DB_PROVIDER=postgres`), vectors (`VECTOR_DB_PROVIDER=pgvector`)
and the graph (`GRAPH_DATABASE_PROVIDER=postgres_demo`) in one `pgvector/pgvector:pg17` service,
pinned by digest. The dlt destination follows the relational provider, so the connector's cursor
and known-path set land in Postgres (`dlt_database_obsidian_vault`) and survive a recreated sync
container. Cost: `postgres_demo` is a demo backend without Cypher, so `SearchType.CYPHER` is
unavailable and the report reads `graph_node` / `graph_edge` with SQL. Neo4j is the alternative
when Cypher matters more than one less container.

**Model caches: one named volume, mounted in both containers.** `HF_HOME` and
`FASTEMBED_CACHE_PATH` point under `/cognee-storage/models` on the `cognee_storage` volume the
image already owns as uid 1000 (a fresh volume at a custom path would be root-owned). The ~750 MB
GLiNER model and the fastembed model download once, on the first sync; the API reuses the same
fastembed cache for query embeddings.

**Health checks, and what "healthy" means for the sync job.** API: the image's own
`curl -f /health`. Postgres: `pg_isready`; both cognee containers wait for it. Sync: healthy means
*the last sync finished and the cursor advanced*. One-shot mode (`compose run`): exit code 0 and a
`last_success.json` written by `sync.py`; no healthcheck fires, because the container is gone.
Loop mode (`SYNC_INTERVAL_SECONDS>0`, `compose --profile sync up -d sync`): `healthcheck.py` fails
when the last success is older than twice the interval, so a wedged loop shows as `(unhealthy)`
in `docker compose ps` (`proof/loop/`). A failed sync leaves staging and memory exactly as they
were, which is the safe failure.

**`ENABLE_BACKEND_ACCESS_CONTROL=false`, and what it changes.** On, every API call needs a user
token and datasets are isolated per user: the sync and the API would have to authenticate as the
same user for recall to see the synced dataset, and the demo graph backend's per-user isolation is
not something this deployment should lean on. Off, there is one tenant and "both see the same
data" holds by construction. Side effect, visible in the GitLab run on this stack: with access
control off, search does not honour the `datasets` filter (one user, all datasets), so a second
dataset in the same Postgres would show up in `ask.sh` answers. Here there is one dataset
(`obsidian_vault`), so it does not bite; turning it on would add a service user for the sync,
token handling in `ask.sh`, and per-dataset databases.

**Wikilinks become edges in one deterministic step, after `remember()`.** cognee's document path
reads only `id`, `title`, `content` and `url` from a dlt row; the connector's structured `links`
column stays in the dlt staging table. `sync/link_edges.py` maps every note path to its document
node (`Data.system_metadata.external_id` → `Data.id`), reads `links` from
`dlt_database_<dataset>.<dataset>.obsidian_notes`, upserts one `links_to` edge per resolved
(source, target) pair through cognee's graph engine, and removes `links_to` edges that no longer
exist. Edited notes get a fresh document node (the data id includes the content hash), so their
old edges are gone by foreign-key cascade and are rebuilt here; deleted notes lose their edges
the same way. The connector stays a pure dlt source and needs no core change for this.

**Closed GLiNER schema from an ontology file.** `ontology/help.owl` names 10 entity types and 8
relation types for a product help centre (feature, ui element, action, platform, integration,
plan, file format, role, organization, person). Reason and measurements: GitLab README,
"Memory scales with chunks per GLiNER call".

**Resources: measured with `scripts/measure.sh`, then limits set from the measurement.** Sync 1
(297 documents): 896 s wall clock, sync container peak **4,634 MiB / 3.97 cores**; sync 2 (19
documents): 118 s, 4,413 MiB; sync 3 (no change): 7 s, 148 MiB, because GLiNER is never loaded when
nothing needs cognifying (`proof/measure_sync*.csv`, `proof/APPENDIX.md` D). The peak does not
depend on corpus size: it is the ~2.7 GiB GLiNER/torch baseline plus `SYNC_DATA_PER_BATCH ×
SYNC_CHUNKS_PER_BATCH` windows in flight (measured in the GitLab deployment on this stack, at
~250 MiB per window). Limits in `docker-compose.yml`: sync **5 GiB limit / 3 GiB reservation**
(4.6 GiB measured + 8 % headroom; the next knob down is `SYNC_DATA_PER_BATCH=2`, which buys ~1 GiB
for about double the wall clock on this corpus), **4 CPUs** (the host VM has 4; the sync is
embarrassingly parallel across cores and nothing else competes with it during a run), API 1 GiB,
Postgres 1 GiB. `restart: unless-stopped` on postgres and api; the sync is a job and is not
restarted. A GPU would move the sync to seconds; nothing in the compose file assumes one.

## Layout

```
docker-compose.yml         postgres + api + sync (sync is a profile; never starts with `up`); vault mounted read-only; images pinned by digest
vault/                     the built vault: 297 published pages, wikilinks, manifest (what the connector syncs)
sync/Dockerfile            cognee/cognee:main + the connector, nothing else
sync/sync.py               one foreground remember(); batch knobs; link_edges; optional loop; last_success.json
sync/link_edges.py         links column → links_to edges between note documents (idempotent)
sync/healthcheck.py        healthy = last success within 2x the interval
sync/visualize.py          cognee's own HTML graph render of the dataset (bounded; whole graph opt-in)
ontology/help.owl          closed GLiNER schema (10 entity types, 8 relation types)
scripts/build_vault.py     help repo → Obsidian vault (published pages only, wikilinks, callouts, manifest); how vault/ was made
scripts/render_link_graph.py  wikilink graph PNG from the connector's links column (stand-in for an Obsidian screenshot)
scripts/mutate_vault.py    one edit, one add, one delete, each with a searchable marker; --undo
scripts/search_markers.sh  rank of each marker in CHUNKS search; deleted title must be absent
scripts/ask.sh             POST /api/v1/search, CHUNKS, over the synced dataset
scripts/measure.sh         docker stats sampler: peak memory / CPU per container while a sync runs
scripts/graph_report_dataset.sql   node/edge counts scoped to one dataset id
scripts/graph_links.sql    links_to edge counts, most linked documents, isolated documents
proof/                     filtered sync logs, docker stats CSVs, SQL output, API search ranks, mutation.json, screenshots, graph HTML + PNG, APPENDIX.md
REPORT.md                  what ended up in the graph and what did not; the six questions (details in proof/APPENDIX.md)
```
