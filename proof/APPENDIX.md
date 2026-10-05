# Appendix to REPORT.md: corpus, method, the three-run proof, resources, hours

Everything here is measured on 05.10.2026 on the stack described in the README; every number traces to a file in this directory.

## A. Corpus and method

- **Source:** the published pages of https://help.cluing.io (repo Collabwriting/help, Astro Starlight, commit 1c357e6 of 09.09): **260 articles + 37 collections = 297 notes**, 577 KB, largest 14 KB. 128 drafts (`draft: true`) excluded by `scripts/build_vault.py`; they are listed by path only in `vault-manifest.json` and never left the private repo. The site's internal links (`/en/articles/<slug>/`) became `[[articles/<slug>|text]]` wikilinks: 1,157 links, 1,149 resolve to a published note, 8 point at drafts or missing pages and stay unresolved on purpose.
- **Stack:** cognee 1.6.2 (`cognee/cognee:main` image), GLiNER demo extractor `fastino/gliner2.5-base-v1` with the closed schema `ontology/help.owl`, embeddings `BAAI/bge-small-en-v1.5` via fastembed, one Postgres 17 for relational + pgvector + `postgres_demo` graph, sync as a second container; lima VM 4 CPUs / 8 GB on an Apple M-series host. `SYNC_DATA_PER_BATCH=4`, `SYNC_CHUNKS_PER_BATCH=4`.
- **Connector:** `cognee-community-connector-obsidian` at the commit under review ([PR](https://github.com/i-ralic/cognee-community/pull/2)); `remember(primary_key="id", write_disposition="merge", max_rows_per_table=0)`; `sync/link_edges.py` after each `remember()`.
- **Counting:** `scripts/graph_report_dataset.sql` and `scripts/graph_links.sql` against `graph_node` / `graph_edge`, scoped to the dataset id. **"Answered"** means the fact is readable in the top-5 chunks the CHUNKS search returns; without an LLM there is no generated answer to grade.
- **Logs:** `proof/sync1.log`, `proof/sync2.log`, `proof/sync3.log` (full container output); `proof/measure_sync*.csv` (docker stats every 5 s); `proof/sql_*.txt` (psql output); `proof/mutation.json` (what was edited, added and deleted, with the original texts); `proof/markers_*.txt` (search ranks).

## B. The three-run proof (edit, add, delete)

All three runs on 05.10.2026 between 20:33 and 20:52 UTC, same image, same Postgres, same vault directory (`proof/compose_ps_*.txt` show every container healthy before and after). Dataset id `6ab75593-9b6e-5bf8-b10d-ce14d5d35f55`.

| | Sync 1 (fresh) | `mutate_vault.py` | Sync 2 | Sync 3 |
|---|---|---|---|---|
| Connector log (`proof/sync*.log`) | **297 notes in vault, 297 emitted, 0 deleted** | edit `articles/12606209-ai-chat-in-cluing.md`; add `articles/99999999-quokka-palette.md`; delete `articles/11793611-how-to-mention-collaborators-in-comments.md` | **297 notes in vault, 19 emitted, 1 deleted** | **297 notes in vault, 0 emitted, 0 deleted** |
| cognee orphan cleanup | – | | "Deleting **19** orphaned dlt row(s)" | none |
| `remember()` / wall clock | 892 s / 896 s | | 113 s / 118 s | 4 s / 7 s |
| Sync container peak RSS / CPU (`measure_sync*.csv`) | 4,634 MiB / 397 % | | 4,413 MiB / 392 % | 148 MiB / 91 % (GLiNER never loaded) |
| TextDocument / DocumentChunk / TextSummary / Entity (`sql_sync*_dataset.txt`) | 297 / 433 / 433 / 1,698 | | 297 / 434 / 434 / 1,702 | identical to sync 2 (`diff` clean) |
| Nodes / edges in the dataset | 2,871 / 9,708 | | 2,877 / 9,671 | identical |
| `links_to` edges / wikilinks they represent (`sql_sync*_links.txt`) | **1,134 / 1,149** | | **1,114 / 1,127** | identical; `link_edges` inserted 0, removed 0 |
| Staging rows `obsidian_notes` (`sql_sync*_staging_rows.txt`) | 297 | | 297 (296 + the added one) | 297 |

Why 19 emitted: the deleted note had **19 inbound wikilinks from 17 notes** (`mutation.json`, `sql_sync2_unresolved_after_delete.txt` = 17 staging rows whose `links` now carry `resolved: null` for that path). The connector re-rendered those 17 unchanged neighbours because a name they link to stopped resolving, plus the edited note and the added note = 19. Why 19 orphans: 18 superseded document versions (edit + 17 re-renders; the data id includes the content hash) + the deleted note. Why 1,127 wikilinks: 1,149 − 19 inbound to the deleted note − 4 outbound from it + 1 from the added note.

**What the graph did with each change** (`sql_sync2_markers.txt`, `sql_sync2_marker_edges.txt`, `markers_sync2.txt`, `sql_sync3_deleted_title_mentions.txt`):

- **Delete** ("How to Mention Collaborators in Comments?", 2.5 KB, 4 outbound and 19 inbound links): documents with that title in the dataset after sync 2: **0**; its `links_to` edges are gone (foreign-key cascade when cognee removed the node). CHUNKS search for the title: **not in the top 5**. The title string still occurs in **2 chunks, both owned by other documents** ("How can I share my snippet with someone?" and "Mention & Search"): it is the alias text of their now-dangling wikilinks, which is exactly what Obsidian shows for a broken link.
- **Add** ("Quokka palette for Inkscape 1.5", marker "the Quokka palette ships with Inkscape 1.5 and was drawn by Mira Kovac", linking to the edited note): one new document, one chunk; one new `links_to` edge (added → "AI Chat in Cluing"); entities `quokka palette is_a feature`, `mira kovac is_a person`, correct `quokka palette available_on inkscape 1.5`, and two over-reads, `quokka palette part_of inkscape 1.5` and `quokka palette performed_on inkscape 1.5`. CHUNKS search for the marker sentence: **rank 1**.
- **Edit** ("AI Chat in Cluing", 3.7 KB, marker "the Zagreb Hackfest 2026 is hosted by Collabwriting at the Lauba hall" appended): the connector re-read it (stat changed, hash changed) and cognee replaced the document (new data id, old one among the 19 orphans). The marker is in exactly **1 chunk**; CHUNKS search for the literal sentence: **rank 1**; for "Where is the Zagreb Hackfest 2026 held?": **not in the top 3** (`questions_sync3.txt`). GLiNER with the closed help-centre schema extracted **no** entity for "Zagreb Hackfest 2026" or "Lauba hall" (no event/location type in `help.owl`; `collabwriting is_a organization` exists), so the `hosts` relation the ontology offers was never used for it. Same lesson as the GitLab run: a fact at the end of a long document is retrievable only by its own words.

## C. Loop mode (`SYNC_INTERVAL_SECONDS=120`) on the committed, pinned image

`docker compose build sync` from the committed `sync/Dockerfile` (cognee image by digest, connector at commit `ad4dda4`), then `SYNC_INTERVAL_SECONDS=120 docker compose --profile sync up -d sync`. Files in `proof/loop/`.

| T+ | `docker compose ps` sync | Connector | `remember()` |
|---|---|---|---|
| 150 s | `Up 2 minutes (healthy)` | 297 notes in vault, 0 emitted, 0 deleted | 3 s |
| 280 s | `Up 4 minutes (healthy)` | 0 emitted, 0 deleted | 1 s |
| 400 s | `Up 6 minutes (healthy)` | 0 emitted, 0 deleted | 1 s |

Four iterations ran before the container was stopped (21:50, 21:52, 21:54, 21:56 UTC, `sync_loop.log`); `healthcheck.py` exit code 0 (`healthcheck_rc.txt`); `last_success.json` written by the last iteration; `link_edges` inserted 0, removed 0 each time. These iterations are also the "sync 3 on the committed image" re-run: same counts as `sql_sync3_*.txt`.

**Two things this run found, kept as evidence.**

1. *The first loop attempt failed on its second iteration* (`proof/loop_attempt1/`): `sync.py` called `asyncio.run()` once per iteration, and cognee binds its database engines to the first event loop, so iterations 2 and 3 died with `RuntimeError: Event loop is closed`. `healthcheck.py` correctly returned 1 at T+300 s (last success older than 2 × 120 s); `docker compose ps` still showed `(healthy)` at T+280 s because Docker flips only after three failed probes (interval 60 s). Fix in the committed `sync.py`: one event loop for the process (`main_async`, `asyncio.sleep`). The run above is with the fix.
2. *The connector's new pipeline scope reset its cursor once.* The first sync on the pinned image reported `297 notes in vault, 297 emitted, 0 deleted` and finished in 5 s: the `cognee_pipeline_scope` marker gives the source its own dlt pipeline name, so its state table started empty and every note was re-read; because every data id is derived from the content hash, cognee re-cognified nothing (`sql_after_cold_state_resync_*.txt` are identical to `sql_sync3_*.txt`; no `data` row was updated after 20:50 UTC). Both pipeline states now exist in `dlt_database_obsidian_vault.obsidian_vault._dlt_pipeline_state` (`ingest_dlt_source` v1–v2 and `ingest_dlt_540b9d9f…` v1). Consequence for operators: upgrading the connector across this change costs one full re-read of the vault (seconds), not a re-cognify.

**Re-pin after the last connector fix.** The connector PR gained one more commit (`d52a05a`, emptied known note = edit) after the loop run above, so `sync/Dockerfile` was re-pinned to it and the loop proof repeated from a rebuild: three iterations at 120 s (22:12, 22:14, 22:16 UTC), each `297 notes in vault, 0 emitted, 0 deleted`, `docker compose ps` `(healthy)` at T+150 s and T+280 s, `healthcheck.py` exit 0 (`proof/loop_d52a05a/`). Pin and proof match at the PR head. The image records the connector archive it was built from as the image label `io.cognee.connector.archive` (the OCI `source` label names this repo) and as `/app/sync/CONNECTOR_ARCHIVE` (`proof/loop_d52a05a/connector_commit.txt`, read back from the built image); the package version alone (0.1.0) cannot tell connector commits apart. A one-shot no-op sync on that rebuilt image is in `sync_oneshot_after_label.log`.

## D. Resources

Measured with `scripts/measure.sh` (docker stats every 5 s; `proof/measure_sync*.csv`), lima VM 4 CPUs / 8 GB:

| | Sync 1 (297 documents) | Sync 2 (19 documents) | Sync 3 (0 documents) |
|---|---|---|---|
| Wall clock | 896 s (≈ 3.0 s per document) | 118 s | 7 s |
| Sync container peak RSS / CPU | 4,634 MiB / 397 % | 4,413 MiB / 392 % | 148 MiB / 91 % |
| API (idle) / Postgres peak | 607 MiB / 166 MiB | 608 MiB / 184 MiB | 609 MiB / 146 MiB |

The sync peak is independent of corpus size (sync 2 with 19 documents peaked within 5 % of sync 1 with 297): it is the 2.7 GiB GLiNER/torch baseline plus `SYNC_DATA_PER_BATCH × SYNC_CHUNKS_PER_BATCH` windows in flight, as measured in the GitLab deployment. 4.6 GiB against the 5 GiB limit is tight; on this corpus `SYNC_DATA_PER_BATCH=2` would buy ~1 GiB of headroom for roughly double the wall clock. A no-op sync never loads the model (148 MiB), which is what makes an hourly `SYNC_INTERVAL_SECONDS` loop cheap. `link_edges.py` took 0.1 s for 1,134 edges. The whole-graph HTML render (`sync/visualize.py` with `VISUALIZE_FULL=true`) was OOM-killed at 5 GiB; the bounded render is what `proof/` contains.

Known cosmetic issue: the published image leaves `/app/.cognee` unwritable for uid 1000, so every cognee process logs "Could not create or read persistent id file" with a traceback (188,440 lines in the raw sync 1 log, removed in the committed `proof/sync*.log`, raw logs kept locally). The committed `sync/Dockerfile` now creates that directory; the three proof runs used the image built before that one-line change (only the warning differs).

## E. Hours, cuts, tools

- **Hours:** ≈ 8.5 h total. Research + vault builder 1.5 h; connector + 40 tests 3 h; connector docs 0.5 h; deployment (compose, sync, link edges, mutate, SQL) 1.5 h; the three runs + proof pack 1 h; this report 1 h. About 0.5 h was lost to a full disk on the host mid-run.
- **Cuts (would do with more time):** Obsidian graph-view screenshots (Obsidian 1.14.4 is installed and opens the vault, but macOS refused screen capture to the unattended session; `proof/vault_tree.txt` + `proof/graph_links_to.html` stand in); the whole-graph HTML render (OOM at 5 GiB); `event`/`location` classes in the ontology; a `GRAPH_COMPLETION` grading pass with an LLM key; an Obsidian plugin-free way to read `.obsidian/graph.json` filters.
- **AI tools:** Claude Code (Fable 5.1) as pair programmer for code, SQL and this text. Every command was run on this stack by me; every number above comes from a file under `proof/`.
