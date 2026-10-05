# The sync job is the published cognee image plus the Obsidian connector.
# Nothing else changes: same cognee, same GLiNER runtime, same user.
# cognee/cognee:main as pulled on 2026-10-05 (cognee 1.6.2), pinned by digest; same as docker-compose.yml api
FROM cognee/cognee@sha256:b9c727a631222897f60de9d796190bbf0a33254afdb335a6638a2419dccc3101

# Commit tarball, not git+https (the image has no git) and not a branch (branches move).
# Point this at the merged connector (upstream tag) when it lands.
ARG CONNECTOR_ARCHIVE=https://github.com/i-ralic/cognee-community/archive/d52a05a4e4c369f3e5dd4334d9a13cc7155f56b6.tar.gz
# The package version (0.1.0) does not change between connector commits, so the image records
# the archive it was built from: as a label and as a file the proof can read back.
# org.opencontainers.image.source is the source of *this* image (this repo); the connector
# archive goes under a custom key.
LABEL org.opencontainers.image.source="https://github.com/cluing-ai/cognee-obsidian-deploy" \
      io.cognee.connector.archive="${CONNECTOR_ARCHIVE}"

USER root
# --no-deps: cognee, dlt and pyyaml are already in the image; the connector
# must not replace a package under the running venv.
RUN /app/.venv/bin/python -m ensurepip --upgrade >/dev/null 2>&1 || true \
 && /app/.venv/bin/python -m pip install --no-cache-dir --no-deps \
      "${CONNECTOR_ARCHIVE}#subdirectory=packages/connector/obsidian" \
 && /app/.venv/bin/python -c "import yaml, dlt, cognee_community_connector_obsidian"
COPY sync.py healthcheck.py link_edges.py visualize.py /app/sync/
RUN echo "${CONNECTOR_ARCHIVE}" > /app/sync/CONNECTOR_ARCHIVE
# /app/.cognee is where cognee writes its persistent id; the image leaves it unwritable for uid 1000,
# which only produces a repeated warning + traceback in the logs (see proof/sync1.log header).
RUN mkdir -p /app/.cognee && chown -R cognee:cognee /app/sync /app/.cognee
USER cognee

ENTRYPOINT ["/app/.venv/bin/python", "/app/sync/sync.py"]
