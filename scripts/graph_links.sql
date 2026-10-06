-- links_to edges materialised from the connector's links column, scoped to one dataset.
--   docker compose exec -T postgres psql -U cognee -d cognee_db -v ds=<dataset_id> -f - < scripts/graph_links.sql
-- Document nodes are named text_<hash>; the note title comes from the relational data row (same id).
\echo == links_to edges between the documents of this dataset
SELECT count(*) AS links_to_edges, sum((e.properties->>'count')::int) AS wikilinks_represented
FROM graph_edge e JOIN graph_node s ON s.id = e.source_id JOIN graph_node t ON t.id = e.target_id
WHERE e.relationship_name = 'links_to' AND :'ds' = ANY(s.source_dataset_ids) AND :'ds' = ANY(t.source_dataset_ids);
\echo == ten most linked-to documents (inbound links_to)
SELECT d.label AS document, d.system_metadata->>'external_id' AS note, count(*) AS inbound
FROM graph_edge e JOIN graph_node t ON t.id = e.target_id JOIN data d ON d.id::text = t.id
WHERE e.relationship_name = 'links_to' AND :'ds' = ANY(t.source_dataset_ids)
GROUP BY d.label, d.system_metadata->>'external_id' ORDER BY inbound DESC, document LIMIT 10;
\echo == documents with no links_to edge in either direction
SELECT d.label AS document, d.system_metadata->>'external_id' AS note FROM graph_node n JOIN data d ON d.id::text = n.id
WHERE n.type = 'TextDocument' AND :'ds' = ANY(n.source_dataset_ids)
  AND NOT EXISTS (SELECT 1 FROM graph_edge e WHERE e.relationship_name = 'links_to' AND (e.source_id = n.id OR e.target_id = n.id))
ORDER BY 1;
\echo == sample of five links_to edges
SELECT ds.label AS from_document, dt.label AS to_document, e.properties->>'count' AS links
FROM graph_edge e JOIN data ds ON ds.id::text = e.source_id JOIN data dt ON dt.id::text = e.target_id
JOIN graph_node s ON s.id = e.source_id
WHERE e.relationship_name = 'links_to' AND :'ds' = ANY(s.source_dataset_ids) ORDER BY 1, 2 LIMIT 5;
