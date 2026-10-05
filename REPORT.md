# Report: what ended up in the graph, and what did not

**BLUF.** 297 published help-centre notes (a vault built from help.cluing.io, 1,157 wikilinks) went into cognee 1.6.2 with no LLM key. The deterministic part of the graph is the wikilink layer: 1,114 `links_to` edges, counted by SQL. The extracted part (1,702 entities, 444 relations from a closed 10-type / 8-relation schema) names the product's concepts correctly, gets the relation between two co-occurring terms wrong about half the time, and never sees structure, steps, numbers or negations. An edit, an add and a delete re-synced exactly (19 emitted, 1 deleted, third sync a no-op). Corpus, method, three-run table, resources, hours: [proof/APPENDIX.md](proof/APPENDIX.md).

## 1. Node types and edge types, with counts

After sync 3 (`proof/sql_sync3_*.txt`, `sql_sync2_edge_types.txt`).

| Node type | Count | | Edge type | Count |
|---|---|---|---|---|
| Entity | 1,702 | | `contains` (chunk → entity) | 5,342 |
| DocumentChunk | 434 | | `is_a` (entity → type) | 1,921 |
| TextSummary | 434 | | **`links_to` (document → document)** | **1,114** |
| TextDocument | 297 | | `made_from`, `is_part_of` | 434 each |
| EntityType | 10 | | `available_on` 99 · `part_of` 77 · `performed_on` 73 · `exports_to` 65 · `integrates_with` 52 · `requires_role` 51 · `triggered_by` 26 · `hosts` 1 | 444 |

Entities by type: action 646, feature 459, ui element 239, file format 114, integration 107, organization 107, role 95, platform 77, person 55, plan 25. `links_to` connects 294 of 297 documents; the hubs are the collection index pages, led by "Snippets, Comments, Tags" (40 inbound) and "Topics, Buckets, Clusters" (35) (`proof/link_graph_from_connector.png`).

## 2. The ten most connected nodes

By entity-entity relations (`is_a` and structural edges excluded): cluing 39, dashboard 32, topic 23, canvas 21, mobile 21, workspace 20, snippet 19, ai chat 18, youtube 17, topics 16. By all edges: the ten `EntityType` nodes, then *tags* (293), *article* (194), *snippets* (180), *topics* (162), because every note ends with a `Tags:` line and every page was tagged `article` or `collection`. `topic`/`topics` and `snippet`/`snippets` are separate nodes: no entity normalisation in the demo extractor.

## 3. Five correct and five wrong relationships, with the source text

Sentences from the chunk the head entity came from (`proof/sql_relation_sentences.txt`); each contains both ends.

Correct:
1. `thumbs-up performed_on snippet`: "Reactions are a quick thumbs-up way to let snippet creators know you found their work helpful." (Snippet Reactions)
2. `deletion performed_on topic`: "Confirm the deletion, and the topic will be permanently removed from your workspace." (How to delete a Topic?)
3. `share requires_role viewer`: "Share by mentioning someone in a comment (@): when you mention someone in a comment, they receive an email with a link to the snippet and get access to the Topic based on the role you assign (Viewer, Commenter, Editor)." (How can I share my snippet with someone?)
4. `save performed_on reddit`: "Save Reddit Posts and Comments as Snippets." (Capture Content from Social Media on Desktop)
5. `search available_on windows`: "Use Ctrl+K to open Search on Windows or ⌘+K on Mac." (How to Search Through the App?)

Wrong:
1. `canvas integrates_with youtube`: the only sentence with both terms is a `Links to:` line ("Capture YouTube Videos; … AI Canvas"), a list of link targets, not a statement.
2. `cluing part_of microsoft edge`: "To get the Cluing mobile extension on Microsoft Edge, follow these steps." Cluing runs *on* Edge; `part_of` inverts it.
3. `screenshot exports_to token`: "Getting from the first screenshot to a working token took less than twenty minutes." A narrative, no export.
4. `someone triggered_by slack`: "You can mention someone directly on Slack, and they'll get notified there." A pronoun became an entity; nothing triggers it.
5. `team version requires_role hobbyist`: "If you've been using Cluing on a Hobbyist or Professional plan … upgrading to the Team Version is the way to go." An upgrade path read as a requirement.

Pattern: the closed schema makes every relation *name* plausible, so the failure is a right-sounding relation between two terms that merely share a 384-word window; in the 25-row random sample (`sql_sync3_report_data.txt`) 11 hold, 14 do not.

## 4. What the extraction missed that a reader would expect

- **The document tree.** Every note carries a breadcrumb ("In this collection > Snippets, Comments, Tags / Snippets"); GLiNER extracted none of it. The tree is in the graph only through `links_to`.
- **Steps and their order.** Most articles are numbered procedures; 646 `action` entities, no ordering.
- **Numbers.** "Hobbyist (Free): 2 MB, Professional: 30 MB" is in a chunk; no `plan` entity carries a value.
- **Negations.** "You can't add collaborators to your Inbox, but you can mention someone" becomes co-occurrence.
- **People, dates, events, places.** "Cluing was founded in 2021 by Sandra Idjoski" is a chunk, not a graph fact: `help.owl` has no `founded`/`date` relation and no event/location type, which is also why the edit marker's "Zagreb Hackfest 2026" and "Lauba hall" were not extracted. My schema choice, not a model limit.

## 5. Three questions the graph can answer and three it cannot

"Answer" = readable in the top-3 CHUNKS results (`proof/questions_sync3.txt`); no LLM composes one.

Can: **"How do I share a snippet with my team?"** (rank 1: copy the content or share a direct link). **"What are topics, buckets and clusters?"** (rank 1: the collection page whose `Links to:` line names all three). **"Which browsers is the Cluing extension available on?"** (rank 2: "Cluing works on: Chrome Webstore …").

Cannot: **"How many snippets can I create on the free plan?"** (three chunks about creating snippets, none with a limit). **"Where is the Zagreb Hackfest 2026 held?"** (the fact is in one chunk, but the question's embedding lands on AI-chat articles and the graph has no event/location entity; the literal sentence is rank 1). **"Who founded Collabwriting and when?"** (rank 2 has the sentence; the graph has no person → organization → date relation).

## 6. The one change I would make first

**Let a document-source row carry a `links` column that cognee turns into edges itself.** Today `_build_document_data_item` reads `id`, `title`, `content`, `url` and nothing else (`resolve_dlt_sources.py` 609–631); `sync/link_edges.py` exists only because of that. A backwards-compatible `links: [{target_id, relationship}]` on a document-mode row, materialised by `extract_dlt_source_edges` and cleaned up by the same orphan logic, would make every "the source already is a graph" connector (Obsidian, Notion, Confluence, GitLab, wikis) deterministic by default. Cheaper but narrower: `event` and `location` classes in `help.owl` would have caught the edit marker.
